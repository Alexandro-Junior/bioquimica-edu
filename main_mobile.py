"""
BioquímicaEDU — App Mobile (Kivy)
Versão otimizada para iOS/Android
Paleta: reagentes da bioquímica (verde-enzima, vermelho-heme, âmbar-bile, violeta-indicador, azul-biureto)
"""

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window
from kivy.uix.progressbar import ProgressBar
from kivy.uix.togglebutton import ToggleButton

import json, csv, random
from pathlib import Path

kivy.require('2.0')
Window.size = (480, 960)  # mobile portrait

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# ─────────────────────────────────────────────
# CORES — Reagentes da Bioquímica
# ─────────────────────────────────────────────
COR = {
    "fundo":           (0.98, 0.96, 0.93, 1),     # #FAF6EE
    "superficie":      (1.0, 1.0, 1.0, 1),
    "topo":            (1.0, 1.0, 1.0, 1),

    "primaria":        (0.086, 0.639, 0.290, 1), # #16A34A verde-enzima
    "primaria_dark":   (0.083, 0.502, 0.243, 1), # #15803D
    "primaria_light":  (0.861, 0.988, 0.906, 1), # #DCFCE7

    "sangue":          (0.882, 0.114, 0.282, 1), # #E11D48
    "sangue_dark":     (0.624, 0.071, 0.227, 1), # #9F1239
    "sangue_light":    (1.0, 0.898, 0.902, 1),   # #FFE4E6

    "bile":            (0.961, 0.620, 0.063, 1), # #F59E0B
    "bile_dark":       (0.706, 0.325, 0.039, 1), # #B45309
    "bile_light":      (0.996, 0.949, 0.780, 1), # #FEF3C7

    "indicador":       (0.486, 0.231, 0.929, 1), # #7C3AED
    "indicador_dark":  (0.357, 0.133, 0.714, 1), # #5B21B6
    "indicador_light": (0.933, 0.914, 0.996, 1), # #EDE9FE

    "cobalto":         (0.118, 0.533, 0.690, 1), # #1E88B0
    "cobalto_dark":    (0.055, 0.361, 0.478, 1), # #0E5C7A
    "cobalto_light":   (0.812, 0.980, 0.996, 1), # #CFFAFE

    "texto":           (0.122, 0.165, 0.216, 1), # #1F2937
    "texto2":          (0.420, 0.447, 0.502, 1), # #6B7280
    "texto3":          (0.612, 0.639, 0.686, 1), # #9CA3AF

    "borda":           (0.898, 0.906, 0.933, 1), # #E5E7EB
    "borda_forte":     (0.820, 0.835, 0.855, 1), # #D1D5DB

    "sucesso":         (0.086, 0.639, 0.290, 1), # #16A34A
    "sucesso_dark":    (0.083, 0.502, 0.243, 1), # #15803D
    "sucesso_light":   (0.861, 0.988, 0.906, 1), # #DCFCE7
    "erro":            (0.863, 0.149, 0.149, 1), # #DC2626
    "erro_dark":       (0.600, 0.106, 0.106, 1), # #991B1B
    "erro_light":      (0.996, 0.886, 0.886, 1), # #FEE2E2

    "categoria": {
        "Hepático":   (0.961, 0.620, 0.063, 1),
        "Renal":      (0.024, 0.714, 0.831, 1),
        "Glicêmico":  (0.086, 0.639, 0.290, 1),
        "Lipídico":   (0.533, 0.361, 0.961, 1),
        "Eletrólito": (0.231, 0.510, 0.961, 1),
        "Cardíaco":   (0.882, 0.114, 0.282, 1),
    },
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
# HELPERS UI
# ─────────────────────────────────────────────
def btn_primario(texto, on_press, **kwargs):
    """Botão grande verde (primário)"""
    return Button(
        text=texto,
        size_hint_y=None,
        height=56,
        background_color=COR["primaria"],
        color=COR["texto"],
        bold=True,
        font_size="16sp",
        on_press=on_press,
        **kwargs
    )


def btn_secundario(texto, on_press, **kwargs):
    """Botão secundário (cinza)"""
    return Button(
        text=texto,
        size_hint_y=None,
        height=56,
        background_color=COR["borda"],
        color=COR["texto"],
        bold=True,
        font_size="15sp",
        on_press=on_press,
        **kwargs
    )


def titulo_secao(texto, cor=None):
    """Label de seção/cabeçalho"""
    return Label(
        text=texto,
        size_hint_y=None,
        height=32,
        color=cor or COR["texto"],
        bold=True,
        font_size="18sp",
    )


# ─────────────────────────────────────────────
# TELA INICIAL
# ─────────────────────────────────────────────
class TelaInicial(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.bg_color = COR["fundo"]
        self.spacing = 0
        self.padding = 0

        # Cabeçalho
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=180,
            bg_color=COR["primaria"],
            padding=20,
            spacing=8,
        )
        lbl_titulo = Label(
            text="⚗  BioquímicaEDU",
            size_hint_y=None,
            height=50,
            color=COR["branco"],
            bold=True,
            font_size="24sp",
        )
        header.add_widget(lbl_titulo)

        lbl_sub = Label(
            text="Aprenda bioquímica clínica em jornada",
            size_hint_y=None,
            height=40,
            color=(1, 1, 1, 0.85),
            font_size="13sp",
        )
        header.add_widget(lbl_sub)

        gamif = BoxLayout(size_hint_y=None, height=40, spacing=12)
        gamif.add_widget(Label(text=f"🔥 {self.app.streak}", font_size="14sp"))
        gamif.add_widget(Label(text=f"⚡ {self.app.xp} XP", font_size="14sp"))
        header.add_widget(gamif)
        self.add_widget(header)

        # Conteúdo
        scroll = ScrollView()
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=16,
            padding=16,
        )
        container.bind(minimum_height=container.setter('height'))

        # Lição 1: Modo Estudo
        c1 = BoxLayout(orientation='vertical', size_hint_y=None, height=160,
                       bg_color=COR["primaria_light"], padding=14, spacing=8)
        c1.add_widget(Label(text="📚  Modo Estudo",
                            size_hint_y=None, height=30,
                            color=COR["primaria_dark"],
                            bold=True, font_size="16sp"))
        c1.add_widget(Label(text="Explore 20 marcadores e suas\ninterpretações clínicas",
                            size_hint_y=None, height=50,
                            color=COR["texto2"],
                            font_size="13sp"))
        c1.add_widget(btn_primario("Iniciar +10 XP",
                                   lambda _: self.app.ir_para("estudo")))
        container.add_widget(c1)

        # Lição 2: Quiz
        c2 = BoxLayout(orientation='vertical', size_hint_y=None, height=160,
                       bg_color=COR["cobalto_light"], padding=14, spacing=8)
        c2.add_widget(Label(text="🧠  Quiz Rápido",
                            size_hint_y=None, height=30,
                            color=COR["cobalto_dark"],
                            bold=True, font_size="16sp"))
        c2.add_widget(Label(text="Teste conhecimentos com\nperguntas embaralhadas",
                            size_hint_y=None, height=50,
                            color=COR["texto2"],
                            font_size="13sp"))
        c2.add_widget(btn_primario("Iniciar +10 XP",
                                   lambda _: self.app.ir_para("quiz")))
        container.add_widget(c2)

        # Lição 3: Diagnóstico
        c3 = BoxLayout(orientation='vertical', size_hint_y=None, height=160,
                       bg_color=COR["indicador_light"], padding=14, spacing=8)
        c3.add_widget(Label(text="🩺  Diagnóstico Simulado",
                            size_hint_y=None, height=30,
                            color=COR["indicador_dark"],
                            bold=True, font_size="16sp"))
        c3.add_widget(Label(text="Analise exames e chegue\nao diagnóstico correto",
                            size_hint_y=None, height=50,
                            color=COR["texto2"],
                            font_size="13sp"))
        c3.add_widget(btn_primario("Iniciar +25 XP",
                                   lambda _: self.app.ir_para("diagnostico")))
        container.add_widget(c3)

        scroll.add_widget(container)
        self.add_widget(scroll)


