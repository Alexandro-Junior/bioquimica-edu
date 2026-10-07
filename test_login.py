"""Testes do login com Google, da sessão guardada e do controle do tutorial.

O Google e o Firebase são simulados, sem rede e sem conta de verdade; o
retorno do navegador para 127.0.0.1 é exercitado de verdade, com um
navegador falso que faz o pedido HTTP. Tudo grava em pastas temporárias.

    python test_login.py
"""

import base64
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

os.environ.pop("BIOQ_SEM_NUVEM", None)   # só neste processo

import autenticacao as A  # noqa: E402
from mobile.conta import GOOGLE, SEM_CONTA, Acesso  # noqa: E402
from mobile.preferencias import Preferencias  # noqa: E402

CFG = {"apiKey": "chave-teste", "projectId": "projeto-teste",
       "webClientId": "web.apps.googleusercontent.com",
       "desktopClientId": "desktop.apps.googleusercontent.com",
       "desktopClientSecret": "segredo-teste"}

TESTES = []
PASTAS = []


def teste(fn):
    TESTES.append(fn)
    return fn


def pasta():
    p = Path(tempfile.mkdtemp(prefix="bioq_login_"))
    PASTAS.append(p)
    return p


def jwt(**dados):
    def parte(d):
        return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()
    return f"{parte({'alg': 'RS256'})}.{parte(dados)}.assinatura"


def token_google(aud, nonce_hash, sub="uid-1", **extra):
    return jwt(iss="https://accounts.google.com", aud=aud, sub=sub, nonce=nonce_hash,
               exp=time.time() + 3600, email="aluno@exemplo.com", **extra)


class Resposta(io.BytesIO):
    def __init__(self, dados, status=200):
        super().__init__(json.dumps(dados).encode())
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


def rede(respostas):
    """Troca a rede do módulo: `respostas(requisicao)` devolve (status, dados)."""
    feitas = []

    def abrir(req, _tempo):
        feitas.append(req)
        status, dados = respostas(req)
        if status >= 400:
            import urllib.error
            raise urllib.error.HTTPError(req.full_url, status, "erro", {},
                                         io.BytesIO(json.dumps(dados).encode()))
        return Resposta(dados, status)

    A._abrir = abrir
    return feitas


# ════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO E TOKENS
# ════════════════════════════════════════════════════════════════════
@teste
def configuracao_fica_fora_do_codigo_e_e_validada():
    raiz = pasta()
    assert A.ler_config(raiz) is None, "sem arquivo, sem login"
    (raiz / "config").mkdir()
    arquivo = raiz / "config" / "firebase.json"
    arquivo.write_text(json.dumps({"apiKey": "x"}), encoding="utf-8")
    assert A.ler_config(raiz) is None, "incompleto não vale"
    arquivo.write_text(json.dumps({**CFG, "desktopClientId": "outro-formato"}), encoding="utf-8")
    cfg = A.ler_config(raiz)
    assert cfg and cfg["desktopClientId"] == "", "id de cliente fora do formato é descartado"
    assert not A.login_disponivel(cfg, "win32") and A.login_disponivel(cfg, "android")
    arquivo.write_text(json.dumps(CFG), encoding="utf-8")
    assert A.login_disponivel(A.ler_config(raiz), "win32")
    os.environ["BIOQ_SEM_NUVEM"] = "1"
    try:
        assert A.ler_config(raiz) is None, "BIOQ_SEM_NUVEM desliga"
    finally:
        del os.environ["BIOQ_SEM_NUVEM"]


@teste
def pkce_e_nonce_seguem_as_especificacoes():
    verificador, desafio = A.criar_pkce()
    assert 43 <= len(verificador) <= 128
    esperado = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).rstrip(b"=")
    assert desafio == esperado.decode()
    bruto, resumo = A.criar_nonce()
    assert resumo == hashlib.sha256(bruto.encode()).hexdigest()
    assert A.criar_pkce()[0] != verificador, "cada login usa um par novo"


