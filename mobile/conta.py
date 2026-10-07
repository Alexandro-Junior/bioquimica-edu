"""Quem está usando o app (conta Google ou sem conta) e se já viu o tutorial.

Regras:
- a escolha (Google ou sem conta) fica salva: a tela de acesso só volta
  depois de sair da conta, ou se a sessão do Google deixar de valer;
- sem conta, tudo fica no aparelho, e "tutorial visto" é uma preferência
  local;
- com conta, "tutorial visto" fica no documento do aluno no Firestore e
  vale em qualquer aparelho. Uma cópia local permite abrir sem internet; se
  o envio falhar, fica pendente e é refeito na próxima abertura;
- entrar ou sair de uma conta nunca apaga o progresso de estudo, que
  continua no aparelho.

Sem dependência do Kivy: as telas chamam estes métodos (os que acessam a
rede, numa thread) e os testes os exercitam com um Google simulado.
"""

import sys
import threading
from pathlib import Path

import autenticacao as A

SEM_ESCOLHA, SEM_CONTA, GOOGLE = "", "sem_conta", "google"
ARQUIVO_SESSAO = "sessao_google.dat"


class Acesso:
    def __init__(self, prefs, pasta_sessao, cfg=..., plataforma=sys.platform,
                 obter_token=None, firebase=None):
        self.prefs = prefs
        self.cfg = A.ler_config() if cfg is ... else cfg
        self.plataforma = plataforma
        self.cofre = A.Cofre(Path(pasta_sessao) / ARQUIVO_SESSAO, plataforma=plataforma)
        self.firebase = firebase or (A.Firebase(self.cfg) if self.cfg else None)
        self._obter_token = obter_token
        # trocado nos testes por uma chamada direta
        self.em_segundo_plano = lambda fn: threading.Thread(target=fn, daemon=True).start()
        self.sessao_encerrada = False
        self.sessao, self.estado = None, {}
        dados = self.cofre.carregar()
        if dados:
            self.sessao = A.sessao_do_cofre(dados)
            self.estado = {"tutorial_visto": bool(dados.get("tutorial_visto")),
                           "tutorial_pendente": bool(dados.get("tutorial_pendente"))}

    # ── estado ──────────────────────────────────────────────────────
    @property
    def modo(self):
        return self.prefs["modo_acesso"]

    @property
    def conectado(self):
        return self.modo == GOOGLE and self.sessao is not None

    def google_disponivel(self):
        return self.firebase is not None and A.login_disponivel(self.cfg, self.plataforma)

    def precisa_escolher(self):
        """Mostrar a tela de acesso? Só se nunca escolheu ou se a sessão se perdeu."""
        return self.modo == SEM_ESCOLHA or (self.modo == GOOGLE and self.sessao is None)

    def tutorial_visto(self):
        if self.conectado:
            return bool(self.estado.get("tutorial_visto"))
        return bool(self.prefs["boas_vindas_vista"])

    def precisa_confirmar_na_nuvem(self):
        """Conta conectada que ainda não sabe se viu o tutorial: vale perguntar
        à nuvem antes de decidir (ele pode ter visto em outro aparelho)."""
        return self.conectado and not self.estado.get("tutorial_visto")

    # ── escolhas ────────────────────────────────────────────────────
    def usar_sem_conta(self):
        self.prefs.definir("modo_acesso", SEM_CONTA)

    def entrar_com_google(self, cancelar=None):
        """Login completo. Bloqueia (rode numa thread); lança A.ErroLogin."""
        if not self.google_disponivel():
            raise A.ErroLogin("O login com Google ainda não foi configurado neste app.")
        id_token, nonce_bruto = self._provedor()(cancelar)
        sessao = self.firebase.entrar(id_token, nonce_bruto)
        if cancelar is not None and cancelar.is_set():
            raise A.LoginCancelado("Login cancelado.")   # não grava nada
        try:
            remoto = self.firebase.ler_aluno(sessao)
        except A.ErroLogin as e:
            print(f"[conta] não foi possível ler a conta agora: {e}")
            remoto = {}
        visto_na_conta = bool(remoto.get("tutorial_visto"))
        # quem já fez o tutorial neste aparelho, sem conta, não precisa refazer
        visto = visto_na_conta or bool(self.prefs["boas_vindas_vista"])
        pendente = visto and not visto_na_conta
        if pendente:
            try:
                self.firebase.marcar_tutorial(sessao)
                pendente = False
            except A.ErroLogin as e:
                print(f"[conta] envio do tutorial adiado: {e}")
        self.sessao = sessao
        self.estado = {"tutorial_visto": visto, "tutorial_pendente": pendente}
        self.sessao_encerrada = False
        self._salvar()
        self.prefs.definir("modo_acesso", GOOGLE)
        return sessao

    def marcar_tutorial_visto(self):
        """Grava no aparelho na hora e, com conta, envia à nuvem em segundo plano."""
        self.prefs.definir("boas_vindas_vista", True)
        if not self.conectado:
            return
        self.estado.update(tutorial_visto=True, tutorial_pendente=True)
        self._salvar()
        self.em_segundo_plano(self._enviar_tutorial)

    def sincronizar(self):
        """Confere a sessão e o tutorial com a nuvem. Bloqueia: rode numa thread.

        Sem internet, não faz nada: o app segue com a cópia local."""
        if not self.conectado or self.firebase is None:
            return
        try:
            self.firebase.renovar(self.sessao)
            if self.firebase.ler_aluno(self.sessao).get("tutorial_visto"):
                self.estado["tutorial_visto"] = True
                self.estado["tutorial_pendente"] = False
            if self.estado.get("tutorial_pendente"):
                self.firebase.marcar_tutorial(self.sessao)
                self.estado["tutorial_pendente"] = False
            self._salvar()   # o token de renovação pode ter mudado
        except A.SessaoEncerrada as e:
            print(f"[conta] sessão encerrada: {e}")
            self._esquecer_sessao()
            self.sessao_encerrada = True
        except A.ErroLogin as e:
            print(f"[conta] sincronização adiada: {e}")

    def sair(self):
        """Sai da conta neste aparelho. O progresso de estudo continua aqui."""
        self._esquecer_sessao()
        self.prefs.definir("modo_acesso", SEM_ESCOLHA)

    # ── interno ─────────────────────────────────────────────────────
    def _provedor(self):
        if self._obter_token is not None:
            return self._obter_token
        if self.plataforma == "android":
            from mobile.login_android import LoginAndroid
            return LoginAndroid(self.cfg)
        return A.LoginNoNavegador(self.cfg)

    def _enviar_tutorial(self):
        sessao = self.sessao
        if sessao is None:
            return
        try:
            self.firebase.marcar_tutorial(sessao)
            if self.sessao is sessao:
                self.estado["tutorial_pendente"] = False
                self._salvar()
        except A.ErroLogin as e:
            print(f"[conta] envio do tutorial adiado: {e}")

    def _salvar(self):
        if self.sessao is not None:
            self.cofre.salvar(A.sessao_para_cofre(self.sessao, **self.estado))

    def _esquecer_sessao(self):
        self.cofre.apagar()
        self.sessao, self.estado = None, {}
