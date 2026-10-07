"""Tela de abertura: a logo enquanto o app carrega.

Continua a imagem de abertura do Android (mesma logo, mesmo fundo), então
a passagem do sistema para o app não pisca. A animação é uma só — a logo
surge e assenta em 0,35 s — e não atrasa nada: o carregamento acontece em
paralelo, e a tela fica no máximo o tempo mínimo para ser percebida.

Se o conteúdo não puder ser lido, a própria abertura diz o que houve e
oferece tentar de novo, em vez de abrir um app vazio.
"""

from pathlib import Path

from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from mobile import componentes as C
from mobile.tema import movimento
from mobile.telas.base import TelaBase

LOGO = Path(__file__).resolve().parents[2] / "assets" / "logo" / "abertura.png"
LOGO_RESERVA = Path(__file__).resolve().parents[2] / "assets" / "logo" / "vertical.png"


class TelaAbertura(TelaBase):

    def montar(self, **_):
        self.coluna = BoxLayout(orientation="vertical", padding=(dp(32), 0))
        self.coluna.add_widget(Widget())
        caixa = AnchorLayout(size_hint_y=None, height=dp(200))
        arquivo = LOGO if LOGO.exists() else LOGO_RESERVA
        self.logo = C.Superficie(size_hint=(None, None), size=(dp(220), dp(154)))
        self.logo.add_widget(Image(source=str(arquivo), fit_mode="contain"))
        caixa.add_widget(self.logo)
        self.coluna.add_widget(caixa)
        self.area_estado = BoxLayout(orientation="vertical", size_hint_y=None,
                                     spacing=dp(12), padding=(0, dp(16), 0, 0))
        self.area_estado.bind(minimum_height=self.area_estado.setter("height"))
        self.coluna.add_widget(self.area_estado)
        self.coluna.add_widget(Widget())
        self.add_widget(self.coluna)

        if movimento():
            self.logo.opacity = 0
            self.logo.escala = 0.94
            Animation(opacity=1, escala=1.0, duration=0.35, t="out_cubic").start(self.logo)

    def mostrar_erro(self, mensagem, ao_tentar):
        self.area_estado.clear_widgets()
        self.area_estado.add_widget(C.Aviso(
            "Os arquivos da pasta data podem estar faltando ou corrompidos. "
            "Reinstalar o app resolve na maioria dos casos.",
            tipo="erro", titulo=mensagem))
        tentar = C.Botao("Tentar de novo", variante="primario", icone="repetir")
        tentar.bind(on_release=lambda *_: ao_tentar())
        self.area_estado.add_widget(tentar)
