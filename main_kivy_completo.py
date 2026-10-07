"""
BioquímicaEDU — o app (Kivy) aberto no computador.

O mesmo app do celular, que se adapta à largura da janela: celular,
tablet e computador. O código fica na pasta mobile/. Equivale a
`python main.py`; mantido para quem já usava este arquivo.

Executar:  python main_kivy_completo.py            (janela larga)
           python main_kivy_completo.py --celular  (formato de celular)
"""

import os

# o Kivy encerra ao ver opções que não conhece (--celular)
os.environ.setdefault("KIVY_NO_ARGS", "1")

from mobile.app import BioquimicaApp  # noqa: E402

if __name__ == "__main__":
    BioquimicaApp().run()
