"""Login com Google (Firebase Authentication) e o estado do aluno na nuvem.

Nenhuma senha passa pelo app. O caminho é este:

1. O Google confirma quem é o estudante e entrega um token de identidade
   (id_token), assinado por ele:
   - no computador, pelo navegador do sistema, no fluxo recomendado para
     aplicativos instalados (OAuth 2.0 com PKCE e retorno para 127.0.0.1,
     RFC 8252). A senha é digitada no site do Google, nunca no app;
   - no Android, pelo seletor de contas do próprio sistema (Credential
     Manager), em mobile/login_android.py.
2. O Firebase Authentication confere esse token e devolve uma sessão do
   app: um token de acesso, que vale uma hora, e um token de renovação.
3. Com o token de acesso, o app lê e grava apenas o documento do próprio
   estudante no Cloud Firestore (alunos/{uid}). As regras do banco
   (firebase/firestore.rules) recusam qualquer outro acesso.

Só o token de renovação fica guardado, e cifrado: no Windows, com a DPAPI
(apenas a mesma conta do Windows consegue decifrar); no Android, na pasta
do app que fica fora do backup. Sair da conta apaga esse arquivo.

Configuração: config/firebase.json, fora do Git (modelo em
config/firebase.exemplo.json; passo a passo em docs/LOGIN_GOOGLE.md).
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
TEMPO_LIMITE_REDE = 20            # segundos por pedido
TEMPO_LIMITE_NAVEGADOR = 300      # para escolher a conta no navegador

AUTORIZACAO = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_GOOGLE = "https://oauth2.googleapis.com/token"
EMISSORES_GOOGLE = ("https://accounts.google.com", "accounts.google.com")
ENTRAR_FIREBASE = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={chave}"
RENOVAR_FIREBASE = "https://securetoken.googleapis.com/v1/token?key={chave}"
DOCUMENTO_ALUNO = ("https://firestore.googleapis.com/v1/projects/{projeto}/databases/(default)"
                   "/documents/alunos/{uid}")


# ════════════════════════════════════════════════════════════════════
# ERROS, COM MENSAGEM PARA O ESTUDANTE
# ════════════════════════════════════════════════════════════════════
class ErroLogin(Exception):
    """Falha que o estudante precisa saber; a mensagem já vem pronta."""


class LoginCancelado(ErroLogin):
    pass


class SemConexao(ErroLogin):
    pass


class SessaoEncerrada(ErroLogin):
    """A sessão não vale mais (conta desativada, acesso revogado): entrar de novo."""


MENSAGENS_FIREBASE = {
    "OPERATION_NOT_ALLOWED": "O login com Google ainda não foi ativado no Firebase.",
    "INVALID_IDP_RESPONSE": "O Google não confirmou a conta. Tente entrar de novo.",
    "USER_DISABLED": "Esta conta foi desativada no BioquímicaEDU.",
    "TOKEN_EXPIRED": "Sua sessão expirou. Entre de novo.",
    "INVALID_REFRESH_TOKEN": "Sua sessão expirou. Entre de novo.",
    "USER_NOT_FOUND": "Sua sessão expirou. Entre de novo.",
    "API_KEY_INVALID": "A configuração do Firebase deste app está incorreta.",
}
SESSAO_INVALIDA = {"USER_DISABLED", "TOKEN_EXPIRED", "INVALID_REFRESH_TOKEN", "USER_NOT_FOUND"}


# ════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ════════════════════════════════════════════════════════════════════
CAMPOS = ("apiKey", "projectId", "webClientId", "desktopClientId", "desktopClientSecret")


def ler_config(raiz=RAIZ):
    """Lê config/firebase.json; None se faltar, estiver incompleto ou nos testes.

    Nada aqui é senha de usuário. A apiKey identifica o projeto do Firebase
    (quem protege os dados são as regras do banco), e o segredo do cliente
    para computador não é tratado como segredo pelo Google em aplicativos
    instalados. Mesmo assim o arquivo fica fora do Git, para não ser
    copiado e usado por outros projetos.
    """
    if os.environ.get("BIOQ_SEM_NUVEM"):
        return None
    try:
        dados = json.loads((Path(raiz) / "config" / "firebase.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(dados, dict):
        return None
    cfg = {campo: str(dados.get(campo) or "").strip() for campo in CAMPOS}
    if not (cfg["apiKey"] and cfg["projectId"]):
        return None
    for campo in ("webClientId", "desktopClientId"):
        if cfg[campo] and not cfg[campo].endswith(".apps.googleusercontent.com"):
            cfg[campo] = ""
    return cfg


def login_disponivel(cfg, plataforma=sys.platform):
    """O login com Google tem o que precisa nesta plataforma?"""
    if not cfg:
        return False
    if plataforma == "android":
        return bool(cfg["webClientId"])
    return bool(cfg["desktopClientId"] and cfg["desktopClientSecret"])


# ════════════════════════════════════════════════════════════════════
# HTTP
# ════════════════════════════════════════════════════════════════════
def _contexto_ssl():
    import ssl
    try:
        import certifi   # no Android, o Python não enxerga os certificados do sistema
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _abrir(requisicao, tempo_limite):
    """Ponto único de rede (os testes trocam esta função por uma falsa)."""
    return urllib.request.urlopen(requisicao, timeout=tempo_limite, context=_contexto_ssl())


def _pedir(url, *, json_corpo=None, form=None, metodo=None, token=None):
    """Faz o pedido e devolve (status, dicionário da resposta)."""
    cabecalhos = {"Accept": "application/json"}
    dados = None
    if json_corpo is not None:
        dados = json.dumps(json_corpo).encode("utf-8")
        cabecalhos["Content-Type"] = "application/json"
    elif form is not None:
        dados = urllib.parse.urlencode(form).encode("utf-8")
        cabecalhos["Content-Type"] = "application/x-www-form-urlencoded"
    if token:
        cabecalhos["Authorization"] = f"Bearer {token}"
    requisicao = urllib.request.Request(url, data=dados, headers=cabecalhos,
                                        method=metodo or ("POST" if dados else "GET"))
    try:
        with _abrir(requisicao, TEMPO_LIMITE_REDE) as resposta:
            return resposta.status, _json(resposta.read())
    except urllib.error.HTTPError as erro:
        return erro.code, _json(erro.read())
    except (urllib.error.URLError, TimeoutError, OSError) as erro:
        raise SemConexao("Sem conexão com a internet. Tente de novo quando estiver online.") from erro


def _json(bruto):
    try:
        return json.loads(bruto.decode("utf-8")) if bruto else {}
    except (ValueError, UnicodeDecodeError):
        return {}


def _codigo_erro(resposta):
    """'TOKEN_EXPIRED' de {'error': {'message': 'TOKEN_EXPIRED : ...'}}."""
    erro = resposta.get("error") if isinstance(resposta, dict) else None
    if isinstance(erro, dict):
        return str(erro.get("message") or erro.get("status") or "").split(" ")[0]
    return str(erro or "")


# ════════════════════════════════════════════════════════════════════
# TOKEN DE IDENTIDADE DO GOOGLE
# ════════════════════════════════════════════════════════════════════
def _b64url(dados):
    return base64.urlsafe_b64encode(dados).rstrip(b"=").decode("ascii")


def criar_pkce():
    """Par do PKCE (RFC 7636): o verificador fica no app; o desafio vai ao Google."""
    verificador = _b64url(secrets.token_bytes(48))
    return verificador, _b64url(hashlib.sha256(verificador.encode("ascii")).digest())


def criar_nonce():
    """Nonce bruto (vai ao Firebase) e seu SHA-256 (vai ao Google, dentro do token)."""
    bruto = secrets.token_urlsafe(32)
    return bruto, hashlib.sha256(bruto.encode("ascii")).hexdigest()


def conteudo_do_token(token):
    """Lê o conteúdo de um JWT. A assinatura não é conferida aqui: o token
    veio direto do Google por conexão TLS (OpenID Connect, seção 3.1.3.7),
    e o Firebase confere a assinatura de novo antes de abrir a sessão."""
    partes = (token or "").split(".")
    if len(partes) != 3:
        raise ErroLogin("O Google devolveu uma resposta inválida.")
    corpo = partes[1] + "=" * (-len(partes[1]) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(corpo))
    except (ValueError, UnicodeDecodeError) as erro:
        raise ErroLogin("O Google devolveu uma resposta inválida.") from erro


def conferir_token(id_token, client_id, nonce_hash, agora=None):
    """Confere emissor, destinatário, nonce e validade do id_token."""
    dados = conteudo_do_token(id_token)
    agora = time.time() if agora is None else agora
    if dados.get("iss") not in EMISSORES_GOOGLE:
        raise ErroLogin("O token não foi emitido pelo Google.")
    if dados.get("aud") != client_id:
        raise ErroLogin("O token foi emitido para outro aplicativo.")
    if not nonce_hash or dados.get("nonce") != nonce_hash:
        raise ErroLogin("A resposta do Google não corresponde a este pedido de login.")
    if float(dados.get("exp", 0)) < agora - 60:
        raise ErroLogin("A resposta do Google expirou. Tente de novo.")
    return dados


# ════════════════════════════════════════════════════════════════════
# COMPUTADOR: LOGIN PELO NAVEGADOR (OAuth 2.0 + PKCE + 127.0.0.1)
# ════════════════════════════════════════════════════════════════════
PAGINA = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>BioquímicaEDU</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{font-family:system-ui,sans-serif;background:#F6F4EF;color:#17211C;display:grid;
place-items:center;min-height:100vh;margin:0}}main{{max-width:28rem;padding:2rem;text-align:center}}
h1{{font-size:1.4rem}}p{{color:#4A534E;line-height:1.5}}</style></head>
<body><main><h1>{titulo}</h1><p>{texto}</p></main></body></html>"""
PAGINA_OK = PAGINA.format(titulo="Pronto!", texto="Você já pode fechar esta aba e voltar ao "
                          "BioquímicaEDU.")