@teste
def token_do_google_e_conferido():
    _, nonce_hash = A.criar_nonce()
    bom = token_google(CFG["desktopClientId"], nonce_hash)
    A.conferir_token(bom, CFG["desktopClientId"], nonce_hash)
    casos = {
        "outro app": token_google("outro.apps.googleusercontent.com", nonce_hash),
        "outro pedido": token_google(CFG["desktopClientId"], "nonce-errado"),
        "vencido": jwt(iss="https://accounts.google.com", aud=CFG["desktopClientId"],
                       nonce=nonce_hash, exp=time.time() - 600),
        "outro emissor": jwt(iss="https://falso.com", aud=CFG["desktopClientId"],
                             nonce=nonce_hash, exp=time.time() + 600),
        "lixo": "nao-e-um-token",
    }
    for nome, token in casos.items():
        try:
            A.conferir_token(token, CFG["desktopClientId"], nonce_hash)
        except A.ErroLogin:
            continue
        raise AssertionError(f"token aceito por engano: {nome}")


# ════════════════════════════════════════════════════════════════════
# COMPUTADOR: NAVEGADOR + 127.0.0.1
# ════════════════════════════════════════════════════════════════════
def navegador_falso(estado_errado_antes=True, erro=None):
    """Lê a URL que o app abriria e responde como o Google responderia."""
    visto = {}

    def abrir(url):
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
        visto.update(q)

        def responder():
            time.sleep(0.2)
            if estado_errado_antes:   # alguém tentando enganar o app: ignorado
                urllib.request.urlopen(f"{q['redirect_uri']}/?code=ATAQUE&state=errado").read()
            if erro:
                urllib.request.urlopen(f"{q['redirect_uri']}/?error={erro}&state={q['state']}").read()
            else:
                urllib.request.urlopen(f"{q['redirect_uri']}/?code=CODIGO-OK&state={q['state']}").read()
        threading.Thread(target=responder, daemon=True).start()
    return abrir, visto


@teste
def login_no_navegador_usa_pkce_estado_e_nonce():
    abrir, visto = navegador_falso()

    def respostas(req):
        form = dict(urllib.parse.parse_qsl(req.data.decode()))
        assert req.full_url == A.TOKEN_GOOGLE
        assert form["code"] == "CODIGO-OK", "o código do atacante não pode ser usado"
        desafio = base64.urlsafe_b64encode(
            hashlib.sha256(form["code_verifier"].encode()).digest()).rstrip(b"=").decode()
        assert desafio == visto["code_challenge"], "o verificador PKCE não confere"
        assert form["redirect_uri"] == visto["redirect_uri"]
        assert form["client_secret"] == CFG["desktopClientSecret"]
        return 200, {"id_token": token_google(CFG["desktopClientId"], visto["nonce"])}

    rede(respostas)
    id_token, nonce_bruto = A.LoginNoNavegador(CFG, abrir_navegador=abrir)()
    assert visto["redirect_uri"].startswith("http://127.0.0.1:"), "retorno só na própria máquina"
    assert visto["code_challenge_method"] == "S256" and visto["scope"] == "openid email profile"
    assert hashlib.sha256(nonce_bruto.encode()).hexdigest() == visto["nonce"]
    assert A.conteudo_do_token(id_token)["aud"] == CFG["desktopClientId"]


@teste
def recusar_no_navegador_cancela_o_login():
    abrir, _ = navegador_falso(estado_errado_antes=False, erro="access_denied")
    rede(lambda req: (500, {}))
    try:
        A.LoginNoNavegador(CFG, abrir_navegador=abrir)()
    except A.LoginCancelado:
        return
    raise AssertionError("deveria ter sido cancelado")


@teste
def cancelar_no_app_interrompe_a_espera():
    cancelar = threading.Event()
    threading.Timer(0.5, cancelar.set).start()
    inicio = time.monotonic()
    try:
        A.LoginNoNavegador(CFG, abrir_navegador=lambda url: None)(cancelar)
    except A.LoginCancelado:
        assert time.monotonic() - inicio < 3, "o cancelamento demorou"
        return
    raise AssertionError("deveria ter sido cancelado")


