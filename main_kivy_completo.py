"""
BioquímicaEDU — versão mobile (Kivy), aberta no computador.

Abre o app numa janela com formato de celular, para testar e estudar no
PC. O código fica na pasta mobile/. No Android e no iOS o ponto de
entrada é o main.py, que detecta o celular e abre esta mesma versão.

Executar:  python main_kivy_completo.py
"""

from mobile.app import BioquimicaApp

if __name__ == "__main__":
    BioquimicaApp().run()