PAGINA_ERRO = PAGINA.format(titulo="Não foi possível entrar", texto="Volte ao BioquímicaEDU e "
                            "tente de novo.")


class _Retorno(BaseHTTPRequestHandler):
    """Recebe o redirecionamento do Google em http://127.0.0.1:<porta>/."""

    def do_GET(self):
        endereco = urllib.parse.urlparse(self.path)
        if endereco.path != "/":
            self.send_response(404)
            self.end_headers()
            return
        consulta = {k: v[0] for k, v in urllib.parse.parse_qs(endereco.query).items()}
        valido = secrets.compare_digest(consulta.get("state", ""), self.server.estado)
        if valido:   # pedido de outra origem, sem o estado certo, é ignorado
            self.server.resposta = consulta
        corpo = (PAGINA_OK if valido and "code" in consulta else PAGINA_ERRO).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *_):
        pass


class LoginNoNavegador:
    """Abre o navegador na página de login do Google e espera o retorno."""

    def __init__(self, cfg, abrir_navegador=webbrowser.open, tempo_limite=TEMPO_LIMITE_NAVEGADOR):
        self.cfg = cfg
        self.abrir_navegador = abrir_navegador
        self.tempo_limite = tempo_limite

    def __call__(self, cancelar=None):
        """Devolve (id_token, nonce_bruto). Bloqueia: rode fora da interface."""
        cancelar = cancelar or threading.Event()
        verificador, desafio = criar_pkce()
        nonce_bruto, nonce_hash = criar_nonce()
        servidor = HTTPServer(("127.0.0.1", 0), _Retorno)
        servidor.timeout = 0.4
        servidor.estado = secrets.token_urlsafe(32)
        servidor.resposta = None
        retorno = f"http://127.0.0.1:{servidor.server_address[1]}"
        try:
            self.abrir_navegador(AUTORIZACAO + "?" + urllib.parse.urlencode({
                "client_id": self.cfg["desktopClientId"],
                "redirect_uri": retorno,
                "response_type": "code",
                "scope": "openid email profile",
                "code_challenge": desafio,
                "code_challenge_method": "S256",
                "state": servidor.estado,
                "nonce": nonce_hash,
                "prompt": "select_account",
            }))
            limite = time.monotonic() + self.tempo_limite
            while servidor.resposta is None:
                if cancelar.is_set():
                    raise LoginCancelado("Login cancelado.")
                if time.monotonic() > limite:
                    raise ErroLogin("O tempo para entrar acabou. Tente de novo.")
                servidor.handle_request()
            resposta = servidor.resposta
        finally:
            servidor.server_close()

        if "code" not in resposta:
            if resposta.get("error") == "access_denied":
                raise LoginCancelado("Login cancelado no navegador.")
            raise ErroLogin("O Google não autorizou o login. Tente de novo.")
        status, tokens = _pedir(TOKEN_GOOGLE, form={
            "code": resposta["code"],
            "client_id": self.cfg["desktopClientId"],
            "client_secret": self.cfg["desktopClientSecret"],
            "redirect_uri": retorno,
            "grant_type": "authorization_code",
            "code_verifier": verificador,
        })
        if status != 200 or "id_token" not in tokens:
            raise ErroLogin("O Google recusou o login. Tente de novo.")
        conferir_token(tokens["id_token"], self.cfg["desktopClientId"], nonce_hash)
        return tokens["id_token"], nonce_bruto