# ════════════════════════════════════════════════════════════════════
# FIREBASE (REST)
# ════════════════════════════════════════════════════════════════════
@teste
def firebase_recebe_o_token_e_devolve_a_sessao():
    def respostas(req):
        corpo = json.loads(req.data)
        post = dict(urllib.parse.parse_qsl(corpo["postBody"]))
        assert "key=chave-teste" in req.full_url
        assert post["providerId"] == "google.com" and post["id_token"] == "TOKEN"
        assert post["nonce"] == "NONCE-BRUTO", "o Firebase precisa do nonce bruto"
        return 200, {"localId": "uid-1", "email": "a@b.com", "displayName": "Ana Souza",
                     "idToken": "acesso", "refreshToken": "renova", "expiresIn": "3600"}
    rede(respostas)
    s = A.Firebase(CFG).entrar("TOKEN", "NONCE-BRUTO")
    assert (s.uid, s.nome, s.token_renovacao) == ("uid-1", "Ana Souza", "renova")
    assert s.acesso_valido()

    rede(lambda req: (400, {"error": {"message": "OPERATION_NOT_ALLOWED"}}))
    try:
        A.Firebase(CFG).entrar("TOKEN", "N")
    except A.ErroLogin as e:
        assert "não foi ativado" in str(e), e
    else:
        raise AssertionError("deveria falhar")


@teste
def sessao_revogada_e_detectada_na_renovacao():
    s = A.Sessao("uid-1", "a@b.com", "Ana", "renova")
    rede(lambda req: (400, {"error": {"message": "TOKEN_EXPIRED"}}))
    try:
        A.Firebase(CFG).renovar(s)
    except A.SessaoEncerrada:
        pass
    else:
        raise AssertionError("TOKEN_EXPIRED deveria encerrar a sessão")
    rede(lambda req: (200, {"id_token": "novo", "refresh_token": "r2", "expires_in": "3600",
                            "user_id": "outra-pessoa"}))
    try:
        A.Firebase(CFG).renovar(s)
    except A.SessaoEncerrada:
        pass
    else:
        raise AssertionError("token de outra pessoa não pode ser aceito")
    rede(lambda req: (200, {"id_token": "novo", "refresh_token": "r2", "expires_in": "3600",
                            "user_id": "uid-1"}))
    A.Firebase(CFG).renovar(s)
    assert (s.token_acesso, s.token_renovacao) == ("novo", "r2") and s.acesso_valido()


@teste
def documento_do_aluno_so_com_o_token_dele():
    s = A.Sessao("uid-1", "a@b.com", "Ana", "renova", token_acesso="acesso",
                 expira_em=time.time() + 3600)
    feitas = rede(lambda req: (404, {}))
    assert A.Firebase(CFG).ler_aluno(s) == {}, "aluno novo: documento ainda não existe"
    assert feitas[0].get_header("Authorization") == "Bearer acesso"
    assert feitas[0].full_url.endswith("/projects/projeto-teste/databases/(default)/documents/alunos/uid-1")
    rede(lambda req: (200, {"fields": {"tutorial_visto": {"booleanValue": True}}}))
    assert A.Firebase(CFG).ler_aluno(s) == {"tutorial_visto": True}

    feitas = rede(lambda req: (200, {}))
    A.Firebase(CFG).marcar_tutorial(s)
    req = feitas[0]
    assert req.get_method() == "PATCH"
    assert "updateMask.fieldPaths=tutorial_visto" in req.full_url, "só os campos do app"
    campos = json.loads(req.data)["fields"]
    assert set(campos) == {"tutorial_visto", "atualizado_em"} and campos["tutorial_visto"]["booleanValue"]


# ════════════════════════════════════════════════════════════════════
# COFRE
# ════════════════════════════════════════════════════════════════════
@teste
def sessao_guardada_cifrada_no_windows():
    if sys.platform != "win32":
        print("    (pulado: DPAPI só existe no Windows)")
        return
    arquivo = pasta() / "sessao_google.dat"
    cofre = A.Cofre(arquivo)
    cofre.salvar({"uid": "uid-1", "token_renovacao": "SEGREDO-123"})
    bruto = arquivo.read_bytes()
    assert bruto.startswith(A.MARCA_DPAPI) and b"SEGREDO-123" not in bruto, "token em texto puro"
    assert cofre.carregar()["token_renovacao"] == "SEGREDO-123"
    arquivo.write_text(json.dumps({"uid": "x", "token_renovacao": "y"}), encoding="utf-8")
    assert cofre.carregar() is None, "no Windows, arquivo não cifrado é recusado"
    arquivo.write_bytes(A.MARCA_DPAPI + b"lixo")
    assert cofre.carregar() is None, "arquivo corrompido não derruba o app"
    cofre.apagar()
    assert not arquivo.exists()


