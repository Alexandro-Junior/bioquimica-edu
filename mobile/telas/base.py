"""Base comum das telas."""

from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.layout import Layout
from kivy.uix.screenmanager import Screen

from mobile.tema import COR


class Moldura(Layout):
    """Centraliza o conteúdo numa coluna de largura máxima.

    No celular a coluna ocupa a tela toda; no tablet e no computador, linhas
    de texto da largura da janela ficariam longas demais para ler, e botões
    de 1.200 px de largura parecem esticados.
    """

    def __init__(self, largura_maxima, **kwargs):
        super().__init__(**kwargs)
        self.largura_maxima = largura_maxima
        self.bind(size=self._trigger_layout, pos=self._trigger_layout)

    def do_layout(self, *_):
        largura = min(self.width, self.largura_maxima)
        for filho in self.children:
            filho.size = (largura, self.height)
            filho.pos = (self.x + (self.width - largura) / 2, self.y)


class TelaBase(Screen):
    """Tela que se reconstrói a cada visita.

    Reconstruir ao entrar garante que o conteúdo reflita o progresso que
    acabou de mudar (uma revisão feita, um caso resolvido) sem que cada
    tela precise saber quem alterou o quê.

    LARGURA_MAXIMA (dp) limita a coluna de conteúdo em telas largas; None
    deixa a tela usar a largura inteira.
    """

    LARGURA_MAXIMA = 760

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.parametros = {}
        self._moldura = None
        with self.canvas.before:
            Color(*COR["fundo"])
            # Screen é um RelativeLayout: o desenho é relativo a ela
            self._fundo = Rectangle(pos=(0, 0))
        self.bind(size=lambda *_: setattr(self._fundo, "size", self.size))

    def preparar(self, **parametros):
        self.parametros = parametros
        self.clear_widgets()
        self._moldura = None
        maxima = self.largura_maxima(**parametros)
        if maxima:
            self._moldura = Moldura(dp(maxima))
            super().add_widget(self._moldura)
        self.montar(**parametros)

    def largura_maxima(self, **_parametros):
        """Largura máxima da coluna (dp); telas podem variar conforme o estado."""
        return self.LARGURA_MAXIMA

    def add_widget(self, widget, *args, **kwargs):
        # o que a tela monta vai para dentro da moldura
        if self._moldura is not None and widget is not self._moldura:
            return self._moldura.add_widget(widget, *args, **kwargs)
        return super().add_widget(widget, *args, **kwargs)

    def largura_util(self):
        """Largura da coluna de conteúdo, para telas que se reorganizam."""
        from kivy.core.window import Window
        largura = self.width or Window.width
        maxima = self.largura_maxima(**self.parametros)
        if maxima:
            largura = min(largura, dp(maxima))
        return largura

    def montar(self, **parametros):
        raise NotImplementedError