# ════════════════════════════════════════════════════════════════════
# FIREBASE: SESSÃO E DOCUMENTO DO ALUNO
# ════════════════════════════════════════════════════════════════════
@dataclass
class Sessao:
    uid: str
    email: str
    nome: str
    token_renovacao: str
    token_acesso: str = ""
    expira_em: float = 0.0

    def acesso_valido(self):
        return bool(self.token_acesso) and time.time() < self.expira_em - 60


class Firebase:
    def __init__(self, cfg):
        self.cfg = cfg

    def entrar(self, id_token, nonce_bruto):
        """Troca o id_token do Google por uma sessão do Firebase."""
        status, d = _pedir(ENTRAR_FIREBASE.format(chave=self.cfg["apiKey"]), json_corpo={
            "postBody": urllib.parse.urlencode({"id_token": id_token, "providerId": "google.com",
                                                "nonce": nonce_bruto}),
            "requestUri": "http://localhost",
            "returnSecureToken": True,
            "returnIdpCredential": False,
        })
        if status != 200 or "localId" not in d or "refreshToken" not in d:
            codigo = _codigo_erro(d)
            raise ErroLogin(MENSAGENS_FIREBASE.get(codigo, "Não foi possível entrar agora. "
                                                           "Tente de novo."))
        return Sessao(uid=d["localId"], email=d.get("email", ""),
                      nome=d.get("displayName") or d.get("fullName") or "",
                      token_renovacao=d["refreshToken"], token_acesso=d.get("idToken", ""),
                      expira_em=time.time() + int(d.get("expiresIn", 3600)))

    def renovar(self, sessao):
        """Novo token de acesso a partir do de renovação."""
        status, d = _pedir(RENOVAR_FIREBASE.format(chave=self.cfg["apiKey"]), form={
            "grant_type": "refresh_token", "refresh_token": sessao.token_renovacao})
        if status != 200:
            codigo = _codigo_erro(d)
            if codigo in SESSAO_INVALIDA:
                raise SessaoEncerrada(MENSAGENS_FIREBASE[codigo])
            raise ErroLogin("Não foi possível confirmar a sessão agora.")
        if d.get("user_id") != sessao.uid:
            raise SessaoEncerrada("Sua sessão expirou. Entre de novo.")
        sessao.token_acesso = d["id_token"]
        sessao.token_renovacao = d.get("refresh_token", sessao.token_renovacao)
        sessao.expira_em = time.time() + int(d.get("expires_in", 3600))
        return sessao

    def _url_aluno(self, sessao):
        return DOCUMENTO_ALUNO.format(projeto=self.cfg["projectId"],
                                      uid=urllib.parse.quote(sessao.uid, safe=""))

    def ler_aluno(self, sessao):
        """{'tutorial_visto': bool} do documento alunos/{uid}; vazio se não existir."""
        if not sessao.acesso_valido():
            self.renovar(sessao)
        status, d = _pedir(self._url_aluno(sessao), token=sessao.token_acesso)
        if status == 404:
            return {}
        if status != 200:
            raise ErroLogin("Não foi possível ler os dados da conta.")
        campos = d.get("fields", {})
        return {"tutorial_visto": bool(campos.get("tutorial_visto", {}).get("booleanValue"))}

    def marcar_tutorial(self, sessao):
        """Grava tutorial_visto = true no documento do aluno (cria se não existir)."""
        if not sessao.acesso_valido():
            self.renovar(sessao)
        agora = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        url = (self._url_aluno(sessao) + "?updateMask.fieldPaths=tutorial_visto"
               "&updateMask.fieldPaths=atualizado_em")
        status, _ = _pedir(url, metodo="PATCH", token=sessao.token_acesso, json_corpo={
            "fields": {"tutorial_visto": {"booleanValue": True},
                       "atualizado_em": {"timestampValue": agora}}})
        if status != 200:
            raise ErroLogin("Não foi possível salvar na conta.")