# ════════════════════════════════════════════════════════════════════
# ACESSO: SEM CONTA, GOOGLE, TUTORIAL ENTRE APARELHOS
# ════════════════════════════════════════════════════════════════════
class NuvemFalsa:
    """Faz o papel do Firebase: guarda o documento de cada aluno."""

    def __init__(self):
        self.alunos = {}
        self.fora_do_ar = False
        self.encerrar = False

    def entrar(self, id_token, nonce):
        uid = A.conteudo_do_token(id_token)["sub"]
        return A.Sessao(uid, f"{uid}@exemplo.com", "Ana Souza", f"renova-{uid}",
                        token_acesso="acesso", expira_em=time.time() + 3600)

    def _rede(self):
        if self.fora_do_ar:
            raise A.SemConexao("sem internet")

    def renovar(self, sessao):
        self._rede()
        if self.encerrar:
            raise A.SessaoEncerrada("expirou")
        return sessao

    def ler_aluno(self, sessao):
        self._rede()
        return dict(self.alunos.get(sessao.uid, {}))

    def marcar_tutorial(self, sessao):
        self._rede()
        self.alunos.setdefault(sessao.uid, {})["tutorial_visto"] = True


def aparelho(nuvem, uid="uid-1"):
    """Um aparelho novo: pasta própria, mesma nuvem."""
    base = pasta()
    prefs = Preferencias(base / "preferencias_mobile.json")

    def google(_cancelar=None):
        bruto, resumo = A.criar_nonce()
        return token_google(CFG["webClientId"], resumo, sub=uid), bruto

    acesso = Acesso(prefs, base, cfg=CFG, plataforma=sys.platform, obter_token=google,
                    firebase=nuvem)
    acesso.em_segundo_plano = lambda fn: fn()
    return acesso, base


def reabrir(acesso, base, nuvem):
    """Fecha e abre o app no mesmo aparelho."""
    novo = Acesso(Preferencias(base / "preferencias_mobile.json"), base, cfg=CFG,
                  plataforma=sys.platform, obter_token=acesso._obter_token, firebase=nuvem)
    novo.em_segundo_plano = lambda fn: fn()
    return novo


@teste
def sem_conta_escolha_e_tutorial_ficam_no_aparelho():
    nuvem = NuvemFalsa()
    acesso, base = aparelho(nuvem)
    assert acesso.precisa_escolher() and not acesso.tutorial_visto()
    acesso.usar_sem_conta()
    acesso.marcar_tutorial_visto()
    assert nuvem.alunos == {}, "sem conta, nada vai para a nuvem"
    depois = reabrir(acesso, base, nuvem)
    assert depois.modo == SEM_CONTA and not depois.precisa_escolher(), "a escolha foi esquecida"
    assert depois.tutorial_visto(), "o tutorial apareceria de novo"


@teste
def com_conta_o_tutorial_vale_em_outro_aparelho():
    nuvem = NuvemFalsa()
    celular, base = aparelho(nuvem)
    celular.entrar_com_google()
    assert celular.modo == GOOGLE and celular.conectado and not celular.tutorial_visto()
    celular.marcar_tutorial_visto()
    assert nuvem.alunos["uid-1"]["tutorial_visto"], "o tutorial não chegou à conta"

    reaberto = reabrir(celular, base, nuvem)
    assert reaberto.conectado and not reaberto.precisa_escolher(), "a sessão não persistiu"
    assert reaberto.tutorial_visto()

    computador, _ = aparelho(nuvem)
    assert computador.precisa_escolher(), "aparelho novo pergunta como entrar"
    computador.entrar_com_google()
    assert computador.tutorial_visto(), "no outro aparelho, o tutorial não deveria aparecer"

    outra_pessoa, _ = aparelho(nuvem, uid="uid-2")
    outra_pessoa.entrar_com_google()
    assert not outra_pessoa.tutorial_visto(), "o tutorial é de cada conta"


