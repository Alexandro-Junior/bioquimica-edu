"""Ponto de entrada do executável do Windows (PyInstaller).

Abre direto o aplicativo (mobile/, em Kivy), sem passar pelo main.py,
que também carrega a versão clássica em Tkinter, desnecessária aqui.
"""

import os
import sys

# Sem janela de console, o Windows não dá saída padrão ao programa: o Kivy
# e os print() do app escreveriam no vazio e poderiam falhar.
if sys.stdout is None or sys.stderr is None:
    nulo = open(os.devnull, "w", encoding="utf-8")
    sys.stdout = sys.stdout or nulo
    sys.stderr = sys.stderr or nulo
    os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")
os.environ.setdefault("KIVY_NO_ARGS", "1")

from mobile.app import BioquimicaApp  # noqa: E402  (depois do ambiente)

if __name__ == "__main__":
    BioquimicaApp().run()