# ════════════════════════════════════════════════════════════════════
# COFRE: ONDE A SESSÃO FICA GUARDADA
# ════════════════════════════════════════════════════════════════════
ENTROPIA = b"BioquimicaEDU/sessao/v1"
MARCA_DPAPI = b"DPAPI1\n"


def _dpapi(dados, cifrar):
    """CryptProtectData/CryptUnprotectData do Windows, via ctypes (sem pywin32)."""
    import ctypes
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    def blob(conteudo):
        buffer = ctypes.create_string_buffer(conteudo, len(conteudo))
        return Blob(len(conteudo), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char))), buffer

    entrada, _b1 = blob(dados)
    entropia, _b2 = blob(ENTROPIA)
    saida = Blob()
    sem_janelas = 0x01   # CRYPTPROTECT_UI_FORBIDDEN
    crypt32 = ctypes.windll.crypt32
    if cifrar:
        ok = crypt32.CryptProtectData(ctypes.byref(entrada), "BioquimicaEDU", ctypes.byref(entropia),
                                      None, None, sem_janelas, ctypes.byref(saida))
    else:
        ok = crypt32.CryptUnprotectData(ctypes.byref(entrada), None, ctypes.byref(entropia),
                                        None, None, sem_janelas, ctypes.byref(saida))
    if not ok:
        raise OSError(f"DPAPI falhou (erro {ctypes.GetLastError()})")
    try:
        return ctypes.string_at(saida.pbData, saida.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(saida.pbData)


class Cofre:
    """Arquivo da sessão: cifrado no Windows; nos outros sistemas, só o dono lê."""

    def __init__(self, caminho, plataforma=sys.platform):
        self.caminho = Path(caminho)
        self.windows = plataforma == "win32"

    def salvar(self, dados):
        bruto = json.dumps(dados).encode("utf-8")
        if self.windows:
            bruto = MARCA_DPAPI + _dpapi(bruto, cifrar=True)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        temporario = self.caminho.with_suffix(".tmp")
        with open(temporario, "wb") as f:
            f.write(bruto)
        if not self.windows:
            os.chmod(temporario, 0o600)
        temporario.replace(self.caminho)

    def carregar(self):
        try:
            bruto = self.caminho.read_bytes()
            if bruto.startswith(MARCA_DPAPI):
                if not self.windows:
                    return None
                bruto = _dpapi(bruto[len(MARCA_DPAPI):], cifrar=False)
            elif self.windows:
                return None   # num Windows, só aceita o arquivo cifrado
            dados = json.loads(bruto.decode("utf-8"))
            return dados if isinstance(dados, dict) else None
        except FileNotFoundError:
            return None
        except (OSError, ValueError, UnicodeDecodeError) as e:
            print(f"[conta] sessão ilegível ({type(e).__name__}); será preciso entrar de novo")
            return None

    def apagar(self):
        try:
            self.caminho.unlink()
        except FileNotFoundError:
            pass


def sessao_para_cofre(sessao, **extras):
    """Só o necessário: o token de acesso, de curta duração, fica na memória."""
    dados = asdict(sessao)
    dados.pop("token_acesso")
    dados.pop("expira_em")
    return {**dados, **extras}


def sessao_do_cofre(dados):
    try:
        return Sessao(uid=str(dados["uid"]), email=str(dados.get("email", "")),
                      nome=str(dados.get("nome", "")), token_renovacao=str(dados["token_renovacao"]))
    except (KeyError, TypeError):
        return None
