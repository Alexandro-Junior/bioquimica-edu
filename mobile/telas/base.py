"""Base comum das telas."""

from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import Screen

from mobile.tema import COR


class TelaBase(Screen):
    """Tela que se reconstrói a cada visita.

    Reconstruir ao entrar garante que o conteúdo reflita o progresso que
    acabou de mudar (uma revisão feita, um caso resolvido) sem que cada
    tela precise saber quem alterou o quê.
    """

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.parametros = {}
        with self.canvas.before:
            Color(*COR["fundo"])
            # Screen é um RelativeLayout: o desenho é relativo a ela
            self._fundo = Rectangle(pos=(0, 0))
        self.bind(size=lambda *_: setattr(self._fundo, "size", self.size))

    def preparar(self, **parametros):
        self.parametros = parametros
        self.clear_widgets()
        self.montar(**parametros)

    def montar(self, **parametros):
        raise NotImplementedError
