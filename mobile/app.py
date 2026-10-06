"""Aplicativo mobile do BioquímicaEDU: dados, progresso, navegação e transições.

Navegação em dois níveis, como nos apps de estudo atuais:

- abas na barra inferior (Início, Estudo, Cards, Prática, Tutor), trocadas
  com um esmaecer rápido, porque são lugares paralelos;
- telas empilhadas (detalhe de um marcador, sessão de revisão), que entram
  deslizando da direita e escondem a barra, porque são um aprofundamento
  com começo e fim. O botão voltar do Android desfaz a pilha.
"""

from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import (FadeTransition, NoTransition, ScreenManager,
                                    SlideTransition)
from kivy.utils import platform

from mobile import dados
from mobile.componentes import BarraNavegacao
from mobile.tema import COR
from mobile.telas.cartas import TelaCartas
from mobile.telas.estudo import TelaDetalhe, TelaEstudo
from mobile.telas.inicio import TelaInicio
from mobile.telas.pratica import TelaPratica
from mobile.telas.revisao import TelaRevisao
from mobile.telas.tutor import TelaTutor

NO_CELULAR = platform in ("android", "ios")

if not NO_CELULAR:
    # no computador, janela no formato de um celular atual
    Window.size = (400, 840)
# o teclado empurra a tela em vez de cobrir o campo de digitação
Window.softinput_mode = "below_target"

# Telas de aprofundamento: sem barra inferior e com voltar
EMPILHADAS = {"detalhe", "revisao"}

ABA_DA_TELA = {
    "inicio": "inicio", "estudo": "estudo", "detalhe": "estudo",
    "cartas": "cartas", "pratica": "pratica", "tutor": "tutor",
    "revisao": "inicio",
}

# Nomes da versão anterior, mantidos para quem ainda chama ir_para com eles
APELIDOS = {
    "flashcards":  ("cartas", {}),
    "quiz":        ("pratica", {"modo": "quiz", "iniciar": True}),
    "diagnostico": ("pratica", {"modo": "casos"}),
}


class BioquimicaApp(App):
    title = "BioquímicaEDU"
    icon = str(Path(__file__).resolve().parent.parent / "assets" / "icon.png")

    TELAS = {
        "inicio": TelaInicio,
        "estudo": TelaEstudo,
        "detalhe": TelaDetalhe,
        "cartas": TelaCartas,
        "pratica": TelaPratica,
        "revisao": TelaRevisao,
        "tutor": TelaTutor,
    }

    def build(self):
        from progresso import Progresso

        Window.clearcolor = COR["fundo"]
        self.progresso = Progresso(self._arquivo_progresso())
        self.marcadores = dados.carregar_marcadores()
        self.flashcards = dados.carregar_flashcards()
        self.extras = dados.carregar_extras()
        self.imagens = dados.carregar_imagens()
        self.quiz = dados.carregar_quiz()
        self.casos = dados.carregar_casos()
        self.casos_resolvidos = set()
        self.ultimo_quiz = None
        self.ia = self._iniciar_ia()
        self.historico = []

        self.raiz = BoxLayout(orientation="vertical")
        self.gerenciador = ScreenManager(transition=NoTransition())
        for nome, Classe in self.TELAS.items():
            self.gerenciador.add_widget(Classe(self, name=nome))
        self.navegacao = BarraNavegacao(ao_escolher=self.ir_para)
        self.raiz.add_widget(self.gerenciador)
        self.raiz.add_widget(self.navegacao)

        Window.bind(on_keyboard=self._tecla)
        self.ir_para("inicio", animar=False)
        return self.raiz

    # ── armazenamento ───────────────────────────────────────────────
    def _arquivo_progresso(self):
        """Onde o progresso fica salvo.

        No celular, na pasta privada do app: fica fora do código, então uma
        atualização do APK não apaga o que o estudante já estudou, e o app
        não precisa de permissão de armazenamento. No computador, em
        data/progresso.json, compartilhado com a versão desktop.
        """
        if NO_CELULAR:
            return Path(self.user_data_dir) / "progresso.json"
        return None

    @staticmethod
    def _iniciar_ia():
        """Ollama só existe no computador; no celular o tutor é offline."""
        if NO_CELULAR:
            return None
        try:
            # o módulo já cria e testa uma instância ao ser importado
            from ollama_ia import ia
        except Exception as e:
            print(f"[tutor] Ollama indisponível ({type(e).__name__}); usando modo offline")
            return None
        return ia if getattr(ia, "disponivel", False) else None

    # ── navegação ───────────────────────────────────────────────────
    def tela_atual(self):
        return self.gerenciador.current_screen

    def ir_para(self, destino, animar=True, foco=None, **parametros):
        if destino in APELIDOS:
            destino, extras = APELIDOS[destino]
            parametros = {**extras, **parametros}
        if destino == "estudo" and foco:
            destino, parametros = "detalhe", {"sigla": foco}
        if not self.gerenciador.has_screen(destino):
            print(f"[navegação] tela desconhecida: {destino}")
            return

        atual = self.gerenciador.current
        if destino in EMPILHADAS:
            if atual != destino:
                self.historico.append(atual)
        else:
            self.historico.clear()

        self.gerenciador.transition = self._transicao(atual, destino, animar)
        self.gerenciador.get_screen(destino).preparar(**parametros)
        self.gerenciador.current = destino
        self._ajustar_navegacao(destino)

    def voltar(self):
        anterior = self.historico.pop() if self.historico else "inicio"
        atual = self.gerenciador.current
        tela = self.gerenciador.get_screen(anterior)
        # o início precisa refletir o que acabou de mudar; as outras telas
        # voltam como estavam (busca, filtro e rolagem preservados)
        if anterior == "inicio" or not tela.children:
            tela.preparar(**tela.parametros)
        self.gerenciador.transition = (SlideTransition(direction="right", duration=0.26)
                                       if atual != anterior else NoTransition())
        self.gerenciador.current = anterior
        self._ajustar_navegacao(anterior)

    @staticmethod
    def _transicao(atual, destino, animar):
        if not animar or atual == destino:
            return NoTransition()
        if destino in EMPILHADAS:
            return SlideTransition(direction="left", duration=0.26)
        if atual in EMPILHADAS:
            return SlideTransition(direction="right", duration=0.26)
        return FadeTransition(duration=0.16)

    def _ajustar_navegacao(self, destino):
        esconder = destino in EMPILHADAS
        self.navegacao.height = 0 if esconder else BarraNavegacao.ALTURA
        self.navegacao.opacity = 0 if esconder else 1
        self.navegacao.disabled = esconder
        if not esconder:
            self.navegacao.selecionar(ABA_DA_TELA.get(destino, "inicio"))

    def _tecla(self, _janela, tecla, *_args):
        """Botão voltar do Android (e Esc no computador)."""
        if tecla != 27:
            return False
        atual = self.gerenciador.current
        if atual in EMPILHADAS:
            self.voltar()
            return True
        if atual != "inicio":
            self.ir_para("inicio")
            return True
        return False  # no início, voltar fecha o app

    # ── motor de estudo ─────────────────────────────────────────────
    def alimentar_memoria(self, texto, acertou, peso):
        """Liga quiz e casos clínicos ao motor de repetição espaçada."""
        from progresso import marcadores_no_texto
        siglas = [m["sigla"] for m in self.marcadores]
        nomes = {m["sigla"]: m["nome"] for m in self.marcadores}
        alvos = marcadores_no_texto(texto, siglas, nomes)
        if alvos:
            self.progresso.registrar_atividade(alvos, acertou, peso=peso)
        return alvos
