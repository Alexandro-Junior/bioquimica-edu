"""Tela de acesso: entrar com o Google ou usar sem conta.

Aparece depois da abertura enquanto o estudante não escolheu, e de novo só
se ele sair da conta. O login roda numa thread (no computador, espera o
navegador; no Android, o seletor de contas), com um "Cancelar" sempre à
mão. Nenhuma senha passa pelo app: quem pede a senha é o próprio Google.
"""

import threading
from pathlib import Path

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import platform

import autenticacao as A
from mobile import componentes as C
from mobile.tema import COR, dpt
from mobile.telas.base import TelaBase

ASSETS = Path(__file__).resolve().parents[2] / "assets"
SIMBOLO = ASSETS / "logo" / "simbolo.png"
LOGO_GOOGLE = ASSETS / "google_g.png"   # gerado de google_g.svg, o "G" oficial


class BotaoGoogle(ButtonBehavior, C.Superficie):
    """Botão no padrão de identidade do Google: fundo branco, borda cinza,
    o "G" colorido e o texto escuro, nos dois temas do app."""

    def __init__(self, texto="Entrar com o Google", **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", max(dp(52), dpt(46)))
        super().__init__(cor_fundo=(1, 1, 1, 1), raio=dp(14), padding=(dp(14), 0),
                         spacing=dp(12), **kwargs)
        self.cor_borda = (0.455, 0.467, 0.459, 1)   # #747775, a borda do guia do Google
        self.add_widget(Widget())
        self.add_widget(Image(source=str(LOGO_GOOGLE), size_hint=(None, None),
                              size=(dp(20), dp(20)), pos_hint={"center_y": 0.5},
                              fit_mode="contain"))
        self.rotulo = Label(text=texto, color=(0.122, 0.122, 0.122, 1), bold=True,
                            font_size="15sp", size_hint_x=None)
        self.rotulo.disabled_color = self.rotulo.color
        self.rotulo.bind(texture_size=lambda r, *_: setattr(r, "width", r.texture_size[0]))
        self.add_widget(self.rotulo)
        self.add_widget(Widget())
        self.bind(disabled=lambda *_: setattr(self, "opacity", 0.5 if self.disabled else 1))

    def on_state(self, _instancia, estado):
        C._afundar(self, estado, 0.965, volta=0.18)


class TelaAcesso(TelaBase):

    LARGURA_MAXIMA = 480   # dp, em tablet e computador

    def montar(self, erro=None, **_):
        self.cancelar = None
        scroll, col = C.coluna_rolavel(padding=(dp(24), dp(32), dp(24), dp(24)), spacing=dp(14))
        caixa = AnchorLayout(size_hint_y=None, height=dp(104))
        caixa.add_widget(Image(source=str(SIMBOLO), size_hint=(None, None),
                               size=(dp(88), dp(88)), fit_mode="contain"))
        col.add_widget(caixa)
        col.add_widget(C.Texto(text="Boas-vindas ao BioquímicaEDU", estilo="display",
                               halign="center"))
        col.add_widget(C.Texto(text="Escolha como quer usar o app. Dá para mudar depois, "
                                    "na tela Conta.",
                               estilo="corpo", halign="center", color=COR["tinta2"]))
        col.add_widget(C.espacador(dp(4)))
        self.area = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(14))
        self.area.bind(minimum_height=self.area.setter("height"))
        col.add_widget(self.area)
        col.add_widget(C.espacador(dp(4)))
        col.add_widget(C.Texto(
            text="Com o Google, o app recebe só o seu nome e o seu e-mail. A senha é "
                 "digitada no próprio Google e nunca passa pelo BioquímicaEDU.",
            estilo="micro", halign="center", color=COR["tinta3"]))
        self.add_widget(scroll)
        self._opcoes(erro)

    # ── estados ─────────────────────────────────────────────────────
    def _opcoes(self, erro=None):
        self.area.clear_widgets()
        if erro:
            self.area.add_widget(C.Aviso(erro, tipo="erro"))
        acesso = self.app.acesso

        com_conta = C.Cartao(spacing=dp(10))
        com_conta.add_widget(C.Texto(text="Com a conta Google", estilo="subtitulo"))
        com_conta.add_widget(C.Texto(text="O app lembra de você em qualquer aparelho: o "
                                          "computador, o tablet e o celular.",
                                     estilo="apoio"))
        self.botao_google = BotaoGoogle()
        self.botao_google.bind(on_release=lambda *_: self._entrar_com_google())
        com_conta.add_widget(self.botao_google)
        if not acesso.google_disponivel():
            self.botao_google.disabled = True
            com_conta.add_widget(C.Texto(text="O login com Google ainda não foi configurado "
                                              "nesta versão do app.",
                                         estilo="micro", color=COR["tinta3"]))
        self.area.add_widget(com_conta)

        sem_conta = C.Cartao(spacing=dp(10))
        sem_conta.add_widget(C.Texto(text="Sem conta", estilo="subtitulo"))
        sem_conta.add_widget(C.Texto(text="Tudo fica salvo só neste aparelho. Você pode "
                                          "entrar com o Google depois, sem perder nada.",
                                     estilo="apoio"))
        self.botao_sem_conta = C.Botao("Usar sem conta", variante="neutro")
        self.botao_sem_conta.bind(on_release=lambda *_: self._usar_sem_conta())
        sem_conta.add_widget(self.botao_sem_conta)
        self.area.add_widget(sem_conta)
        C.aparecer([com_conta, sem_conta])

    def _aguardando(self):
        self.area.clear_widgets()
        cartao = C.Cartao(spacing=dp(14))
        linha = AnchorLayout(size_hint_y=None, height=dp(48))
        self.indicador = C.Digitando(texto="Entrando")
        linha.add_widget(self.indicador)
        cartao.add_widget(linha)
        onde = ("Escolha a sua conta Google na janela do Android." if platform == "android"
                else "Continue no navegador que acabou de abrir: escolha a sua conta "
                     "Google e volte para cá.")
        cartao.add_widget(C.Texto(text=onde, estilo="corpo", halign="center"))
        cancelar = C.Botao("Cancelar", variante="fantasma")
        cancelar.bind(on_release=lambda *_: self._cancelar())
        cartao.add_widget(cancelar)
        self.area.add_widget(cartao)

    # ── ações ───────────────────────────────────────────────────────
    def _usar_sem_conta(self):
        self.app.acesso.usar_sem_conta()
        self.app.seguir_apos_acesso()

    def _entrar_com_google(self):
        if self.cancelar is not None:   # um login já em andamento
            return
        self.cancelar = threading.Event()
        self._aguardando()
        threading.Thread(target=self._login, args=(self.cancelar,), daemon=True).start()

    def _cancelar(self):
        if self.cancelar is not None:
            self.cancelar.set()
        self.cancelar = None
        self._opcoes()

    def _login(self, cancelar):
        try:
            sessao = self.app.acesso.entrar_com_google(cancelar)
        except A.LoginCancelado as e:
            mensagem = None if cancelar.is_set() else str(e)
            Clock.schedule_once(lambda _dt: self._falhou(cancelar, mensagem), 0)
            return
        except A.ErroLogin as e:
            Clock.schedule_once(lambda _dt, m=str(e): self._falhou(cancelar, m), 0)
            return
        except Exception as e:   # noqa: BLE001  (nada pode derrubar a tela)
            print(f"[conta] falha inesperada no login: {type(e).__name__}: {e}")
            Clock.schedule_once(lambda _dt: self._falhou(
                cancelar, "Não foi possível entrar agora. Tente de novo."), 0)
            return
        Clock.schedule_once(lambda _dt: self._entrou(cancelar, sessao), 0)

    def _falhou(self, cancelar, mensagem):
        if cancelar.is_set() and mensagem is None:
            return   # o estudante cancelou: a tela já voltou às opções
        self.cancelar = None
        self._opcoes(mensagem)

    def _entrou(self, cancelar, sessao):
        if cancelar.is_set():
            return   # cancelado no último instante: a tela já voltou às opções
        self.cancelar = None
        nome = (sessao.nome or sessao.email or "").split(" ")[0]
        self.app.seguir_apos_acesso()
        self.app.mostrar_mensagem(f"Olá, {nome}! Você entrou com o Google." if nome
                                  else "Você entrou com o Google.", "sucesso")