# ─────────────────────────────────────────────
# MODO ESTUDO
# ─────────────────────────────────────────────
class TelaEstudo(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.marcadores = carregar_marcadores()
        self.categorias = sorted(set(m["categoria"] for m in self.marcadores))
        self.cat_atual = "Todas"
        self.busca = ""
        self.bg_color = COR["fundo"]

        # Cabeçalho
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60,
                           bg_color=COR["topo"], padding=12, spacing=8)
        btn_voltar = Button(text="✕", size_hint_x=None, width=50,
                            background_color=COR["topo"],
                            color=COR["texto"],
                            on_press=lambda _: app.ir_para("inicio"))
        header.add_widget(btn_voltar)
        header.add_widget(Label(text="📚  Modo Estudo", color=COR["texto"],
                               bold=True, font_size="16sp"))
        self.add_widget(header)

        # Busca
        self.busca_input = TextInput(
            text="", multiline=False,
            size_hint_y=None, height=44,
            hint_text="🔍  Buscar marcador...",
            background_color=COR["trilha"] if hasattr(COR, "trilha") else COR["borda"],
        )
        self.busca_input.bind(text=lambda *_: self._filtrar())
        self.add_widget(self.busca_input)

        # Chips de categoria (scroll horizontal simulado com grid)
        chips_box = BoxLayout(size_hint_y=None, height=50, padding=12, spacing=8)
        scroll_chips = ScrollView(size_hint=(1, None), size=(400, 50))
        chips_grid = GridLayout(cols=10, size_hint_x=None, spacing=6)
        chips_grid.bind(minimum_width=chips_grid.setter('width'))

        for cat in ["Todas"] + self.categorias:
            btn = ToggleButton(text=cat, size_hint_x=None, width=80,
                               height=40, font_size="11sp")
            btn.bind(state=lambda b, c=cat: self._sel_categoria(c, b))
            chips_grid.add_widget(btn)

        scroll_chips.add_widget(chips_grid)
        chips_box.add_widget(scroll_chips)
        self.add_widget(chips_box)

        # Lista de marcadores
        scroll = ScrollView()
        self.lista_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=6,
            padding=12,
        )
        self.lista_container.bind(minimum_height=self.lista_container.setter('height'))
        scroll.add_widget(self.lista_container)
        self.add_widget(scroll)

        self._filtrar()

    def _sel_categoria(self, cat, btn):
        if btn.state == "down":
            self.cat_atual = cat
            self._filtrar()

    def _filtrar(self):
        busca = self.busca_input.text.lower()
        filtrados = [
            m for m in self.marcadores
            if (self.cat_atual == "Todas" or m["categoria"] == self.cat_atual)
            and (busca in m["nome"].lower() or busca in m["sigla"].lower())
        ]
        self.lista_container.clear_widgets()
        for m in filtrados:
            self.lista_container.add_widget(
                self._card_marcador(m)
            )

    def _card_marcador(self, m):
        cor_cat = COR["categoria"].get(m["categoria"], COR["primaria"])
        card = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=70,
            bg_color=COR["superficie"],
            padding=10,
            spacing=10,
        )
        # Bolinha colorida
        dot = Label(
            text="●", size_hint_x=None, width=20,
            color=cor_cat, font_size="18sp"
        )
        card.add_widget(dot)

        # Info
        info = BoxLayout(orientation='vertical', spacing=2)
        info.add_widget(Label(text=m["nome"], color=COR["texto"],
                             bold=True, font_size="13sp"))
        info.add_widget(Label(text=f"{m['sigla']}  ·  {m['categoria']}",
                             color=COR["texto2"], font_size="11sp"))
        card.add_widget(info)

        # Click -> detalhe
        card.bind(on_press=lambda _: self.app.mostrar_detalhe(m))
        card.bind(size=lambda *_: setattr(card, 'pos', card.pos))
        return card

    def mostrar_detalhe(self, m):
        """Popup com detalhe do marcador"""
        cor_cat = COR["categoria"].get(m["categoria"], COR["primaria"])

        content = BoxLayout(orientation='vertical', padding=12, spacing=8)
        scroll = ScrollView()
        inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12)
        inner.bind(minimum_height=inner.setter('height'))

        # Cabeçalho
        header = BoxLayout(
            orientation='vertical', size_hint_y=None, height=100,
            bg_color=cor_cat, padding=12, spacing=6
        )
        header.add_widget(Label(
            text=m["categoria"].upper(), color=COR["branco"],
            font_size="10sp", bold=True, size_hint_y=None, height=20
        ))
        header.add_widget(Label(
            text=m["nome"], color=COR["branco"],
            font_size="18sp", bold=True, size_hint_y=None, height=40
        ))
        header.add_widget(Label(
            text=f"Sigla {m['sigla']}", color=COR["branco"],
            font_size="11sp", size_hint_y=None, height=20
        ))
        inner.add_widget(header)

        # Valor de referência
        ref_card = BoxLayout(orientation='vertical', size_hint_y=None, height=80,
                            bg_color=COR["superficie"], padding=12, spacing=4)
        ref_card.add_widget(Label(
            text="VALOR DE REFERÊNCIA", color=COR["texto3"],
            font_size="10sp", bold=True, size_hint_y=None, height=16
        ))
        ref_card.add_widget(Label(
            text=f"{m['valor_ref_min']} – {m['valor_ref_max']} {m['unidade']}",
            color=cor_cat, font_size="16sp", bold=True,
            size_hint_y=None, height=30
        ))
        inner.add_widget(ref_card)

        # Interpretações
        for titulo, texto in [
            ("⬆ QUANDO ELEVADO", m["interpretacao_alta"]),
            ("⬇ QUANDO BAIXO", m["interpretacao_baixa"]),
        ]:
            interp = BoxLayout(orientation='vertical', size_hint_y=None,
                              bg_color=COR["superficie"], padding=12, spacing=4)
            interp.size_hint_y = None
            interp.add_widget(Label(text=titulo, color=COR["texto"],
                                   font_size="12sp", bold=True,
                                   size_hint_y=None, height=24))
            interp.add_widget(Label(text=texto, color=COR["texto2"],
                                   font_size="11sp", size_hint_y=None,
                                   height=100))
            interp.height = 124
            inner.add_widget(interp)

        # Doenças associadas
        if m["doencas_associadas_alta"] and m["doencas_associadas_alta"] != "—":
            doencas = BoxLayout(orientation='vertical', size_hint_y=None,
                               bg_color=COR["erro_light"], padding=12, spacing=4)
            doencas.add_widget(Label(text="Doenças — Valor ALTO",
                                    color=COR["erro_dark"],
                                    font_size="11sp", bold=True,
                                    size_hint_y=None, height=20))
            for d in m["doencas_associadas_alta"].split(","):
                d = d.strip()
                if d and d != "—":
                    doencas.add_widget(Label(text=f"• {d}",
                                            color=COR["texto"],
                                            font_size="10sp",
                                            size_hint_y=None, height=24))
            doencas.height = 20 + len(m["doencas_associadas_alta"].split(",")) * 24
            inner.add_widget(doencas)

        scroll.add_widget(inner)
        content.add_widget(scroll)
        content.add_widget(btn_secundario("Voltar",
                                         lambda _: popup.dismiss()))

        popup = Popup(
            title=m["nome"],
            content=content,
            size_hint=(1, 0.95),
        )
        popup.open()


