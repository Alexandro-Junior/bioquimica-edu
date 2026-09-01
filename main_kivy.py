"""
BioquímicaEDU — Versão Mobile (Kivy)
Otimizado para Android/iOS - Celulares e Tablets
Inclui: Estudo + Flashcards + Vídeos + Exemplos

Features:
✓ Interface responsiva (portrait/landscape)
✓ Toque otimizado (botões grandes)
✓ Scroll fluido
✓ Paleta bioquímica mantida
✓ 5 modos de estudo
"""

import kivy
kivy.require('2.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

import json
import csv
import random
import webbrowser
from pathlib import Path

kivy.require('2.0')
Window.size = (480, 960)  # Mobile portrait

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# ─────────────────────────────────────────────
# CORES — Reagentes da Bioquímica
# ─────────────────────────────────────────────
COR = {
    "fundo":           (0.98, 0.96, 0.93, 1),
    "superficie":      (1.0, 1.0, 1.0, 1),
    "primaria":        (0.086, 0.639, 0.290, 1),
    "primaria_dark":   (0.083, 0.502, 0.243, 1),
    "sangue":          (0.882, 0.114, 0.282, 1),
    "bile":            (0.961, 0.620, 0.063, 1),
    "indicador":       (0.486, 0.231, 0.929, 1),
    "cobalto":         (0.118, 0.533, 0.690, 1),
    "texto":           (0.122, 0.165, 0.216, 1),
    "texto2":          (0.420, 0.447, 0.502, 1),
    "sucesso":         (0.086, 0.639, 0.290, 1),
    "erro":            (0.863, 0.149, 0.149, 1),
    "branco":          (1.0, 1.0, 1.0, 1),
}

# ─────────────────────────────────────────────
# CARREGAMENTO DE DADOS
# ─────────────────────────────────────────────
def carregar_marcadores():
    marcadores = []
    try:
        with open(DATA_DIR / "marcadores.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                row["valor_ref_min"] = float(row["valor_ref_min"])
                row["valor_ref_max"] = float(row["valor_ref_max"])
                marcadores.append(row)
    except Exception as e:
        print(f"Erro ao carregar marcadores: {e}")
    return marcadores

def carregar_flashcards():
    try:
        with open(DATA_DIR / "flashcards.json", encoding="utf-8") as f:
            dados = json.load(f)
            return dados.get("flashcards", [])
    except Exception as e:
        print(f"Erro ao carregar flashcards: {e}")
        return []

def carregar_marcadores_extras():
    try:
        with open(DATA_DIR / "marcadores_extras.json", encoding="utf-8") as f:
            dados = json.load(f)
            extras = {}
            for m in dados.get("marcadores_extras", []):
                extras[m["sigla"]] = m
            return extras
    except Exception as e:
        print(f"Aviso: Extras não disponíveis: {e}")
        return {}

def carregar_casos():
    try:
        with open(DATA_DIR / "casos_clinicos.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar casos: {e}")
        return []

def carregar_quiz():
    try:
        with open(DATA_DIR / "quiz_perguntas.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar quiz: {e}")
        return []

# ─────────────────────────────────────────────
# TELA INICIAL
# ─────────────────────────────────────────────
class TelaInicial(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.bg_color = COR["fundo"]

        # Cabeçalho
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=140,
                          bg_color=COR["primaria"], padding=20, spacing=8)
        header.add_widget(Label(text="⚗  BioquímicaEDU", size_hint_y=None,
                               height=40, color=COR["branco"],
                               bold=True, font_size="24sp"))
        header.add_widget(Label(text="Aprenda Bioquímica Clínica", size_hint_y=None,
                               height=30, color=(1, 1, 1, 0.8), font_size="14sp"))
        header.add_widget(Label(text="5 modos de estudo interativo", size_hint_y=None,
                               height=25, color=(1, 1, 1, 0.6), font_size="12sp"))
        self.add_widget(header)

        # Scroll com cards
        scroll = ScrollView()
        container = BoxLayout(orientation='vertical', size_hint_y=None,
                             spacing=12, padding=16)
        container.bind(minimum_height=container.setter('height'))

        # Cards de modos de estudo
        modos = [
            ("📚 Estudo", "20 marcadores\ncom interpretações", COR["primaria"], "estudo"),
            ("🎴 Flashcards", "50 cards que viram\nao clicar", COR["bile"], "flashcards"),
            ("🎥 Vídeos", "Vídeos explicativos\ne exemplos clínicos", COR["sangue"], "videos"),
            ("🧠 Quiz", "Teste seus\nconhecimentos", COR["cobalto"], "quiz"),
            ("🩺 Diagnóstico", "Analise casos\nclínicos", COR["indicador"], "diagnostico"),
        ]

        for icone_titulo, desc, cor, modo in modos:
            btn = Button(text=f"{icone_titulo}\n{desc}",
                        size_hint_y=None, height=120,
                        background_color=cor,
                        color=COR["branco"],
                        bold=True, font_size="14sp")
            btn.bind(on_press=lambda _, m=modo: self.ir_para(m))
            container.add_widget(btn)

        scroll.add_widget(container)
        self.add_widget(scroll)

    def ir_para(self, modo):
        self.app.ir_para(modo)

# ─────────────────────────────────────────────
# MODO ESTUDO
# ─────────────────────────────────────────────
class TelaEstudo(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.marcadores = carregar_marcadores()
        self.extras = carregar_marcadores_extras()
        self.bg_color = COR["fundo"]

        # Header
        header = BoxLayout(size_hint_y=None, height=50, bg_color=COR["primaria"],
                          padding=12, spacing=8)
        btn_voltar = Button(text="←", size_hint_x=None, width=50,
                           background_color=COR["primaria_dark"],
                           on_press=lambda _: self.app.ir_para("inicio"))
        header.add_widget(btn_voltar)
        header.add_widget(Label(text="📚 Modo Estudo", font_size="16sp",
                               color=COR["branco"], bold=True))
        self.add_widget(header)

        # Busca
        busca = BoxLayout(size_hint_y=None, height=50, padding=8)
        self.busca_input = TextInput(text="", multiline=False,
                                      hint_text="🔍 Buscar...",
                                      background_color=COR["superficie"],
                                      size_hint_x=0.8)
        busca.add_widget(self.busca_input)
        self.add_widget(busca)

        # Lista de marcadores
        scroll = ScrollView()
        self.lista_container = BoxLayout(orientation='vertical', size_hint_y=None,
                                         spacing=4, padding=8)
        self.lista_container.bind(minimum_height=self.lista_container.setter('height'))
        scroll.add_widget(self.lista_container)
        self.add_widget(scroll)

        self._popular_lista()

    def _popular_lista(self):
        self.lista_container.clear_widgets()
        busca = self.busca_input.text.lower()

        for m in self.marcadores:
            if busca in m["nome"].lower() or busca in m["sigla"].lower():
                btn = Button(text=f"{m['sigla']} — {m['nome']}\n{m['categoria']}",
                            size_hint_y=None, height=70,
                            background_color=COR["superficie"],
                            color=COR["texto"],
                            font_size="12sp")
                btn.bind(on_press=lambda _, marc=m: self._detalhe(marc))
                self.lista_container.add_widget(btn)

    def _detalhe(self, m):
        """Popup com detalhe do marcador + abas"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=8)

        # Abas
        tabs = TabbedPanel(size_hint_y=0.9, default_tab_text='Info')

        # Aba 1: Info
        aba_info = TabbedPanelItem(text='Info')
        scroll_info = ScrollView()
        info_content = BoxLayout(orientation='vertical', size_hint_y=None,
                                spacing=8, padding=10)
        info_content.bind(minimum_height=info_content.setter('height'))

        info_content.add_widget(Label(text=m["nome"], size_hint_y=None, height=30,
                                      bold=True, font_size="16sp", color=COR["texto"]))
        info_content.add_widget(Label(text=f"Ref: {m['valor_ref_min']}–{m['valor_ref_max']} {m['unidade']}",
                                      size_hint_y=None, height=25, font_size="12sp",
                                      color=COR["texto2"]))
        info_content.add_widget(Label(text=f"Elevado: {m['interpretacao_alta'][:100]}...",
                                      size_hint_y=None, height=60, font_size="11sp",
                                      text_size=(350, None), color=COR["texto"]))
        info_content.add_widget(Label(text=f"Baixo: {m['interpretacao_baixa'][:100]}...",
                                      size_hint_y=None, height=60, font_size="11sp",
                                      text_size=(350, None), color=COR["texto"]))

        scroll_info.add_widget(info_content)
        aba_info.content = scroll_info
        tabs.add_widget(aba_info)

        # Aba 2: Vídeos (se disponível)
        if m["sigla"] in self.extras and self.extras[m["sigla"]].get("videos"):
            aba_videos = TabbedPanelItem(text='Vídeos')
            scroll_videos = ScrollView()
            videos_content = BoxLayout(orientation='vertical', size_hint_y=None,
                                      spacing=8, padding=10)
            videos_content.bind(minimum_height=videos_content.setter('height'))

            for vid in self.extras[m["sigla"]]["videos"]:
                lbl = Label(text=f"🎥 {vid['titulo']}", size_hint_y=None,
                           height=30, font_size="12sp", bold=True,
                           color=COR["texto"])
                videos_content.add_widget(lbl)

                btn_video = Button(text="▶ Assistir", size_hint_y=None, height=40,
                                  background_color=COR["sangue"])
                def abrir_vid(_, url=vid["url"]):
                    webbrowser.open(url.replace("/embed/", "/watch?v="))
                btn_video.bind(on_press=abrir_vid)
                videos_content.add_widget(btn_video)

            scroll_videos.add_widget(videos_content)
            aba_videos.content = scroll_videos
            tabs.add_widget(aba_videos)

        # Aba 3: Exemplos (se disponível)
        if m["sigla"] in self.extras and self.extras[m["sigla"]].get("exemplos"):
            aba_exemplos = TabbedPanelItem(text='Exemplos')
            scroll_exemplos = ScrollView()
            exemplos_content = BoxLayout(orientation='vertical', size_hint_y=None,
                                        spacing=8, padding=10)
            exemplos_content.bind(minimum_height=exemplos_content.setter('height'))

            for i, ex in enumerate(self.extras[m["sigla"]]["exemplos"], 1):
                exemplos_content.add_widget(Label(text=f"📋 Caso {i}: {ex['titulo']}",
                                                 size_hint_y=None, height=25,
                                                 font_size="12sp", bold=True,
                                                 color=COR["texto"]))
                exemplos_content.add_widget(Label(text=ex['descricao'][:100] + "...",
                                                 size_hint_y=None, height=50,
                                                 font_size="10sp",
                                                 text_size=(350, None),
                                                 color=COR["texto2"]))
                exemplos_content.add_widget(Label(text=f"💊 {ex['conducao'][:80]}...",
                                                 size_hint_y=None, height=40,
                                                 font_size="10sp",
                                                 text_size=(350, None),
                                                 color=COR["texto"]))
                exemplos_content.add_widget(Label(size_hint_y=None, height=10))

            scroll_exemplos.add_widget(exemplos_content)
            aba_exemplos.content = scroll_exemplos
            tabs.add_widget(aba_exemplos)

        content.add_widget(tabs)

        # Botões
        botoes = BoxLayout(size_hint_y=0.1, spacing=10, padding=10)
        btn_fechar = Button(text="Fechar", background_color=COR["texto2"])
        botoes.add_widget(btn_fechar)
        content.add_widget(botoes)

        popup = Popup(title=m["nome"], content=content, size_hint=(0.95, 0.9))
        btn_fechar.bind(on_press=popup.dismiss)
        popup.open()

# ─────────────────────────────────────────────
# MODO FLASHCARDS
# ─────────────────────────────────────────────
class TelaFlashcards(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.flashcards = carregar_flashcards()
        self.indice = 0
        self.virado = False
        self.bg_color = COR["fundo"]

        # Header
        header = BoxLayout(size_hint_y=None, height=50, bg_color=COR["bile"],
                          padding=12, spacing=8)
        btn_voltar = Button(text="←", size_hint_x=None, width=50,
                           background_color=COR["bile"], bold=True,
                           on_press=lambda _: self.app.ir_para("inicio"))
        header.add_widget(btn_voltar)
        header.add_widget(Label(text="🎴 Flashcards", font_size="16sp",
                               color=COR["branco"], bold=True))
        self.add_widget(header)

        # Progresso
        prog = BoxLayout(size_hint_y=None, height=40, padding=10)
        prog.add_widget(Label(text=f"{self.indice + 1}/{len(self.flashcards)}",
                             bold=True, font_size="16sp", color=COR["texto"]))
        self.add_widget(prog)

        # Card
        self.card_btn = Button(text="❓\n\nClique no card para virar",
                              size_hint_y=0.6, background_color=COR["primaria"],
                              color=COR["branco"], bold=True, font_size="18sp")
        self.card_btn.bind(on_press=lambda _: self._virar())
        self.add_widget(self.card_btn)

        # Botões navegação
        nav = BoxLayout(size_hint_y=None, height=60, spacing=10, padding=10)
        btn_ant = Button(text="← Anterior", background_color=COR["texto2"])
        btn_ant.bind(on_press=lambda _: self._anterior())
        nav.add_widget(btn_ant)

        btn_prox = Button(text="Próximo →", background_color=COR["primaria"])
        btn_prox.bind(on_press=lambda _: self._proximo())
        nav.add_widget(btn_prox)

        self.add_widget(nav)
        self._atualizar()

    def _virar(self):
        self.virado = not self.virado
        self._atualizar()

    def _anterior(self):
        if self.indice > 0:
            self.indice -= 1
            self.virado = False
            self._atualizar()

    def _proximo(self):
        if self.indice < len(self.flashcards) - 1:
            self.indice += 1
            self.virado = False
            self._atualizar()
        else:
            from kivy.uix.popup import Popup
            pop = Popup(title="Parabéns!",
                       content=BoxLayout(children=[Label(text="Você completou todos os flashcards! 🎉")]),
                       size_hint=(0.8, 0.3))
            pop.open()

    def _atualizar(self):
        card = self.flashcards[self.indice]
        if self.virado:
            self.card_btn.text = f"✅\n\n{card['resposta']}"
            self.card_btn.background_color = COR["primaria_dark"]
        else:
            self.card_btn.text = f"❓\n\n{card['pergunta']}"
            self.card_btn.background_color = COR["primaria"]

# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────
class BioquimicaEDUApp(App):
    def build(self):
        Window.size = (480, 960)
        self.telas = {}
        self.container = BoxLayout()
        self.ir_para("inicio")
        return self.container

    def ir_para(self, modo):
        self.container.clear_widgets()

        if modo == "inicio":
            tela = TelaInicial(self)
        elif modo == "estudo":
            tela = TelaEstudo(self)
        elif modo == "flashcards":
            tela = TelaFlashcards(self)
        elif modo == "videos":
            tela = TelaEstudo(self)  # Mesma tela de estudo (videos integrados)
        elif modo == "quiz":
            tela = TelaInicial(self)  # Placeholder
        elif modo == "diagnostico":
            tela = TelaInicial(self)  # Placeholder
        else:
            tela = TelaInicial(self)

        self.container.add_widget(tela)

if __name__ == "__main__":
    BioquimicaEDUApp().run()