@teste
def quem_viu_sem_conta_nao_ve_de_novo_ao_entrar():
    nuvem = NuvemFalsa()
    acesso, _ = aparelho(nuvem)
    acesso.usar_sem_conta()
    acesso.marcar_tutorial_visto()
    acesso.entrar_com_google()
    assert acesso.tutorial_visto() and nuvem.alunos["uid-1"]["tutorial_visto"]


@teste
def sem_internet_o_tutorial_fica_pendente_e_e_enviado_depois():
    nuvem = NuvemFalsa()
    acesso, base = aparelho(nuvem)
    acesso.entrar_com_google()
    nuvem.fora_do_ar = True
    acesso.marcar_tutorial_visto()
    assert acesso.tutorial_visto() and acesso.estado["tutorial_pendente"]
    reaberto = reabrir(acesso, base, nuvem)
    reaberto.sincronizar()   # ainda sem internet: segue com a cópia local
    assert reaberto.conectado and reaberto.tutorial_visto()
    nuvem.fora_do_ar = False
    reaberto.sincronizar()
    assert nuvem.alunos["uid-1"]["tutorial_visto"] and not reaberto.estado["tutorial_pendente"]


@teste
def sessao_encerrada_volta_para_a_tela_de_acesso():
    nuvem = NuvemFalsa()
    acesso, base = aparelho(nuvem)
    acesso.entrar_com_google()
    nuvem.encerrar = True
    acesso.sincronizar()
    assert acesso.sessao_encerrada and not acesso.conectado
    assert reabrir(acesso, base, nuvem).precisa_escolher()


@teste
def sair_da_conta_nao_apaga_o_progresso():
    nuvem = NuvemFalsa()
    acesso, base = aparelho(nuvem)
    progresso = base / "progresso.json"
    progresso.write_text('{"itens": {"K": {"acertos": 3}}}', encoding="utf-8")
    acesso.entrar_com_google()
    acesso.sair()
    assert not (base / "sessao_google.dat").exists(), "a sessão ficou no aparelho"
    assert acesso.precisa_escolher() and acesso.modo == ""
    assert progresso.read_text(encoding="utf-8") == '{"itens": {"K": {"acertos": 3}}}'


@teste
def cancelar_depois_da_resposta_nao_grava_nada():
    nuvem = NuvemFalsa()
    acesso, base = aparelho(nuvem)
    cancelar = threading.Event()
    google = acesso._obter_token

    def google_e_cancela(c=None):
        resultado = google(c)
        cancelar.set()   # o estudante cancelou enquanto o Google respondia
        return resultado
    acesso._obter_token = google_e_cancela
    try:
        acesso.entrar_com_google(cancelar)
    except A.LoginCancelado:
        pass
    else:
        raise AssertionError("deveria ter cancelado")
    assert not acesso.conectado and acesso.modo == ""
    assert not (base / "sessao_google.dat").exists()


@teste
def sem_configuracao_o_google_avisa_e_sem_conta_funciona():
    base = pasta()
    acesso = Acesso(Preferencias(base / "p.json"), base, cfg=None)
    assert not acesso.google_disponivel()
    try:
        acesso.entrar_com_google()
    except A.ErroLogin as e:
        assert "não foi configurado" in str(e)
    else:
        raise AssertionError("deveria avisar")
    acesso.usar_sem_conta()
    assert not acesso.precisa_escolher()


if __name__ == "__main__":
    original = A._abrir
    falhas = 0
    for fn in TESTES:
        try:
            fn()
            print(f"  ✓ {fn.__name__.replace('_', ' ')}")
        except Exception as e:
            falhas += 1
            import traceback
            traceback.print_exc()
            print(f"  ✗ {fn.__name__.replace('_', ' ')}: {type(e).__name__}: {e}")
        finally:
            A._abrir = original
    for p in PASTAS:
        shutil.rmtree(p, ignore_errors=True)
    print(f"\n{len(TESTES) - falhas}/{len(TESTES)} testes do login passaram")
    sys.exit(1 if falhas else 0)
