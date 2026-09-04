"""
BioquímicaEDU — Versão Mobile COMPLETA (Kivy)
Android/iOS - 5 Modos de Estudo + IA Integrada

✅ Modo Estudo (20 marcadores + vídeos + exemplos)
✅ Flashcards (50 cards que viram)
✅ Quiz (10+ perguntas dinâmicas)
✅ Diagnóstico (5 casos clínicos)
✅ Tutor IA (chat conversacional offline)
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image

import json
import csv
import random
import webbrowser
import threading
from pathlib import Path

Window.size = (480, 960)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# ─────────────────────────────────────────────
# CORES
# ─────────────────────────────────────────────
COR = {
    "fundo":       (0.98, 0.96, 0.93, 1),
    "superficie":  (1.0, 1.0, 1.0, 1),
    "primaria":    (0.086, 0.639, 0.290, 1),
    "sangue":      (0.882, 0.114, 0.282, 1),
    "bile":        (0.961, 0.620, 0.063, 1),
    "cobalto":     (0.118, 0.533, 0.690, 1),
    "indicador":   (0.486, 0.231, 0.929, 1),
    "texto":       (0.122, 0.165, 0.216, 1),
    "texto2":      (0.420, 0.447, 0.502, 1),
    "sucesso":     (0.086, 0.639, 0.290, 1),
    "erro":        (0.863, 0.149, 0.149, 1),
    "branco":      (1.0, 1.0, 1.0, 1),
}

# ─────────────────────────────────────────────
# CARREGAMENTO
# ─────────────────────────────────────────────
def carregar_marcadores():
    marcadores = []
    try:
        with open(DATA_DIR / "marcadores.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                row["valor_ref_min"] = float(row["valor_ref_min"])
                row["valor_ref_max"] = float(row["valor_ref_max"])
                marcadores.append(row)
    except: pass
    return marcadores

def carregar_flashcards():
    try:
        with open(DATA_DIR / "flashcards.json", encoding="utf-8") as f:
            return json.load(f).get("flashcards", [])
    except: return []

def carregar_extras():
    try:
        with open(DATA_DIR / "marcadores_extras.json", encoding="utf-8") as f:
            dados = json.load(f)
            return {m["sigla"]: m for m in dados.get("marcadores_extras", [])}
    except: return {}

def carregar_quiz():
    try:
        with open(DATA_DIR / "quiz_perguntas.json", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def carregar_casos():
    try:
        with open(DATA_DIR / "casos_clinicos.json", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def carregar_imagens():
    try:
        with open(DATA_DIR / "marcadores_imagens.json", encoding="utf-8") as f:
            dados = json.load(f)
            return {m["sigla"]: m for m in dados.get("marcadores_imagens", [])}
    except: return {}

# ─────────────────────────────────────────────
# TELA INICIAL
# ─────────────────────────────────────────────
class TelaInicial(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.bg_color = COR["fundo"]

        header = BoxLayout(orientation='vertical', size_hint_y=None, height=140,
                          bg_color=COR["primaria"], padding=20, spacing=8)
        header.add_widget(Label(text="⚗  BioquímicaEDU", size_hint_y=None,
                               height=40, color=COR["branco"], bold=True, font_size="24sp"))
        header.add_widget(Label(text=f"⚡ XP: {app.xp}  🔥 Streak: {app.streak}",
                               size_hint_y=None, height=30, color=(1, 1, 1, 0.8),
                               font_size="13sp"))
        header.add_widget(Label(text="5 modos interativos", size_hint_y=None,
                               height=25, color=(1, 1, 1, 0.6), font_size="12sp"))
        self.add_widget(header)

        scroll = ScrollView()
        container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12, padding=16)
        container.bind(minimum_height=container.setter('height'))

        modos = [
            ("📚 Estudo", "20 marcadores\ncom vídeos", COR["primaria"], "estudo"),
            ("🎴 Flashcards", "50 cards flip", COR["bile"], "flashcards"),
            ("🧠 Quiz", "Teste dinâmico\ncom IA", COR["cobalto"], "quiz"),
            ("🩺 Diagnóstico", "5 casos\nclínicos", COR["indicador"], "diagnostico"),
            ("💬 Tutor IA", "Chat com\ntutor offline", COR["sangue"], "tutor"),
        ]

        for titulo, desc, cor, modo in modos:
            btn = Button(text=f"{titulo}\n{desc}", size_hint_y=None, height=100,
                        background_color=cor, color=COR["branco"],
                        bold=True, font_size="13sp")
            btn.bind(on_press=lambda _, m=modo: self.app.ir_para(m))
            container.add_widget(btn)

        scroll.add_widget(container)
        self.add_widget(scroll)

# ─────────────────────────────────────────────
# MODO ESTUDO (Integrado com vídeos/exemplos)
# ─────────────────────────────────────────────
class TelaEstudo(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.marcadores = carregar_marcadores()
        self.extras = carregar_extras()
        self.imagens = carregar_imagens()
        self.bg_color = COR["fundo"]

        header = BoxLayout(size_hint_y=None, height=50, bg_color=COR["primaria"],
                          padding=12, spacing=8)
        btn_voltar = Button(text="←", size_hint_x=None, width=50,
                           background_color=COR["primaria"],
                           on_press=lambda _: self.app.ir_para("inicio"))
        header.add_widget(btn_voltar)
        header.add_widget(Label(text="📚 Estudo", font_size="16sp",
                               color=COR["branco"], bold=True))
        self.add_widget(header)

        busca = BoxLayout(size_hint_y=None, height=50, padding=8)
        self.busca_input = TextInput(text="", multiline=False,
                                      hint_text="🔍 Buscar...",
                                      background_color=COR["superficie"])
        self.busca_input.bind(text=lambda *_: self._popular_lista())
        busca.add_widget(self.busca_input)
        self.add_widget(busca)

        scroll = ScrollView()
        self.lista = BoxLayout(orientation='vertical', size_hint_y=None,
                              spacing=4, padding=8)
        self.lista.bind(minimum_height=self.lista.setter('height'))
        scroll.add_widget(self.lista)
        self.add_widget(scroll)
        self._popular_lista()

    def _popular_lista(self):
        self.lista.clear_widgets()
        busca = self.busca_input.text.lower()
        for m in self.marcadores:
            if busca in m["nome"].lower() or busca in m["sigla"].lower():
                btn = Button(text=f"{m['sigla']} — {m['nome']}", size_hint_y=None,
                            height=60, background_color=COR["superficie"],
                            color=COR["texto"], font_size="12sp")
                btn.bind(on_press=lambda _, marc=m: self._detalhe(marc))
                self.lista.add_widget(btn)

    def _detalhe(self, m):
        content = BoxLayout(orientation='vertical', padding=10, spacing=8)
        tabs = TabbedPanel(size_hint_y=0.9, default_tab_text='Info')

        # Aba Info
        aba_info = TabbedPanelItem(text='Info')
        scroll_info = ScrollView()
        info_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=10)
        info_box.bind(minimum_height=info_box.setter('height'))
        info_box.add_widget(Label(text=m["nome"], size_hint_y=None, height=30,
                                  bold=True, font_size="16sp", color=COR["texto"]))
        info_box.add_widget(Label(text=f"Ref: {m['valor_ref_min']}–{m['valor_ref_max']} {m['unidade']}",
                                  size_hint_y=None, height=25, font_size="12sp"))
        info_box.add_widget(Label(text="Elevado:", size_hint_y=None, height=20,
                                  bold=True, font_size="11sp", color=COR["erro"]))
        info_box.add_widget(Label(text=m['interpretacao_alta'], size_hint_y=None,
                                  height=80, font_size="10sp", text_size=(350, None)))
        info_box.add_widget(Label(text="Baixo:", size_hint_y=None, height=20,
                                  bold=True, font_size="11sp", color=COR["cobalto"]))
        info_box.add_widget(Label(text=m['interpretacao_baixa'], size_hint_y=None,
                                  height=80, font_size="10sp", text_size=(350, None)))
        scroll_info.add_widget(info_box)
        aba_info.content = scroll_info
        tabs.add_widget(aba_info)

        # Aba Vídeos
        if m["sigla"] in self.extras and self.extras[m["sigla"]].get("videos"):
            aba_videos = TabbedPanelItem(text='Vídeos')
            scroll_videos = ScrollView()
            videos_box = BoxLayout(orientation='vertical', size_hint_y=None,
                                  spacing=8, padding=10)
            videos_box.bind(minimum_height=videos_box.setter('height'))
            for vid in self.extras[m["sigla"]]["videos"]:
                videos_box.add_widget(Label(text=f"🎥 {vid['titulo']}", size_hint_y=None,
                                           height=25, font_size="11sp", bold=True))
                btn = Button(text=f"▶ {vid.get('duracao', '?')}", size_hint_y=None,
                            height=40, background_color=COR["sangue"])
                btn.bind(on_press=lambda _, u=vid["url"]:
                        webbrowser.open(u.replace("/embed/", "/watch?v=")))
                videos_box.add_widget(btn)
            scroll_videos.add_widget(videos_box)
            aba_videos.content = scroll_videos
            tabs.add_widget(aba_videos)

        # Aba Exemplos
        if m["sigla"] in self.extras and self.extras[m["sigla"]].get("exemplos"):
            aba_exemplos = TabbedPanelItem(text='Exemplos')
            scroll_exemplos = ScrollView()
            ex_box = BoxLayout(orientation='vertical', size_hint_y=None,
                              spacing=8, padding=10)
            ex_box.bind(minimum_height=ex_box.setter('height'))
            for i, ex in enumerate(self.extras[m["sigla"]]["exemplos"], 1):
                ex_box.add_widget(Label(text=f"Caso {i}: {ex['titulo']}", size_hint_y=None,
                                       height=20, font_size="11sp", bold=True))
                ex_box.add_widget(Label(text=ex['descricao'], size_hint_y=None,
                                       height=50, font_size="10sp", text_size=(350, None)))
                ex_box.add_widget(Label(text=f"Valores: {ex['valores']}", size_hint_y=None,
                                       height=40, font_size="9sp", text_size=(350, None)))
                ex_box.add_widget(Label(text=f"💊 {ex['conducao']}", size_hint_y=None,
                                       height=50, font_size="9sp", text_size=(350, None)))
            scroll_exemplos.add_widget(ex_box)
            aba_exemplos.content = scroll_exemplos
            tabs.add_widget(aba_exemplos)

        # Aba Imagens
        if m["sigla"] in self.imagens and self.imagens[m["sigla"]].get("imagens"):
            aba_imagens = TabbedPanelItem(text='Imagens')
            scroll_imagens = ScrollView()
            img_box = BoxLayout(orientation='vertical', size_hint_y=None,
                               spacing=10, padding=10)
            img_box.bind(minimum_height=img_box.setter('height'))
            for i, img in enumerate(self.imagens[m["sigla"]]["imagens"], 1):
                img_box.add_widget(Label(text=f"📊 {img['titulo']}", size_hint_y=None,
                                        height=20, font_size="11sp", bold=True))
                img_box.add_widget(Label(text=img['descricao'], size_hint_y=None,
                                        height=50, font_size="10sp", text_size=(350, None)))
                img_path = DATA_DIR / "images" / img['arquivo']
                if img_path.exists():
                    try:
                        img_widget = Image(source=str(img_path), size_hint_y=None, height=180)
                        img_box.add_widget(img_widget)
                    except:
                        img_box.add_widget(Label(text="[Imagem não carregada]", size_hint_y=None,
                                                height=40, font_size="9sp", color=COR["texto2"]))
                else:
                    img_box.add_widget(Label(text=f"🖼 [Arquivo: {img['arquivo']}]\n(Adicione a imagem em data/images/)",
                                            size_hint_y=None, height=60, font_size="9sp",
                                            text_size=(350, None), color=COR["bile"]))
            scroll_imagens.add_widget(img_box)
            aba_imagens.content = scroll_imagens
            tabs.add_widget(aba_imagens)

        content.add_widget(tabs)
        footer = BoxLayout(size_hint_y=0.1, padding=10)
        btn_fechar = Button(text="Fechar", background_color=COR["texto2"])
        footer.add_widget(btn_fechar)
        content.add_widget(footer)

        popup = Popup(title=m["nome"], content=content, size_hint=(0.95, 0.9))
        btn_fechar.bind(on_press=popup.dismiss)
        popup.open()

# ─────────────────────────────────────────────
# FLASHCARDS
# ─────────────────────────────────────────────
class TelaFlashcards(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.flashcards = carregar_flashcards()
        self.indice = 0
        self.virado = False
        self.bg_color = COR["fundo"]

        header = BoxLayout(size_hint_y=None, height=50, bg_color=COR["bile"],
                          padding=12, spacing=8)
        btn_voltar = Button(text="←", size_hint_x=None, width=50,
                           background_color=COR["bile"],
                           on_press=lambda _: self.app.ir_para("inicio"))
        header.add_widget(btn_voltar)
        header.add_widget(Label(text="🎴 Flashcards", font_size="16sp",
                               color=COR["branco"], bold=True))
        self.add_widget(header)

        prog = BoxLayout(size_hint_y=None, height=40, padding=10)
        prog.add_widget(Label(text=f"{self.indice + 1}/{len(self.flashcards)}",
                             bold=True, font_size="16sp"))
        self.add_widget(prog)

        self.card = Button(text="❓\n\nClique para virar", size_hint_y=0.6,
                          background_color=COR["primaria"],
                          color=COR["branco"], bold=True, font_size="18sp")
        self.card.bind(on_press=lambda _: self._virar())
        self.add_widget(self.card)

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

    def _atualizar(self):
        card = self.flashcards[self.indice]
        if self.virado:
            self.card.text = f"✅\n\n{card['resposta']}"
            self.card.background_color = (0.083, 0.502, 0.243, 1)
        else:
            self.card.text = f"❓\n\n{card['pergunta']}"
            self.card.background_color = COR["primaria"]

# ─────────────────────────────────────────────
# QUIZ
# ─────────────────────────────────────────────
class TelaQuiz(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.quiz = carregar_quiz()
        self.perguntas = random.sample(self.quiz, min(10, len(self.quiz)))
        self.indice = 0
        self.acertos = 0
        self.respondido = False
        self.bg_color = COR["fundo"]

        header = BoxLayout(size_hint_y=None, height=50, bg_color=COR["cobalto"],
                          padding=12, spacing=8)
        btn_voltar = Button(text="←", size_hint_x=None, width=50,
                           background_color=COR["cobalto"],
                           on_press=lambda _: self.app.ir_para("inicio"))
        header.add_widget(btn_voltar)
        header.add_widget(Label(text="🧠 Quiz", font_size="16sp",
                               color=COR["branco"], bold=True))
        self.add_widget(header)

        self.area = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.add_widget(self.area)
        self._pergunta()

    def _pergunta(self):
        self.area.clear_widgets()
        if self.indice >= len(self.perguntas):
            self._resultado()
            return

        self.respondido = False
        p = self.perguntas[self.indice]

        self.area.add_widget(Label(text=f"{self.indice + 1}/{len(self.perguntas)}",
                                   size_hint_y=None, height=20, font_size="12sp",
                                   color=COR["texto2"]))
        self.area.add_widget(Label(text=p["pergunta"], size_hint_y=None, height=80,
                                   font_size="13sp", bold=True,
                                   text_size=(400, None), color=COR["texto"]))

        self.escolha = None
        alts_container = BoxLayout(orientation='vertical', size_hint_y=0.6, spacing=8)
        for i, alt in enumerate(p["alternativas"]):
            btn = Button(text=alt, size_hint_y=None, height=60,
                        background_color=COR["superficie"],
                        color=COR["texto"], font_size="11sp")
            def sel(_, i_=i, p_=p):
                if not self.respondido:
                    self.escolha = i_
                    self._responder(i_, p_)
            btn.bind(on_press=sel)
            alts_container.add_widget(btn)

        self.area.add_widget(alts_container)

    def _responder(self, indice, p):
        self.respondido = True
        correto = p["resposta_correta"] == indice

        if correto:
            self.acertos += 1
            self.app.xp += 10
            self.app.streak += 1
        else:
            self.app.streak = 0

        fb = BoxLayout(orientation='vertical', size_hint_y=None, height=80, padding=10)
        titulo = "✅ Correto!" if correto else "❌ Errado"
        cor = COR["sucesso"] if correto else COR["erro"]
        fb.add_widget(Label(text=titulo, size_hint_y=None, height=30,
                           font_size="14sp", bold=True, color=cor))
        fb.add_widget(Label(text=p["explicacao"], size_hint_y=None, height=50,
                           font_size="10sp", text_size=(400, None),
                           color=COR["texto"]))

        btn_prox = Button(text="Próxima →", size_hint_y=None, height=40,
                         background_color=COR["primaria"])
        def prox_pergunta(_):
            self.indice += 1
            self._pergunta()
        btn_prox.bind(on_press=prox_pergunta)
        fb.add_widget(btn_prox)
        self.area.add_widget(fb)

    def _resultado(self):
        self.area.clear_widgets()
        pct = (self.acertos / len(self.perguntas) * 100) if self.perguntas else 0
        self.area.add_widget(Label(text="🏆 Resultado Final", size_hint_y=None,
                                   height=40, font_size="18sp", bold=True,
                                   color=COR["texto"]))
        self.area.add_widget(Label(text=f"{self.acertos}/{len(self.perguntas)} corretas",
                                   size_hint_y=None, height=30, font_size="14sp",
                                   color=COR["texto2"]))
        self.area.add_widget(Label(text=f"{pct:.0f}%", size_hint_y=None, height=50,
                                   font_size="32sp", bold=True,
                                   color=COR["primaria"]))
        btn_novo = Button(text="Novo Quiz", size_hint_y=None, height=50,
                         background_color=COR["primaria"])
        btn_novo.bind(on_press=lambda _: self.app.ir_para("quiz"))
        self.area.add_widget(btn_novo)

# ─────────────────────────────────────────────
# DIAGNÓSTICO
# ─────────────────────────────────────────────
class TelaDiagnostico(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.casos = carregar_casos()
        self.respondido = False
        self.bg_color = COR["fundo"]

        header = BoxLayout(size_hint_y=None, height=50, bg_color=COR["indicador"],
                          padding=12, spacing=8)
        btn_voltar = Button(text="←", size_hint_x=None, width=50,
                           background_color=COR["indicador"],
                           on_press=lambda _: self.app.ir_para("inicio"))
        header.add_widget(btn_voltar)
        header.add_widget(Label(text="🩺 Diagnóstico", font_size="16sp",
                               color=COR["branco"], bold=True))
        self.add_widget(header)

        scroll = ScrollView()
        container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=12)
        container.bind(minimum_height=container.setter('height'))

        for i, caso in enumerate(self.casos, 1):
            btn = Button(text=f"Caso {i}: {caso['titulo']}\n{caso['historia'][:60]}...",
                        size_hint_y=None, height=90, background_color=COR["superficie"],
                        color=COR["texto"], font_size="11sp")
            btn.bind(on_press=lambda _, c=caso: self._abrir(c))
            container.add_widget(btn)

        scroll.add_widget(container)
        self.add_widget(scroll)

    def _abrir(self, caso):
        content = BoxLayout(orientation='vertical', padding=10, spacing=8)

        scroll = ScrollView()
        inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=10)
        inner.bind(minimum_height=inner.setter('height'))

        inner.add_widget(Label(text=caso["titulo"], size_hint_y=None, height=25,
                              bold=True, font_size="14sp", color=COR["texto"]))
        inner.add_widget(Label(text=caso["historia"], size_hint_y=None, height=80,
                              font_size="11sp", text_size=(350, None),
                              color=COR["texto"]))

        inner.add_widget(Label(text="Exames:", size_hint_y=None, height=15,
                              bold=True, font_size="10sp", color=COR["texto2"]))
        for nome, dados in caso["exames"].items():
            val = dados["valor"]
            if val > dados["ref_max"]:
                status, cor = "⬆ ALTO", COR["erro"]
            elif val < dados["ref_min"]:
                status, cor = "⬇ BAIXO", COR["cobalto"]
            else:
                status, cor = "✓ NORMAL", COR["sucesso"]
            inner.add_widget(Label(text=f"{nome}: {val} {status}",
                                  size_hint_y=None, height=20, font_size="10sp",
                                  color=cor))

        inner.add_widget(Label(text="Diagnóstico?", size_hint_y=None, height=20,
                              bold=True, font_size="11sp", color=COR["texto"]))

        self.diag_buttons = []
        alts = caso["alternativas"][:]
        random.shuffle(alts)
        for alt in alts:
            btn = Button(text=alt, size_hint_y=None, height=50,
                        background_color=COR["superficie"],
                        color=COR["texto"], font_size="10sp")
            def verif(_, a=alt, c=caso):
                self._verificar(a, c)
            btn.bind(on_press=verif)
            inner.add_widget(btn)
            self.diag_buttons.append(btn)

        scroll.add_widget(inner)
        content.add_widget(scroll)

        footer = BoxLayout(size_hint_y=0.1, padding=10)
        btn_fechar = Button(text="Fechar", background_color=COR["texto2"])
        footer.add_widget(btn_fechar)
        content.add_widget(footer)

        self.popup = Popup(title="Caso Clínico", content=content, size_hint=(0.95, 0.9))
        btn_fechar.bind(on_press=self.popup.dismiss)
        self.popup.open()

    def _verificar(self, escolha, caso):
        correto = escolha == caso["resposta_correta"]

        if correto:
            self.app.xp += 25
            self.app.streak += 1
        else:
            self.app.streak = 0

        for btn in self.diag_buttons:
            btn.disabled = True

        from kivy.uix.boxlayout import BoxLayout as BL
        from kivy.uix.label import Label as Lbl
        fb = BL(orientation='vertical', size_hint_y=None, height=120, padding=10, spacing=8)
        titulo = "✅ Correto!" if correto else "❌ Errado"
        cor = COR["sucesso"] if correto else COR["erro"]
        fb.add_widget(Lbl(text=titulo, size_hint_y=None, height=25, font_size="13sp",
                         bold=True, color=cor))
        if not correto:
            fb.add_widget(Lbl(text=f"Resposta: {caso['resposta_correta']}",
                             size_hint_y=None, height=20, font_size="10sp",
                             color=COR["sucesso"]))
        fb.add_widget(Lbl(text=caso["explicacao"][:100], size_hint_y=None, height=75,
                         font_size="9sp", text_size=(330, None),
                         color=COR["texto"]))

        from kivy.uix.button import Button as Btn
        btn_ok = Btn(text="OK", size_hint_y=None, height=40, background_color=COR["primaria"])
        btn_ok.bind(on_press=self.popup.dismiss)
        fb.add_widget(btn_ok)

        self.popup.content.add_widget(fb)

# ─────────────────────────────────────────────
# TUTOR IA (Chat offline)
# ─────────────────────────────────────────────
class TelaTutor(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.bg_color = COR["fundo"]
        self.marcadores = carregar_marcadores()

        header = BoxLayout(size_hint_y=None, height=50, bg_color=COR["sangue"],
                          padding=12, spacing=8)
        btn_voltar = Button(text="←", size_hint_x=None, width=50,
                           background_color=COR["sangue"],
                           on_press=lambda _: self.app.ir_para("inicio"))
        header.add_widget(btn_voltar)
        header.add_widget(Label(text="💬 Tutor IA", font_size="16sp",
                               color=COR["branco"], bold=True))
        self.add_widget(header)

        scroll = ScrollView()
        self.chat_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=10)
        self.chat_box.bind(minimum_height=self.chat_box.setter('height'))
        scroll.add_widget(self.chat_box)
        self.add_widget(scroll)

        input_box = BoxLayout(size_hint_y=None, height=60, spacing=8, padding=10)
        self.input = TextInput(text="", multiline=False, hint_text="Pergunte ao tutor...",
                              background_color=COR["superficie"])
        input_box.add_widget(self.input)
        btn_enviar = Button(text="→", size_hint_x=None, width=50,
                           background_color=COR["sangue"])
        btn_enviar.bind(on_press=lambda _: self._enviar())
        input_box.add_widget(btn_enviar)
        self.add_widget(input_box)

        self._msg_inicial()

    def _msg_inicial(self):
        msg = Label(text="🤖 Olá! Sou seu tutor IA. Pergunta-me sobre marcadores bioquímicos.",
                   size_hint_y=None, height=60, font_size="11sp",
                   text_size=(400, None), color=COR["cobalto"])
        self.chat_box.add_widget(msg)

    def _enviar(self):
        pergunta = self.input.text.strip()
        if not pergunta:
            return

        self.input.text = ""

        # Mostra pergunta
        msg_user = Label(text=f"👤 {pergunta}", size_hint_y=None, height=60,
                        font_size="11sp", text_size=(400, None),
                        color=COR["texto"])
        self.chat_box.add_widget(msg_user)

        # Gera resposta offline (simples pattern matching)
        resposta = self._gerar_resposta(pergunta)

        # Mostra resposta
        msg_bot = Label(text=f"🤖 {resposta}", size_hint_y=None, height=80,
                       font_size="11sp", text_size=(400, None),
                       color=COR["cobalto"])
        self.chat_box.add_widget(msg_bot)

    def _gerar_resposta(self, pergunta):
        pergunta_lower = pergunta.lower()

        # Busca marcador mencionado
        for m in self.marcadores:
            if m["sigla"].lower() in pergunta_lower or m["nome"].lower() in pergunta_lower:
                return f"{m['nome']} ({m['sigla']}):\nReferência: {m['valor_ref_min']}-{m['valor_ref_max']} {m['unidade']}\nElevado indica: {m['interpretacao_alta'][:100]}..."

        # Respostas genéricas
        respostas = {
            "oi": "Olá! Posso ajudar com informações sobre marcadores bioquímicos.",
            "ajuda": "Pergunte sobre qualquer marcador (ALT, AST, Glicose, etc) e te darei as informações clínicas.",
            "obrigado": "De nada! Continue estudando! 📚",
            "oi": "Olá! Como posso ajudar no seu estudo de bioquímica?",
        }

        for palavra, resp in respostas.items():
            if palavra in pergunta_lower:
                return resp

        return "Pergunta sobre um marcador específico (ex: ALT, Glicose, Potássio) para receber mais informações!"

# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────
class BioquimicaApp(App):
    def build(self):
        Window.size = (480, 960)
        self.xp = 0
        self.streak = 0
        self.container = BoxLayout()
        self.ir_para("inicio")
        return self.container

    def ir_para(self, modo):
        self.container.clear_widgets()

        telas = {
            "inicio": TelaInicial(self),
            "estudo": TelaEstudo(self),
            "flashcards": TelaFlashcards(self),
            "quiz": TelaQuiz(self),
            "diagnostico": TelaDiagnostico(self),
            "tutor": TelaTutor(self),
        }

        self.container.add_widget(telas.get(modo, TelaInicial(self)))

if __name__ == "__main__":
    BioquimicaApp().run()