# ─────────────────────────────────────────────
# MODO QUIZ
# ─────────────────────────────────────────────
class TelaQuiz(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.perguntas = carregar_quiz()
        self.perguntas_embaralhadas = []
        self.indice = 0
        self.acertos = 0
        self.respondido = False
        self.escolha = None
        self.total = 0
        self.bg_color = COR["fundo"]

        # Cabeçalho
        header = BoxLayout(orientation='horizontal', size_hint_y=None,
                          height=60, bg_color=COR["topo"], padding=12, spacing=8)
        btn_voltar = Button(text="✕", size_hint_x=None, width=50,
                           background_color=COR["topo"],
                           color=COR["texto"],
                           on_press=lambda _: app.ir_para("inicio"))
        header.add_widget(btn_voltar)
        header.add_widget(Label(text="🧠  Quiz", color=COR["texto"],
                               bold=True, font_size="16sp"))
        self.add_widget(header)

        # Container principal
        self.main_container = BoxLayout(orientation='vertical', padding=16, spacing=12)
        self.add_widget(self.main_container)

        self._tela_config()

    def _tela_config(self):
        self.main_container.clear_widgets()

        titulo = Label(
            text="Quantas perguntas?",
            size_hint_y=None, height=50,
            color=COR["texto"], bold=True, font_size="18sp"
        )
        self.main_container.add_widget(titulo)

        opcoes = [5, 8, 10, 12] if len(self.perguntas) >= 12 else \
                 list(range(3, len(self.perguntas) + 1))

        self.num_perguntas = opcoes[0]
        grid_ops = GridLayout(cols=2, size_hint_y=None, height=120, spacing=8)
        for n in opcoes:
            def set_num(_, val=n):
                self.num_perguntas = val
            btn = Button(text=str(n), font_size="16sp",
                        background_color=COR["cobalto_light"],
                        color=COR["cobalto"])
            btn.bind(on_press=set_num)
            grid_ops.add_widget(btn)
        self.main_container.add_widget(grid_ops)

        self.main_container.add_widget(Label(size_hint_y=1))
        self.main_container.add_widget(
            btn_primario("Iniciar Quiz", lambda _: self._iniciar())
        )

    def _iniciar(self):
        self.perguntas_embaralhadas = random.sample(
            self.perguntas, min(self.num_perguntas, len(self.perguntas))
        )
        self.total = len(self.perguntas_embaralhadas)
        self.indice = 0
        self.acertos = 0
        self._mostrar_pergunta()

    def _mostrar_pergunta(self):
        if self.indice >= self.total:
            self._resultado()
            return

        self.respondido = False
        self.escolha = None
        p = self.perguntas_embaralhadas[self.indice]
        cor_cat = COR["categoria"].get(p.get("categoria", ""), COR["cobalto"])

        self.main_container.clear_widgets()

        # Progresso
        pct = self.indice / self.total if self.total > 0 else 0
        prog = BoxLayout(size_hint_y=None, height=50, spacing=8, padding=12)
        prog_bar = ProgressBar(max=self.total, value=self.indice + 1,
                               size_hint_y=None, height=8)
        prog.add_widget(prog_bar)
        prog.add_widget(Label(text=f"{self.indice+1}/{self.total}",
                             size_hint_x=None, width=60,
                             color=COR["texto2"], font_size="12sp"))
        self.main_container.add_widget(prog)

        # Categoria
        cat_chip = Label(
            text=f"  {p.get('categoria', '—').upper()}  ",
            size_hint_y=None, height=28,
            color=COR["branco"],
            bold=True, font_size="11sp",
            background_color=cor_cat,
        )
        self.main_container.add_widget(cat_chip)

        # Pergunta
        self.main_container.add_widget(Label(
            text=p["pergunta"],
            size_hint_y=None, height=100,
            color=COR["texto"],
            bold=True, font_size="16sp",
            text_size=(400, None),
        ))

        # Alternativas
        scroll = ScrollView()
        alt_container = BoxLayout(
            orientation='vertical', size_hint_y=None, spacing=8
        )
        alt_container.bind(minimum_height=alt_container.setter('height'))

        self._alt_botoes = []
        for i, texto in enumerate(p["alternativas"]):
            def sel(_, i_=i):
                if not self.respondido:
                    self.escolha = i_
                    self._refresh_alternativas()
            btn = Button(
                text=f"{chr(65+i)}) {texto}",
                size_hint_y=None, height=70,
                background_color=COR["borda"],
                color=COR["texto"],
                font_size="13sp",
                on_press=sel,
            )
            alt_container.add_widget(btn)
            self._alt_botoes.append(btn)

        scroll.add_widget(alt_container)
        self.main_container.add_widget(scroll)

        # Botão verificar
        self._btn_verificar = btn_primario(
            "Verificar", lambda _: self._verificar(p)
        )
        self._btn_verificar.disabled = True
        self.main_container.add_widget(self._btn_verificar)

    def _refresh_alternativas(self):
        for i, btn in enumerate(self._alt_botoes):
            if i == self.escolha:
                btn.background_color = COR["cobalto"]
                btn.color = COR["branco"]
            else:
                btn.background_color = COR["borda"]
                btn.color = COR["texto"]
        self._btn_verificar.disabled = False

    def _verificar(self, p):
        if self.escolha is None or self.respondido:
            return
        self.respondido = True
        correto = p["resposta_correta"]
        acertou = (self.escolha == correto)

        # Colorir
        for i, btn in enumerate(self._alt_botoes):
            if i == correto:
                btn.background_color = COR["sucesso"]
                btn.disabled = True
            elif i == self.escolha and not acertou:
                btn.background_color = COR["erro"]
                btn.disabled = True

        if acertou:
            self.acertos += 1
            self.app.xp += 10
            self.app.streak += 1
        else:
            self.app.streak = 0

        # Feedback
        self.main_container.add_widget(Label(
            text="✅ Correto!" if acertou else "❌ Errado",
            size_hint_y=None, height=40,
            color=COR["sucesso_dark"] if acertou else COR["erro_dark"],
            bold=True, font_size="16sp",
        ))
        self.main_container.add_widget(Label(
            text=p["explicacao"],
            size_hint_y=None, height=80,
            color=COR["texto"],
            font_size="12sp",
            text_size=(400, None),
        ))

        self.indice += 1
        label = "Continuar" if self.indice < self.total else "Resultado"
        self.main_container.add_widget(
            btn_primario(label, lambda _: self._mostrar_pergunta())
        )

    def _resultado(self):
        pct = (self.acertos / self.total * 100) if self.total else 0
        if pct >= 80:
            emoji, msg = "🏆", "Excelente! Você domina."
        elif pct >= 60:
            emoji, msg = "👍", "Bom resultado — revise os erros."
        else:
            emoji, msg = "📖", "Continue estudando."

        self.main_container.clear_widgets()
        self.main_container.add_widget(Label(
            text=emoji,
            size_hint_y=None, height=60,
            font_size="48sp",
        ))
        self.main_container.add_widget(Label(
            text="Lição concluída!",
            size_hint_y=None, height=50,
            color=COR["texto"],
            bold=True, font_size="20sp",
        ))
        self.main_container.add_widget(Label(
            text=f"{self.acertos}/{self.total} corretas",
            size_hint_y=None, height=40,
            color=COR["texto2"],
            font_size="16sp",
        ))
        self.main_container.add_widget(Label(
            text=f"{pct:.0f}%",
            size_hint_y=None, height=60,
            color=COR["primaria"],
            bold=True, font_size="36sp",
        ))
        self.main_container.add_widget(Label(
            text=msg,
            size_hint_y=None, height=40,
            color=COR["texto2"],
            font_size="13sp",
        ))
        self.main_container.add_widget(Label(size_hint_y=1))
        self.main_container.add_widget(
            btn_primario("Nova lição", lambda _: self._tela_config())
        )
        self.main_container.add_widget(
            btn_secundario("Voltar", lambda _: self.app.ir_para("inicio"))
        )


# ─────────────────────────────────────────────
# MODO DIAGNÓSTICO
# ─────────────────────────────────────────────
class TelaDiagnostico(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.casos = carregar_casos()
        self.respondido = False
        self.bg_color = COR["fundo"]

        # Cabeçalho
        header = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=60,
            bg_color=COR["topo"], padding=12, spacing=8
        )
        btn_voltar = Button(
            text="✕", size_hint_x=None, width=50,
            background_color=COR["topo"], color=COR["texto"],
            on_press=lambda _: app.ir_para("inicio")
        )
        header.add_widget(btn_voltar)
        header.add_widget(Label(text="🩺  Diagnóstico",
                               color=COR["texto"],
                               bold=True, font_size="16sp"))
        self.add_widget(header)

        # Lista de casos
        scroll = ScrollView()
        self.casos_container = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=12, padding=16
        )
        self.casos_container.bind(
            minimum_height=self.casos_container.setter('height')
        )

        for i, caso in enumerate(self.casos):
            card = self._card_caso(caso, i + 1)
            self.casos_container.add_widget(card)

        scroll.add_widget(self.casos_container)
        self.add_widget(scroll)

    def _card_caso(self, caso, n):
        card = BoxLayout(
            orientation='vertical', size_hint_y=None, height=140,
            bg_color=COR["indicador_light"], padding=12, spacing=8
        )
        cab = BoxLayout(size_hint_y=None, height=30, spacing=8)
        num_canvas = Label(
            text=str(n), size_hint_x=None, width=30,
            color=COR["indicador_dark"],
            bold=True, font_size="16sp",
        )
        cab.add_widget(num_canvas)
        cab.add_widget(Label(text=caso["titulo"],
                            color=COR["texto"],
                            bold=True, font_size="14sp"))
        card.add_widget(cab)

        card.add_widget(Label(
            text=caso["historia"][:100] + "...",
            size_hint_y=None, height=35,
            color=COR["texto2"],
            font_size="11sp",
            text_size=(350, None),
        ))

        card.add_widget(btn_primario(
            "Analisar", lambda _, c=caso: self._abrir(c)
        ))
        return card

    def _abrir(self, caso):
        from kivy.uix.modalview import ModalView

        modal = ModalView(size_hint=(1, 0.95))
        content = BoxLayout(orientation='vertical', padding=12, spacing=8)
        scroll = ScrollView()
        inner = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=12, padding=12
        )
        inner.bind(minimum_height=inner.setter('height'))

        # Título
        inner.add_widget(Label(
            text=caso["titulo"],
            size_hint_y=None, height=40,
            color=COR["indicador_dark"],
            bold=True, font_size="16sp",
        ))

        # História
        inner.add_widget(Label(
            text="📋 História Clínica",
            size_hint_y=None, height=20,
            color=COR["texto3"],
            bold=True, font_size="11sp",
        ))
        inner.add_widget(Label(
            text=caso["historia"],
            size_hint_y=None, height=100,
            color=COR["texto"],
            font_size="11sp",
            text_size=(380, None),
        ))

        # Exames
        inner.add_widget(Label(
            text="🔬 Exames Laboratoriais",
            size_hint_y=None, height=20,
            color=COR["texto"],
            bold=True, font_size="12sp",
        ))

        for nome, dados in caso["exames"].items():
            val = dados["valor"]
            if val > dados["ref_max"]:
                status, cor = "ALTO", COR["erro"]
            elif val < dados["ref_min"]:
                status, cor = "BAIXO", COR["cobalto"]
            else:
                status, cor = "NORMAL", COR["sucesso"]

            exame = BoxLayout(
                orientation='vertical', size_hint_y=None, height=50,
                bg_color=cor, padding=8, spacing=2
            )
            exame.add_widget(Label(
                text=f"{nome} {val} {dados['unidade']}",
                color=COR["branco"],
                bold=True, font_size="11sp",
                size_hint_y=None, height=20,
            ))
            exame.add_widget(Label(
                text=f"Ref. {dados['ref_min']}–{dados['ref_max']} | {status}",
                color=COR["branco"],
                font_size="10sp",
                size_hint_y=None, height=16,
            ))
            inner.add_widget(exame)

        # Pergunta + alternativas
        inner.add_widget(Label(
            text="🩺 Diagnóstico mais provável?",
            size_hint_y=None, height=24,
            color=COR["texto"],
            bold=True, font_size="12sp",
        ))

        alts = caso["alternativas"][:]
        random.shuffle(alts)
        for alt in alts:
            def sel(_, a=alt):
                if not self.respondido:
                    self._resp_diag(a, caso, modal)
            btn = Button(
                text=alt, size_hint_y=None, height=50,
                background_color=COR["borda"],
                color=COR["texto"],
                font_size="12sp",
                on_press=sel,
            )
            inner.add_widget(btn)

        scroll.add_widget(inner)
        content.add_widget(scroll)
        content.add_widget(btn_secundario("Voltar", lambda _: modal.dismiss()))

        modal.add_widget(content)
        modal.open()

    def _resp_diag(self, escolha, caso, modal):
        self.respondido = True
        correto = caso["resposta_correta"]
        acertou = (escolha == correto)

        if acertou:
            self.app.xp += 25
            self.app.streak += 1
        else:
            self.app.streak = 0

        # Feedback popup
        from kivy.uix.modalview import ModalView
        fb = ModalView(size_hint=(0.9, 0.6))
        content = BoxLayout(orientation='vertical', padding=20, spacing=12)
        content.add_widget(Label(
            text="✅ Diagnóstico correto!" if acertou else "❌ Diagnóstico incorreto",
            size_hint_y=None, height=40,
            color=COR["sucesso_dark"] if acertou else COR["erro_dark"],
            bold=True, font_size="16sp",
        ))
        if not acertou:
            content.add_widget(Label(
                text=f"Resposta: {correto}",
                size_hint_y=None, height=30,
                color=COR["texto"],
                font_size="12sp",
            ))
        content.add_widget(Label(
            text=caso["explicacao"],
            size_hint_y=None, height=100,
            color=COR["texto2"],
            font_size="11sp",
            text_size=(280, None),
        ))
        content.add_widget(Label(size_hint_y=1))
        content.add_widget(btn_primario("OK", lambda _: (fb.dismiss(), modal.dismiss())))

        fb.add_widget(content)
        fb.open()


# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────
class BioquimicaEDU(App):
    def build(self):
        Window.size = (480, 960)
        self.xp = 0
        self.streak = 0
        self.telas = {}
        self.container = RelativeLayout()
        self.ir_para("inicio")
        return self.container

    def ir_para(self, nome):
        # Limpar container
        self.container.clear_widgets()

        # Criar tela
        if nome == "inicio":
            tela = TelaInicial(self)
        elif nome == "estudo":
            tela = TelaEstudo(self)
        elif nome == "quiz":
            tela = TelaQuiz(self)
        elif nome == "diagnostico":
            tela = TelaDiagnostico(self)
        else:
            return

        self.container.add_widget(tela)
        self.telas[nome] = tela


if __name__ == "__main__":
    BioquimicaEDU().run()
