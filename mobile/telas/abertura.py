"""Tela de abertura: logo e nome do app enquanto ele carrega.

Continua a imagem de abertura do Android (mesma logo, mesmo fundo), então
a passagem do sistema para o app não pisca. A logo surge e assenta em
0,35 s; logo abaixo, três pontos discretos mostram que o app está
carregando, e o rodapé traz a origem do projeto. O carregamento acontece em
paralelo: a tela fica só o tempo mínimo para ser percebida.

Se o conteúdo não puder ser lido, a própria abertura diz o que houve e
oferece tentar de novo, em vez de abrir um app vazio.
"""

from pathlib import Path

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from mobile import componentes as C
from mobile.tema import COR, movimento
from mobile.telas.base import TelaBase

LOGO = Path(__file__).resolve().parents[2] / "assets" / "logo" / "abertura.png"
LOGO_RESERVA = Path(__file__).resolve().parents[2] / "assets" / "logo" / "vertical.png"
PROPORCAO_LOGO = 500 / 720   # altura / largura de abertura.png


class TelaAbertura(TelaBase):

    LARGURA_MAXIMA = 480   # dp, em tablet e computador

    def montar(self, **_):
        self.coluna = BoxLayout(orientation="vertical", padding=(dp(32), 0, dp(32), dp(20)))
        self.coluna.add_widget(Widget())
        caixa = AnchorLayout(size_hint_y=None)
        arquivo = LOGO if LOGO.exists() else LOGO_RESERVA
        self.logo = C.Superficie(size_hint=(None, None))
        self.logo.add_widget(Image(source=str(arquivo), fit_mode="contain"))
        caixa.add_widget(self.logo)
        self.coluna.add_widget(caixa)

        # a tela nasce antes de a janela ter a largura final: a logo
        # acompanha a coluna até o layout assentar
        def ajustar(*_):
            largura = min(dp(300), max(dp(180), self.coluna.width * 0.8))
            self.logo.size = (largura, largura * PROPORCAO_LOGO)
            caixa.height = self.logo.height + dp(8)
        self.coluna.bind(width=ajustar)
        ajustar()

        self.area_estado = BoxLayout(orientation="vertical", size_hint_y=None,
                                     spacing=dp(12), padding=(0, dp(28), 0, 0))
        self.area_estado.bind(minimum_height=self.area_estado.setter("height"))
        self.carregando = BoxLayout(size_hint=(None, None), size=(dp(52), dp(12)),
                                    spacing=dp(8), pos_hint={"center_x": 0.5})
        self.pontos = [C.Ponto(COR["acento"], tamanho=dp(9)) for _ in range(3)]
        for ponto in self.pontos:
            self.carregando.add_widget(ponto)
        self.area_estado.add_widget(self.carregando)
        self.coluna.add_widget(self.area_estado)
        self.coluna.add_widget(Widget())
        self.coluna.add_widget(C.rotulo("UNICID · PIBIC/CNPq", "13sp", COR["tinta3"],
                                        alinhar="center"))
        self.add_widget(self.coluna)

        if movimento():
            self.logo.opacity = 0
            self.logo.escala = 0.94
            Animation(opacity=1, escala=1.0, duration=0.35, t="out_cubic").start(self.logo)
            for i, ponto in enumerate(self.pontos):
                ponto.opacity = 0.25
                Clock.schedule_once(lambda _dt, p=ponto: self._pulsar(p), 0.2 + i * 0.16)

    @staticmethod
    def _pulsar(ponto):
        anim = (Animation(opacity=1, duration=0.45, t="in_out_sine")
                + Animation(opacity=0.25, duration=0.45, t="in_out_sine"))
        anim.repeat = True
        anim.start(ponto)

    def on_leave(self, *_):
        for ponto in getattr(self, "pontos", []):
            Animation.cancel_all(ponto)

    def mostrar_erro(self, mensagem, ao_tentar):
        self.on_leave()
        self.area_estado.clear_widgets()
        self.area_estado.add_widget(C.Aviso(
            "Os arquivos da pasta data podem estar faltando ou corrompidos. "
            "Reinstalar o app resolve na maioria dos casos.",
            tipo="erro", titulo=mensagem))
        tentar = C.Botao("Tentar de novo", variante="primario", icone="repetir")
        tentar.bind(on_release=lambda *_: ao_tentar())
        self.area_estado.add_widget(tentar)
