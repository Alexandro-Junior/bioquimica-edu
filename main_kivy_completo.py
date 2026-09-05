"""
BioquímicaEDU — Versão Mobile (Kivy)
Android / iOS — 5 modos de estudo

- Estudo: 20 marcadores, com abas Info / Fontes / Vídeos / Exemplos / Imagens
- Flashcards: cards que viram ao toque
- Quiz: perguntas de múltipla escolha com explicação
- Diagnóstico: casos clínicos com interpretação de exames
- Tutor: chat sobre marcadores (usa Ollama local se disponível, senão offline)

Executar:  python main_kivy_completo.py
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.properties import NumericProperty

import json
import csv
import random
import webbrowser
import threading
from pathlib import Path

Window.size = (480, 960)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMG_DIR = DATA_DIR / "images"

# ─────────────────────────────────────────────
# PALETA (inspirada em reagentes bioquímicos)
# ─────────────────────────────────────────────
COR = {
    "fundo":      (0.98, 0.96, 0.93, 1),
    "superficie": (1.00, 1.00, 1.00, 1),
    "primaria":   (0.086, 0.639, 0.290, 1),   # verde de Fehling
    "sangue":     (0.882, 0.114, 0.282, 1),   # vermelho do heme
    "bile":       (0.961, 0.620, 0.063, 1),   # âmbar biliar
    "cobalto":    (0.118, 0.533, 0.690, 1),   # azul de biureto
    "indicador":  (0.486, 0.231, 0.929, 1),   # violeta de fenolftaleína
    "texto":      (0.122, 0.165, 0.216, 1),
    "texto2":     (0.420, 0.447, 0.502, 1),
    "sucesso":    (0.086, 0.639, 0.290, 1),
    "erro":       (0.863, 0.149, 0.149, 1),
    "branco":     (1.00, 1.00, 1.00, 1),
    "borda":      (0.88, 0.86, 0.83, 1),
}

# Estágios de memória: progressão fria para quente conforme o item fixa
COR_ESTAGIO = {
    "novo":        (0.78, 0.81, 0.79, 1),
    "aprendendo":  (0.88, 0.64, 0.35, 1),
    "firmando":    (0.36, 0.61, 0.84, 1),
    "consolidado": (0.055, 0.486, 0.353, 1),
}

ROTULO_ESTAGIO = {
    "novo": "Nao estudados",
    "aprendendo": "Aprendendo",
    "firmando": "Firmando",
    "consolidado": "Consolidados",
}


# ─────────────────────────────────────────────
# WIDGETS DE APOIO
# ─────────────────────────────────────────────
class Painel(BoxLayout):
    """BoxLayout que realmente pinta um fundo colorido."""

    def __init__(self, cor=None, **kwargs):
        super().__init__(**kwargs)
        self._ret = None
        if cor is not None:
            with self.canvas.before:
                Color(*cor)
                self._ret = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self._redesenhar, size=self._redesenhar)

    def _redesenhar(self, *_):
        if self._ret is not None:
            self._ret.pos = self.pos
            self._ret.size = self.size


class Texto(Label):
    """Label que quebra linha e cresce em altura conforme o conteúdo."""

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "top")
        kwargs.setdefault("color", COR["texto"])
        kwargs.setdefault("font_size", "13sp")
        super().__init__(**kwargs)
        self.bind(width=self._ajustar_largura, texture_size=self._ajustar_altura)

    def _ajustar_largura(self, *_):
        self.text_size = (self.width, None)

    def _ajustar_altura(self, *_):
        self.height = self.texture_size[1]


class Botao(Button):
    """Botão com cor sólida (sem a textura cinza padrão do Kivy)."""

    def __init__(self, cor=None, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", cor or COR["primaria"])
        kwargs.setdefault("color", COR["branco"])
        kwargs.setdefault("font_size", "14sp")
        super().__init__(**kwargs)


class BotaoClaro(Botao):
    """Botão de listagem: fundo branco, texto escuro, alinhado à esquerda."""

    def __init__(self, **kwargs):
        kwargs.setdefault("cor", COR["superficie"])
        kwargs.setdefault("color", COR["texto"])
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)
        self.bind(size=self._ajustar)

    def _ajustar(self, *_):
        self.text_size = (self.width - dp(24), None)


class AnelDia(Widget):
    """Anel de progresso do dia: fração da fila já revisada.

    O número no centro é o que falta, não o total — é isso que o
    estudante precisa para decidir se começa agora.
    """

    fracao = NumericProperty(0.0)

    def __init__(self, restante=0, cor=None, **kwargs):
        super().__init__(**kwargs)
        self.restante = restante
        self.cor = cor or COR["primaria"]
        self.bind(pos=self._redesenhar, size=self._redesenhar, fracao=self._redesenhar)

    def animar(self, fracao, restante, cor=None):
        self.restante = restante
        self.cor = cor or COR["primaria"]
        self.fracao = 0.0
        Animation(fracao=max(0.0, min(1.0, fracao)),
                  duration=0.8, t="out_cubic").start(self)

    def _redesenhar(self, *_):
        self.canvas.clear()
        lado = min(self.width, self.height)
        if lado <= 1:
            return
        cx = self.center_x
        cy = self.center_y
        raio = lado / 2
        espessura = dp(9)

        with self.canvas:
            Color(*COR["borda"])
            Ellipse(pos=(cx - raio, cy - raio), size=(raio * 2, raio * 2))
            # angle_end=0 faria o Kivy desenhar a elipse inteira, então o
            # arco só entra quando há progresso de fato.
            if self.fracao > 0.002:
                Color(*self.cor)
                Ellipse(pos=(cx - raio, cy - raio), size=(raio * 2, raio * 2),
                        angle_start=0, angle_end=360 * self.fracao)
            Color(*COR["superficie"])
            r2 = raio - espessura
            Ellipse(pos=(cx - r2, cy - r2), size=(r2 * 2, r2 * 2))


class BarraEstagios(Widget):
    """Barra única dividida pelos quatro estágios de memória.

    Empilhada, e não quatro barras separadas: o que importa é a proporção
    entre estágios, e proporção se lê melhor num todo dividido.
    """

    avanco = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contagem = {}
        self.bind(pos=self._redesenhar, size=self._redesenhar,
                  avanco=self._redesenhar)

    def animar(self, contagem):
        self.contagem = contagem
        self.avanco = 0.0
        Animation(avanco=1.0, duration=0.75, t="out_cubic").start(self)

    def _redesenhar(self, *_):
        self.canvas.clear()
        if not self.contagem or self.width <= 1:
            return
        total = sum(self.contagem.values()) or 1
        x = self.x
        with self.canvas:
            Color(*COR["borda"])
            Rectangle(pos=self.pos, size=self.size)
            for chave in ("consolidado", "firmando", "aprendendo", "novo"):
                n = self.contagem.get(chave, 0)
                if not n:
                    continue
                w = (n / total) * self.width * self.avanco
                if w < 1:
                    continue
                Color(*COR_ESTAGIO[chave])
                Rectangle(pos=(x, self.y), size=(w, self.height))
                x += w


class BarraDominio(Widget):
    """Barra fina de domínio, usada por categoria."""

    avanco = NumericProperty(0.0)

    def __init__(self, valor=0.0, cor=None, **kwargs):
        super().__init__(**kwargs)
        self.valor = valor
        self.cor = cor or COR["primaria"]
        self.bind(pos=self._redesenhar, size=self._redesenhar,
                  avanco=self._redesenhar)

    def animar(self, valor, atraso=0.0):
        self.valor = max(0.0, min(1.0, valor))
        self.avanco = 0.0
        Animation(avanco=1.0, duration=0.7, t="out_cubic").start(self)

    def _redesenhar(self, *_):
        self.canvas.clear()
        if self.width <= 1:
            return
        with self.canvas:
            Color(*COR["borda"])
            Rectangle(pos=self.pos, size=self.size)
            Color(*self.cor)
            Rectangle(pos=self.pos,
                      size=(self.width * self.valor * self.avanco, self.height))


def cartao(cor=None, altura=None):
    """Superfície branca — a unidade visual do painel."""
    kw = {"orientation": "vertical", "padding": dp(14), "spacing": dp(6)}
    if altura is not None:
        kw["size_hint_y"] = None
        kw["height"] = altura
    return Painel(cor=cor or COR["superficie"], **kw)


def cabecalho(app, titulo, cor):
    """Barra superior com botão voltar."""
    barra = Painel(cor=cor, size_hint_y=None, height=dp(56),
                   padding=(dp(8), dp(6)), spacing=dp(4))
    voltar = Botao(text="<", cor=cor, size_hint_x=None, width=dp(44),
                   font_size="20sp", bold=True)
    voltar.bind(on_press=lambda _: app.ir_para("inicio"))
    barra.add_widget(voltar)
    barra.add_widget(Label(text=titulo, font_size="17sp",
                           color=COR["branco"], bold=True))
    return barra


def coluna_rolavel(padding=dp(12), spacing=dp(8), fundo=None):
    """Retorna (raiz, coluna) já ligados para conteúdo de altura variável.

    Se `fundo` for informado, a área rolável ganha esse fundo — necessário
    dentro de Popup, cujo fundo padrão é escuro e deixaria o texto ilegível.
    """
    scroll = ScrollView()
    coluna = BoxLayout(orientation="vertical", size_hint_y=None,
                       padding=padding, spacing=spacing)
    coluna.bind(minimum_height=coluna.setter("height"))
    scroll.add_widget(coluna)
    if fundo is None:
        return scroll, coluna
    moldura = Painel(cor=fundo)
    moldura.add_widget(scroll)
    return moldura, coluna


# ─────────────────────────────────────────────
# CARREGAMENTO DE DADOS
# ─────────────────────────────────────────────
def _ler_json(nome, default):
    try:
        with open(DATA_DIR / nome, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[dados] falha ao ler {nome}: {e}")
        return default


def carregar_marcadores():
    marcadores = []
    try:
        with open(DATA_DIR / "marcadores.csv", encoding="utf-8") as f:
            for linha in csv.DictReader(f):
                try:
                    linha["valor_ref_min"] = float(linha["valor_ref_min"])
                    linha["valor_ref_max"] = float(linha["valor_ref_max"])
                except (TypeError, ValueError):
                    continue
                marcadores.append(linha)
    except OSError as e:
        print(f"[dados] falha ao ler marcadores.csv: {e}")
    return marcadores


def carregar_flashcards():
    return _ler_json("flashcards.json", {}).get("flashcards", [])


def carregar_extras():
    dados = _ler_json("marcadores_extras.json", {})
    return {m["sigla"]: m for m in dados.get("marcadores_extras", [])}


def carregar_imagens():
    dados = _ler_json("marcadores_imagens.json", {})
    return {m["sigla"]: m for m in dados.get("marcadores_imagens", [])}


def carregar_quiz():
    return _ler_json("quiz_perguntas.json", [])


def carregar_casos():
    return _ler_json("casos_clinicos.json", [])


# ─────────────────────────────────────────────
# TELA INICIAL
# ─────────────────────────────────────────────
class TelaInicial(Painel):
    """Painel de estudo.

    Mesma lógica da versão desktop, adaptada à tela estreita: a decisão
    do dia ocupa a dobra inicial, e o contexto vem abaixo, por rolagem.
    """

    def __init__(self, app, **kwargs):
        super().__init__(cor=COR["fundo"], orientation="vertical", **kwargs)
        self.app = app
        self.siglas = [m["sigla"] for m in app.marcadores]
        self.categorias = {m["sigla"]: m["categoria"] for m in app.marcadores}
        self.nomes = {m["sigla"]: m["nome"] for m in app.marcadores}
        self.resumo = app.progresso.resumo(self.siglas, self.categorias)

        self._topo()
        scroll, coluna = coluna_rolavel(padding=dp(12), spacing=dp(10))
        self._cartao_hoje(coluna)
        self._cartao_memoria(coluna)
        self._cartao_focar(coluna)
        self._cartao_sistemas(coluna)
        self._modos(coluna)
        self.add_widget(scroll)

    def _topo(self):
        dias = self.resumo["sequencia"]
        seq = "primeiro dia" if dias <= 1 else f"{dias} dias seguidos"
        topo = Painel(cor=COR["superficie"], orientation="vertical",
                      size_hint_y=None, height=dp(74),
                      padding=(dp(14), dp(10)), spacing=dp(2))
        topo.add_widget(Label(text="BioquimicaEDU", size_hint_y=None, height=dp(30),
                              color=COR["texto"], bold=True, font_size="21sp",
                              halign="left", valign="middle",
                              text_size=(Window.width - dp(28), None)))
        topo.add_widget(Label(
            text=f"{seq}  ·  {self.resumo['revisados_hoje']} revisoes hoje",
            size_hint_y=None, height=dp(20), color=COR["texto2"],
            font_size="12sp", halign="left", valign="middle",
            text_size=(Window.width - dp(28), None)))
        self.add_widget(topo)

    # ── 1. hoje ─────────────────────────────────────────────────────
    def _cartao_hoje(self, coluna):
        fila = self.resumo["fila"]
        vencidos = self.resumo["vencidos"]
        reforco = self.resumo["reforco"]
        novos = self.resumo["novos"]
        feitos = self.resumo["revisados_hoje"]
        primeiro_uso = novos == len(self.siglas)

        cor_acao = COR["bile"] if vencidos else COR["primaria"]

        if primeiro_uso:
            titulo, acao = "Comece por aqui", "Estudar os primeiros"
            detalhe = (f"Sao {len(self.siglas)} marcadores. O app mostra poucos "
                       "por vez e traz cada um de volta pouco antes de voce esquecer.")
        elif reforco:
            titulo, acao = "Corrija o que errou hoje", "Retomar os que errei"
            detalhe = (f"{reforco} marcador(es) errados nesta sessao. Rever agora, "
                       "com o erro fresco, e o que fixa a correcao.")
        elif vencidos:
            titulo, acao = "Revisao de hoje pronta", "Comecar revisao"
            detalhe = (f"{vencidos} marcador(es) chegaram ao ponto de revisao, "
                       "no limite entre lembrar e esquecer.")
        elif fila:
            titulo, acao = "Revisoes em dia", "Aprender algo novo"
            detalhe = f"Nada vencido. Da para avancar em {min(len(fila), novos)} novo(s)."
        else:
            titulo, acao = "Tudo revisado", ""
            detalhe = ("Nenhum marcador venceu hoje. O app chama de volta quando "
                       "a memoria precisar.")

        c = cartao()
        c.size_hint_y = None
        c.bind(minimum_height=c.setter("height"))

        linha = BoxLayout(size_hint_y=None, height=dp(104), spacing=dp(12))
        anel = AnelDia(size_hint_x=None, width=dp(104))
        linha.add_widget(anel)

        lado = BoxLayout(orientation="vertical", spacing=dp(2))
        lado.add_widget(Texto(text=f"[b]{titulo}[/b]", markup=True, font_size="18sp"))
        lado.add_widget(Texto(text=detalhe, font_size="12sp", color=COR["texto2"]))
        linha.add_widget(lado)
        c.add_widget(linha)

        total = feitos + len(fila)
        fracao = (feitos / total) if total else 1.0
        Clock.schedule_once(
            lambda _: anel.animar(fracao, max(0, len(fila)), cor_acao), 0.15)
        Clock.schedule_once(
            lambda _: self._centro_anel(anel, len(fila)), 0.05)

        if fila:
            c.add_widget(Texto(
                text=f"{len(fila)} itens · cerca de {self.resumo['minutos_estimados']} min",
                font_size="11sp", color=COR["texto2"]))
            botao = Botao(text=acao, cor=cor_acao, size_hint_y=None, height=dp(50),
                          bold=True, font_size="15sp")
            botao.bind(on_press=lambda _: self.app.ir_para("revisao"))
            c.add_widget(botao)

        coluna.add_widget(c)

    def _centro_anel(self, anel, restante):
        """Número dentro do anel: o que falta, que é o que decide a ação."""
        rotulo = Label(text=f"[b]{restante}[/b]\n[size=10]{'a revisar' if restante else 'em dia'}[/size]",
                       markup=True, color=COR["texto"], font_size="24sp",
                       halign="center", valign="middle")
        rotulo.size = anel.size
        rotulo.pos = anel.pos
        rotulo.text_size = anel.size
        anel.add_widget(rotulo)
        anel.bind(pos=lambda *_: setattr(rotulo, "pos", anel.pos),
                  size=lambda *_: (setattr(rotulo, "size", anel.size),
                                   setattr(rotulo, "text_size", anel.size)))

    # ── 2. memória ──────────────────────────────────────────────────
    def _cartao_memoria(self, coluna):
        c = cartao(altura=dp(120))
        dominio = self.resumo["dominio_geral"]
        c.add_widget(Texto(text="[b]ESTADO DA MEMORIA[/b]", markup=True,
                           font_size="12sp", color=COR["texto2"]))
        c.add_widget(Texto(text=f"{dominio * 100:.0f}% de dominio",
                           font_size="11sp", color=COR["texto2"]))

        barra = BarraEstagios(size_hint_y=None, height=dp(20))
        c.add_widget(barra)
        Clock.schedule_once(lambda _: barra.animar(self.resumo["estagios"]), 0.25)

        legenda = " · ".join(
            f"{ROTULO_ESTAGIO[k]}: {self.resumo['estagios'].get(k, 0)}"
            for k in ("consolidado", "firmando", "aprendendo", "novo"))
        c.add_widget(Texto(text=legenda, font_size="10sp", color=COR["texto2"]))
        coluna.add_widget(c)

    # ── 3. onde focar ───────────────────────────────────────────────
    def _cartao_focar(self, coluna):
        fracos = self.resumo["pontos_fracos"]
        if not fracos:
            return
        c = cartao()
        c.size_hint_y = None
        c.bind(minimum_height=c.setter("height"))
        c.add_widget(Texto(text="[b]ONDE FOCAR[/b]", markup=True,
                           font_size="12sp", color=COR["texto2"]))
        c.add_widget(Texto(text="Seus marcadores mais frageis agora",
                           font_size="11sp", color=COR["texto2"]))

        for sigla, dominio in fracos:
            b = BotaoClaro(
                text=f"{sigla} · {self.nomes.get(sigla, '')}\n{dominio * 100:.0f}% de dominio",
                size_hint_y=None, height=dp(54), font_size="12sp")
            b.bind(on_press=lambda _, s=sigla: self.app.ir_para("estudo", foco=s))
            c.add_widget(b)
        coluna.add_widget(c)

    # ── 4. sistemas ─────────────────────────────────────────────────
    def _cartao_sistemas(self, coluna):
        itens = sorted(self.resumo["dominio_categoria"].items(),
                       key=lambda kv: -kv[1])
        c = cartao(altura=dp(56 + 26 * len(itens)))
        c.add_widget(Texto(text="[b]POR SISTEMA[/b]", markup=True,
                           font_size="12sp", color=COR["texto2"]))
        for i, (categoria, valor) in enumerate(itens):
            linha = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(8))
            linha.add_widget(Label(text=categoria, font_size="11sp",
                                   color=COR["texto"], size_hint_x=None,
                                   width=dp(84), halign="left", valign="middle",
                                   text_size=(dp(84), dp(22))))
            barra = BarraDominio(size_hint_y=None, height=dp(7),
                                 pos_hint={"center_y": 0.5})
            linha.add_widget(barra)
            linha.add_widget(Label(text=f"{valor * 100:.0f}%", font_size="10sp",
                                   color=COR["texto2"], size_hint_x=None,
                                   width=dp(34)))
            c.add_widget(linha)
            Clock.schedule_once(
                lambda _, b=barra, v=valor: b.animar(v), 0.3 + i * 0.06)
        coluna.add_widget(c)

    # ── acesso aos modos ────────────────────────────────────────────
    def _modos(self, coluna):
        modos = [
            ("Estudo", COR["primaria"], "estudo"),
            ("Flashcards", COR["bile"], "flashcards"),
            ("Quiz", COR["cobalto"], "quiz"),
            ("Diagnostico", COR["indicador"], "diagnostico"),
            ("Tutor", COR["sangue"], "tutor"),
        ]
        for titulo, cor, destino in modos:
            b = Botao(text=titulo, cor=cor, size_hint_y=None, height=dp(46),
                      font_size="14sp", bold=True)
            b.bind(on_press=lambda _, d=destino: self.app.ir_para(d))
            coluna.add_widget(b)


# ─────────────────────────────────────────────
# ESTUDO
# ─────────────────────────────────────────────
class TelaEstudo(Painel):
    def __init__(self, app, **kwargs):
        super().__init__(cor=COR["fundo"], orientation="vertical", **kwargs)
        self.app = app
        self.marcadores = app.marcadores
        self.extras = app.extras
        self.imagens = app.imagens

        self.add_widget(cabecalho(app, "Estudo", COR["primaria"]))

        faixa = Painel(cor=COR["superficie"], size_hint_y=None, height=dp(52),
                       padding=dp(8))
        self.busca = TextInput(hint_text="Buscar marcador...", multiline=False,
                               font_size="15sp", padding=(dp(10), dp(10)))
        self.busca.bind(text=lambda *_: self._listar())
        faixa.add_widget(self.busca)
        self.add_widget(faixa)

        scroll, self.lista = coluna_rolavel(padding=dp(10), spacing=dp(6))
        self.add_widget(scroll)
        self._listar()

    def _listar(self):
        self.lista.clear_widgets()
        termo = self.busca.text.strip().lower()
        achou = False
        for m in self.marcadores:
            if termo and termo not in m["nome"].lower() and termo not in m["sigla"].lower():
                continue
            achou = True
            marcas = []
            if m["sigla"] in self.extras:
                if self.extras[m["sigla"]].get("referencias"):
                    marcas.append("fontes")
                if self.extras[m["sigla"]].get("videos"):
                    marcas.append("video")
                if self.extras[m["sigla"]].get("exemplos"):
                    marcas.append("casos")
            if m["sigla"] in self.imagens:
                marcas.append("imagens")
            sufixo = f"\n[{'  '.join(marcas)}]" if marcas else ""

            botao = BotaoClaro(text=f"{m['sigla']} - {m['nome']}{sufixo}",
                               size_hint_y=None, height=dp(64), font_size="13sp")
            botao.bind(on_press=lambda _, mm=m: self._detalhe(mm))
            self.lista.add_widget(botao)

        if not achou:
            self.lista.add_widget(Texto(text="Nenhum marcador encontrado.",
                                        color=COR["texto2"], halign="center"))

    # ---------- detalhe em abas ----------
    def _detalhe(self, m):
        conteudo = BoxLayout(orientation="vertical", padding=dp(6), spacing=dp(6))
        abas = TabbedPanel(do_default_tab=False, tab_width=dp(96))

        abas.add_widget(self._aba_info(m))
        extras = self.extras.get(m["sigla"], {})
        if extras.get("referencias"):
            abas.add_widget(self._aba_referencias(extras["referencias"]))
        if extras.get("videos"):
            abas.add_widget(self._aba_videos(extras["videos"]))
        if extras.get("exemplos"):
            abas.add_widget(self._aba_exemplos(extras["exemplos"]))
        imgs = self.imagens.get(m["sigla"], {}).get("imagens")
        if imgs:
            abas.add_widget(self._aba_imagens(imgs))

        conteudo.add_widget(abas)
        fechar = Botao(text="Fechar", cor=COR["texto2"],
                       size_hint_y=None, height=dp(46))
        conteudo.add_widget(fechar)

        popup = Popup(title=f"{m['sigla']} - {m['nome']}", content=conteudo,
                      size_hint=(0.96, 0.9), title_size="15sp")
        fechar.bind(on_press=popup.dismiss)
        popup.open()

    def _aba_info(self, m):
        aba = TabbedPanelItem(text="Info")
        scroll, col = coluna_rolavel(fundo=COR["superficie"])

        col.add_widget(Texto(text=f"[b]{m['nome']}[/b]", markup=True, font_size="17sp"))
        col.add_widget(Texto(text=f"Categoria: {m.get('categoria', '-')}",
                             color=COR["texto2"], font_size="12sp"))
        col.add_widget(Texto(
            text=f"[b]Referencia:[/b] {m['valor_ref_min']} - {m['valor_ref_max']} {m['unidade']}",
            markup=True, font_size="14sp"))

        col.add_widget(Texto(text="[b]Quando esta ELEVADO[/b]", markup=True,
                             color=COR["erro"], font_size="14sp"))
        col.add_widget(Texto(text=m.get("interpretacao_alta", "-"), font_size="12sp"))
        if m.get("doencas_associadas_alta"):
            col.add_widget(Texto(text=f"Associado a: {m['doencas_associadas_alta']}",
                                 color=COR["texto2"], font_size="12sp"))

        col.add_widget(Texto(text="[b]Quando esta BAIXO[/b]", markup=True,
                             color=COR["cobalto"], font_size="14sp"))
        col.add_widget(Texto(text=m.get("interpretacao_baixa", "-"), font_size="12sp"))
        if m.get("doencas_associadas_baixa"):
            col.add_widget(Texto(text=f"Associado a: {m['doencas_associadas_baixa']}",
                                 color=COR["texto2"], font_size="12sp"))

        aba.add_widget(scroll)
        return aba

    def _aba_referencias(self, referencias):
        """Bibliografia academica verificada (StatPearls / NCBI Bookshelf)."""
        aba = TabbedPanelItem(text="Fontes")
        scroll, col = coluna_rolavel(fundo=COR["superficie"])
        for ref in referencias:
            col.add_widget(Texto(text=f"[b]{ref['titulo']}[/b]", markup=True,
                                 font_size="14sp"))
            col.add_widget(Texto(text=ref["fonte"], color=COR["texto2"],
                                 font_size="11sp"))
            if ref.get("nota"):
                col.add_widget(Texto(text=ref["nota"], font_size="12sp"))
            botao = Botao(text="Abrir referencia", cor=COR["cobalto"],
                          size_hint_y=None, height=dp(42), font_size="13sp")
            botao.bind(on_press=lambda _, u=ref["url"]: self._abrir_link(u))
            col.add_widget(botao)
            col.add_widget(Texto(text="", size_hint_y=None, height=dp(6)))
        aba.add_widget(scroll)
        return aba

    @staticmethod
    def _abrir_link(url):
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"[link] nao foi possivel abrir: {e}")

    def _aba_videos(self, videos):
        aba = TabbedPanelItem(text="Videos")
        scroll, col = coluna_rolavel(fundo=COR["superficie"])
        for v in videos:
            col.add_widget(Texto(text=f"[b]{v['titulo']}[/b]", markup=True, font_size="14sp"))
            col.add_widget(Texto(text=f"Duracao: {v.get('duracao', '-')}",
                                 color=COR["texto2"], font_size="12sp"))
            botao = Botao(text="Assistir no YouTube", cor=COR["sangue"],
                          size_hint_y=None, height=dp(44))
            botao.bind(on_press=lambda _, u=v["url"]: self._abrir_video(u))
            col.add_widget(botao)
        aba.add_widget(scroll)
        return aba

    @staticmethod
    def _abrir_video(url):
        try:
            webbrowser.open(url.replace("/embed/", "/watch?v="))
        except Exception as e:
            print(f"[video] nao foi possivel abrir: {e}")

    def _aba_exemplos(self, exemplos):
        aba = TabbedPanelItem(text="Exemplos")
        scroll, col = coluna_rolavel(fundo=COR["superficie"])
        for i, ex in enumerate(exemplos, 1):
            col.add_widget(Texto(text=f"[b]{i}. {ex['titulo']}[/b]", markup=True,
                                 font_size="14sp"))
            col.add_widget(Texto(text=ex["descricao"], font_size="12sp"))
            col.add_widget(Texto(text=f"[b]Valores:[/b] {ex['valores']}", markup=True,
                                 color=COR["cobalto"], font_size="12sp"))
            col.add_widget(Texto(text=f"[b]Conduta:[/b] {ex['conducao']}", markup=True,
                                 color=COR["primaria"], font_size="12sp"))
            col.add_widget(Texto(text="", size_hint_y=None, height=dp(6)))
        aba.add_widget(scroll)
        return aba

    def _aba_imagens(self, imagens):
        aba = TabbedPanelItem(text="Imagens")
        scroll, col = coluna_rolavel(fundo=COR["superficie"])
        for img in imagens:
            col.add_widget(Texto(text=f"[b]{img['titulo']}[/b]", markup=True,
                                 font_size="14sp"))
            col.add_widget(Texto(text=img["descricao"], font_size="12sp"))
            caminho = IMG_DIR / img["arquivo"]
            if caminho.exists():
                col.add_widget(Image(source=str(caminho), size_hint_y=None,
                                     height=dp(190), allow_stretch=True,
                                     keep_ratio=True))
            else:
                col.add_widget(Texto(
                    text=f"Imagem ausente: {img['arquivo']}\n"
                         f"Gere com: python criar_imagens.py",
                    color=COR["bile"], font_size="11sp"))
            col.add_widget(Texto(text="", size_hint_y=None, height=dp(6)))
        aba.add_widget(scroll)
        return aba


# ─────────────────────────────────────────────
# FLASHCARDS
# ─────────────────────────────────────────────
class TelaFlashcards(Painel):
    def __init__(self, app, **kwargs):
        super().__init__(cor=COR["fundo"], orientation="vertical", **kwargs)
        self.app = app
        self.cards = list(app.flashcards)
        self.indice = 0
        self.virado = False

        self.add_widget(cabecalho(app, "Flashcards", COR["bile"]))

        self.progresso = Label(text="", size_hint_y=None, height=dp(36),
                               color=COR["texto2"], font_size="14sp", bold=True)
        self.add_widget(self.progresso)

        corpo = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        self.card = Botao(text="", cor=COR["primaria"], halign="center",
                          valign="middle", font_size="16sp", bold=True)
        self.card.bind(size=lambda b, *_: setattr(b, "text_size", (b.width - dp(28), None)))
        self.card.bind(on_press=lambda _: self._virar())
        corpo.add_widget(self.card)

        navegacao = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        anterior = Botao(text="Anterior", cor=COR["texto2"])
        anterior.bind(on_press=lambda _: self._mover(-1))
        navegacao.add_widget(anterior)
        embaralhar = Botao(text="Embaralhar", cor=COR["cobalto"])
        embaralhar.bind(on_press=lambda _: self._embaralhar())
        navegacao.add_widget(embaralhar)
        proximo = Botao(text="Proximo", cor=COR["primaria"])
        proximo.bind(on_press=lambda _: self._mover(1))
        navegacao.add_widget(proximo)
        corpo.add_widget(navegacao)

        self.add_widget(corpo)
        self._atualizar()

    def _virar(self):
        if self.cards:
            self.virado = not self.virado
            self._atualizar()

    def _mover(self, passo):
        if not self.cards:
            return
        self.indice = (self.indice + passo) % len(self.cards)
        self.virado = False
        self._atualizar()

    def _embaralhar(self):
        random.shuffle(self.cards)
        self.indice = 0
        self.virado = False
        self._atualizar()

    def _atualizar(self):
        if not self.cards:
            self.progresso.text = "Nenhum flashcard disponivel"
            self.card.text = "Verifique data/flashcards.json"
            return
        card = self.cards[self.indice]
        self.progresso.text = f"{self.indice + 1} de {len(self.cards)}"
        if self.virado:
            self.card.text = f"RESPOSTA\n\n{card['resposta']}"
            self.card.background_color = COR["cobalto"]
        else:
            self.card.text = f"PERGUNTA\n\n{card['pergunta']}\n\n(toque para virar)"
            self.card.background_color = COR["primaria"]


# ─────────────────────────────────────────────
# QUIZ
# ─────────────────────────────────────────────
class TelaQuiz(Painel):
    def __init__(self, app, **kwargs):
        super().__init__(cor=COR["fundo"], orientation="vertical", **kwargs)
        self.app = app
        banco = list(app.quiz)
        random.shuffle(banco)
        self.perguntas = banco[:10]
        self.indice = 0
        self.acertos = 0

        self.add_widget(cabecalho(app, "Quiz", COR["cobalto"]))
        self.area = BoxLayout(orientation="vertical")
        self.add_widget(self.area)
        self._mostrar_pergunta()

    def _mostrar_pergunta(self):
        self.area.clear_widgets()

        if not self.perguntas:
            self.area.add_widget(Texto(text="Nenhuma pergunta disponivel.",
                                       halign="center", color=COR["texto2"]))
            return
        if self.indice >= len(self.perguntas):
            self._mostrar_resultado()
            return

        p = self.perguntas[self.indice]
        scroll, col = coluna_rolavel(padding=dp(14), spacing=dp(10))

        col.add_widget(Texto(text=f"Pergunta {self.indice + 1} de {len(self.perguntas)}"
                                  f"    Acertos: {self.acertos}",
                             color=COR["texto2"], font_size="12sp"))
        col.add_widget(Texto(text=f"[b]{p['pergunta']}[/b]", markup=True, font_size="15sp"))

        for i, alternativa in enumerate(p["alternativas"]):
            botao = BotaoClaro(text=alternativa, size_hint_y=None, height=dp(58),
                               font_size="13sp")
            botao.bind(on_press=lambda _, idx=i, perg=p: self._responder(idx, perg))
            col.add_widget(botao)

        self.area.add_widget(scroll)

    def _responder(self, escolha, pergunta):
        correta = pergunta["resposta_correta"]
        acertou = escolha == correta

        if acertou:
            self.acertos += 1
            self.app.registrar_acerto(10)
        else:
            self.app.registrar_erro()

        # Faz o acerto contar para o agendamento do marcador: sem isso,
        # responder sobre troponina nao afetaria quando ela volta.
        texto = " ".join([pergunta.get("pergunta", ""),
                          *pergunta.get("alternativas", []),
                          pergunta.get("explicacao", "")])
        self.app.alimentar_memoria(texto, acertou, peso="quiz")

        self.area.clear_widgets()
        scroll, col = coluna_rolavel(padding=dp(14), spacing=dp(10))

        col.add_widget(Texto(text="[b]Correto[/b]" if acertou else "[b]Incorreto[/b]",
                             markup=True, font_size="20sp",
                             color=COR["sucesso"] if acertou else COR["erro"]))
        if not acertou:
            col.add_widget(Texto(
                text=f"Resposta certa: {pergunta['alternativas'][correta]}",
                color=COR["sucesso"], font_size="14sp"))
        col.add_widget(Texto(text=pergunta.get("explicacao", ""), font_size="13sp"))

        avancar = Botao(text="Continuar", cor=COR["cobalto"],
                        size_hint_y=None, height=dp(50))
        avancar.bind(on_press=lambda _: self._avancar())
        col.add_widget(avancar)

        self.area.add_widget(scroll)

    def _avancar(self):
        self.indice += 1
        self._mostrar_pergunta()

    def _mostrar_resultado(self):
        self.area.clear_widgets()
        total = len(self.perguntas)
        pct = self.acertos / total * 100 if total else 0

        scroll, col = coluna_rolavel(padding=dp(20), spacing=dp(12))
        col.add_widget(Texto(text="[b]Resultado[/b]", markup=True,
                             font_size="24sp", halign="center"))
        col.add_widget(Texto(text=f"[b]{pct:.0f}%[/b]", markup=True, font_size="46sp",
                             halign="center",
                             color=COR["sucesso"] if pct >= 70 else COR["bile"]))
        col.add_widget(Texto(text=f"{self.acertos} de {total} corretas",
                             halign="center", color=COR["texto2"], font_size="15sp"))

        if pct >= 70:
            recado = "Bom dominio do conteudo."
        elif pct >= 50:
            recado = "Revise os marcadores que errou no modo Estudo."
        else:
            recado = "Vale revisar os flashcards antes de tentar de novo."
        col.add_widget(Texto(text=recado, halign="center", font_size="13sp"))

        de_novo = Botao(text="Novo quiz", cor=COR["cobalto"],
                        size_hint_y=None, height=dp(50))
        de_novo.bind(on_press=lambda _: self.app.ir_para("quiz"))
        col.add_widget(de_novo)

        voltar = Botao(text="Voltar ao inicio", cor=COR["texto2"],
                       size_hint_y=None, height=dp(50))
        voltar.bind(on_press=lambda _: self.app.ir_para("inicio"))
        col.add_widget(voltar)

        self.area.add_widget(scroll)


# ─────────────────────────────────────────────
# DIAGNÓSTICO
# ─────────────────────────────────────────────
class TelaDiagnostico(Painel):
    def __init__(self, app, **kwargs):
        super().__init__(cor=COR["fundo"], orientation="vertical", **kwargs)
        self.app = app
        self.casos = app.casos

        self.add_widget(cabecalho(app, "Diagnostico", COR["indicador"]))
        self.area = BoxLayout(orientation="vertical")
        self.add_widget(self.area)
        self._listar()

    def _listar(self):
        self.area.clear_widgets()
        scroll, col = coluna_rolavel(padding=dp(10), spacing=dp(8))

        if not self.casos:
            col.add_widget(Texto(text="Nenhum caso disponivel.", color=COR["texto2"]))

        for caso in self.casos:
            resumo = caso["historia"]
            if len(resumo) > 90:
                resumo = resumo[:90].rstrip() + "..."
            marca = "  [resolvido]" if caso["id"] in self.app.casos_resolvidos else ""
            botao = BotaoClaro(text=f"{caso['titulo']}{marca}\n{resumo}",
                               size_hint_y=None, height=dp(96), font_size="12sp")
            botao.bind(on_press=lambda _, c=caso: self._abrir(c))
            col.add_widget(botao)

        self.area.add_widget(scroll)

    def _abrir(self, caso):
        self.area.clear_widgets()
        scroll, col = coluna_rolavel(padding=dp(12), spacing=dp(8))

        col.add_widget(Texto(text=f"[b]{caso['titulo']}[/b]", markup=True, font_size="16sp"))
        col.add_widget(Texto(text=caso["historia"], font_size="13sp"))

        col.add_widget(Texto(text="[b]Exames[/b]", markup=True, font_size="15sp"))
        for nome, dados in caso["exames"].items():
            col.add_widget(self._linha_exame(nome, dados))

        col.add_widget(Texto(text="[b]Qual o diagnostico?[/b]", markup=True,
                             font_size="15sp"))

        alternativas = list(caso["alternativas"])
        random.shuffle(alternativas)
        for alternativa in alternativas:
            botao = BotaoClaro(text=alternativa, size_hint_y=None, height=dp(56),
                               font_size="13sp")
            botao.bind(on_press=lambda _, a=alternativa, c=caso: self._responder(a, c))
            col.add_widget(botao)

        voltar = Botao(text="Escolher outro caso", cor=COR["texto2"],
                       size_hint_y=None, height=dp(46))
        voltar.bind(on_press=lambda _: self._listar())
        col.add_widget(voltar)

        self.area.add_widget(scroll)

    @staticmethod
    def _linha_exame(nome, dados):
        valor = dados["valor"]
        unidade = dados.get("unidade", "")
        minimo, maximo = dados.get("ref_min"), dados.get("ref_max")

        situacao, cor = "normal", COR["sucesso"]
        if isinstance(valor, (int, float)) and isinstance(minimo, (int, float)) \
                and isinstance(maximo, (int, float)):
            if valor > maximo:
                situacao, cor = "ALTO", COR["erro"]
            elif valor < minimo:
                situacao, cor = "BAIXO", COR["cobalto"]
            referencia = f"(ref {minimo} - {maximo})"
        else:
            # exames qualitativos, ex.: cetonas "MASSIVAS"
            situacao, cor = "alterado", COR["erro"]
            referencia = f"(ref {minimo})" if minimo else ""

        return Texto(text=f"{nome}: [b]{valor} {unidade}[/b]  {situacao}  {referencia}",
                     markup=True, color=cor, font_size="13sp")

    def _responder(self, escolha, caso):
        acertou = escolha == caso["resposta_correta"]
        ja_resolvido = caso["id"] in self.app.casos_resolvidos

        if acertou:
            if not ja_resolvido:
                self.app.casos_resolvidos.add(caso["id"])
                self.app.registrar_acerto(25)
        else:
            self.app.registrar_erro()

        # Interpretar um caso e recuperacao sobre varios marcadores ao
        # mesmo tempo: todos os dos exames entram, com peso de
        # diagnostico (erro pune menos que numa questao direta).
        self.app.alimentar_memoria(" ".join(caso.get("exames", {}).keys()),
                                   acertou, peso="diagnostico")

        self.area.clear_widgets()
        scroll, col = coluna_rolavel(padding=dp(14), spacing=dp(10))

        col.add_widget(Texto(text="[b]Diagnostico correto[/b]" if acertou
                                  else "[b]Nao e esse[/b]",
                             markup=True, font_size="20sp",
                             color=COR["sucesso"] if acertou else COR["erro"]))
        col.add_widget(Texto(text=f"Sua resposta: {escolha}",
                             color=COR["texto2"], font_size="13sp"))
        if not acertou:
            col.add_widget(Texto(text=f"[b]Correto:[/b] {caso['resposta_correta']}",
                                 markup=True, color=COR["sucesso"], font_size="14sp"))
        col.add_widget(Texto(text=caso.get("explicacao", ""), font_size="13sp"))

        se_errou = Botao(text="Tentar este caso de novo", cor=COR["bile"],
                         size_hint_y=None, height=dp(48))
        se_errou.bind(on_press=lambda _, c=caso: self._abrir(c))
        if not acertou:
            col.add_widget(se_errou)

        lista = Botao(text="Voltar aos casos", cor=COR["indicador"],
                      size_hint_y=None, height=dp(48))
        lista.bind(on_press=lambda _: self._listar())
        col.add_widget(lista)

        self.area.add_widget(scroll)


# ─────────────────────────────────────────────
# TUTOR
# ─────────────────────────────────────────────
class TelaTutor(Painel):
    def __init__(self, app, **kwargs):
        super().__init__(cor=COR["fundo"], orientation="vertical", **kwargs)
        self.app = app
        self.marcadores = app.marcadores

        self.add_widget(cabecalho(app, "Tutor", COR["sangue"]))

        scroll, self.conversa = coluna_rolavel(padding=dp(10), spacing=dp(8))
        self.scroll = scroll
        self.add_widget(scroll)

        entrada = Painel(cor=COR["superficie"], size_hint_y=None, height=dp(60),
                         padding=dp(8), spacing=dp(6))
        self.campo = TextInput(hint_text="Pergunte sobre um marcador...",
                               multiline=False, font_size="14sp",
                               padding=(dp(10), dp(10)))
        self.campo.bind(on_text_validate=lambda _: self._enviar())
        entrada.add_widget(self.campo)
        enviar = Botao(text="Enviar", cor=COR["sangue"],
                       size_hint_x=None, width=dp(84))
        enviar.bind(on_press=lambda _: self._enviar())
        entrada.add_widget(enviar)
        self.add_widget(entrada)

        siglas = ", ".join(m["sigla"] for m in self.marcadores[:6])
        self._responder(
            "Ola. Pergunte sobre qualquer marcador e eu explico os valores de "
            f"referencia e o significado clinico.\n\nExemplos: {siglas}...")

    def _mensagem(self, texto, cor, alinhamento):
        self.conversa.add_widget(Texto(text=texto, color=cor, halign=alinhamento,
                                       font_size="13sp"))
        Clock.schedule_once(lambda _: setattr(self.scroll, "scroll_y", 0), 0.05)

    def _responder(self, texto):
        self._mensagem(texto, COR["cobalto"], "left")

    def _enviar(self):
        pergunta = self.campo.text.strip()
        if not pergunta:
            return
        self.campo.text = ""
        self._mensagem(f"Voce: {pergunta}", COR["texto"], "right")

        marcador = self._identificar_marcador(pergunta)
        if self.app.ia is not None and marcador is not None:
            self._responder("Consultando o tutor local...")
            threading.Thread(target=self._perguntar_ia,
                             args=(marcador, pergunta), daemon=True).start()
        else:
            self._responder(self._resposta_local(pergunta, marcador))

    def _perguntar_ia(self, marcador, pergunta):
        """Consulta o Ollama em segundo plano; cai para a base local se falhar."""
        try:
            resposta = self.app.ia.chat_marcador(marcador["nome"], pergunta)
        except Exception as e:
            resposta = ""
            print(f"[tutor] falha na consulta: {type(e).__name__}: {e}")

        if not self._resposta_util(resposta):
            # Ollama no ar mas sem modelo instalado, ou resposta vazia.
            self.app.ia = None  # nao insiste nas proximas perguntas
            resposta = ("O tutor local nao esta disponivel (verifique se o modelo "
                        "foi baixado com 'ollama pull mistral'). "
                        "Respondendo pela base do app:\n\n"
                        + self._resumo(marcador))

        Clock.schedule_once(lambda _: self._responder(resposta), 0)

    @staticmethod
    def _resposta_util(texto):
        if not texto or not texto.strip():
            return False
        inicio = texto.strip().lower()
        return not inicio.startswith(("erro", "error", "[erro"))

    def _identificar_marcador(self, pergunta):
        texto = pergunta.lower()
        for m in self.marcadores:
            if m["sigla"].lower() in texto or m["nome"].lower() in texto:
                return m
        return None

    @staticmethod
    def _resumo(m):
        return (f"{m['nome']} ({m['sigla']})\n"
                f"Referencia: {m['valor_ref_min']} - {m['valor_ref_max']} {m['unidade']}\n\n"
                f"Elevado: {m.get('interpretacao_alta', '-')}\n"
                f"Associado a: {m.get('doencas_associadas_alta', '-')}\n\n"
                f"Baixo: {m.get('interpretacao_baixa', '-')}\n"
                f"Associado a: {m.get('doencas_associadas_baixa', '-')}")

    def _resposta_local(self, pergunta, marcador):
        if marcador is not None:
            return self._resumo(marcador)

        texto = pergunta.lower()
        if any(p in texto for p in ("oi", "ola", "bom dia", "boa tarde", "boa noite")):
            return "Ola. Digite o nome ou a sigla de um marcador para comecar."
        if "obrigad" in texto:
            return "De nada. Bons estudos."
        if any(p in texto for p in ("ajuda", "como", "o que voce faz")):
            return ("Digite a sigla de um marcador (por exemplo ALT, Glicose, "
                    "Potassio) e eu mostro a faixa de referencia e o que significa "
                    "estar alto ou baixo.")

        disponiveis = ", ".join(m["sigla"] for m in self.marcadores)
        return ("Nao encontrei esse marcador na base.\n\n"
                f"Marcadores disponiveis: {disponiveis}")


# ─────────────────────────────────────────────
# REVISÃO
# ─────────────────────────────────────────────
class TelaRevisao(Painel):
    """Sessão de estudo: pergunta, confiança, resposta, autoavaliação.

    A confiança é pedida ANTES de revelar a resposta. Depois de ver, todo
    mundo acha que sabia — perguntar antes é o que torna a medida honesta.

    A autoavaliação tem quatro níveis, e não certo/errado, porque o SM-2
    precisa de graduação: "lembrei com esforço" e "lembrei na hora" levam
    a intervalos diferentes.
    """

    AVALIACOES = [
        ("De novo", 0, COR["erro"]),
        ("Dificil", 3, COR["bile"]),
        ("Bom",     4, COR["primaria"]),
        ("Facil",   5, COR["cobalto"]),
    ]

    CONFIANCA = [(1, "Nenhuma"), (2, "Pouca"), (3, "Media"), (4, "Boa"), (5, "Total")]

    def __init__(self, app, **kwargs):
        super().__init__(cor=COR["fundo"], orientation="vertical", **kwargs)
        self.app = app
        self.progresso = app.progresso
        self.por_sigla = {m["sigla"]: m for m in app.marcadores}
        self.fila = self.progresso.fila_do_dia(list(self.por_sigla))
        self.posicao = 0
        self.acertos = 0
        self.confianca = None

        self.add_widget(cabecalho(app, "Revisao", COR["primaria"]))
        self.area = BoxLayout(orientation="vertical")
        self.add_widget(self.area)
        self._mostrar()

    def _mostrar(self):
        self.area.clear_widgets()
        self.confianca = None

        if not self.fila:
            self._vazio()
            return
        if self.posicao >= len(self.fila):
            self._fim()
            return

        sigla = self.fila[self.posicao]
        m = self.por_sigla[sigla]
        scroll, col = coluna_rolavel(padding=dp(14), spacing=dp(8))

        col.add_widget(Texto(text=f"{self.posicao + 1} de {len(self.fila)}",
                             font_size="11sp", color=COR["texto2"]))
        col.add_widget(Texto(text=m["categoria"].upper(), font_size="10sp",
                             color=COR["texto2"]))
        col.add_widget(Texto(text=f"[b]{m['nome']}[/b]", markup=True,
                             font_size="20sp"))
        col.add_widget(Texto(text=f"Sigla: {sigla}", font_size="11sp",
                             color=COR["texto2"]))
        col.add_widget(Texto(
            text="Qual a faixa de referencia e o que significa estar alterado?",
            font_size="14sp"))

        self.col = col
        self._pedir_confianca()
        self.area.add_widget(scroll)

    def _pedir_confianca(self):
        self.col.add_widget(Texto(text="Antes de ver: o quanto voce acha que sabe?",
                                  font_size="12sp", color=COR["texto2"]))
        grade = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(4))
        for valor, rotulo in self.CONFIANCA:
            b = Botao(text=rotulo, cor=COR["superficie"], color=COR["texto"],
                      font_size="10sp")
            b.bind(on_press=lambda _, v=valor: self._definir_confianca(v))
            grade.add_widget(b)
        self.grade_confianca = grade
        self.col.add_widget(grade)

    def _definir_confianca(self, valor):
        self.confianca = valor
        for (v, _), b in zip(self.CONFIANCA, self.grade_confianca.children[::-1]):
            marcado = v == valor
            b.background_color = COR["primaria"] if marcado else COR["superficie"]
            b.color = COR["branco"] if marcado else COR["texto"]
        self.botao_revelar = Botao(text="Ver resposta", cor=COR["primaria"],
                                   size_hint_y=None, height=dp(48), bold=True)
        self.botao_revelar.bind(on_press=lambda _: self._revelar())
        self.col.add_widget(self.botao_revelar)

    def _revelar(self):
        sigla = self.fila[self.posicao]
        m = self.por_sigla[sigla]

        # o botao cumpriu a funcao; deixa-lo na tela so ocupa espaco
        botao = getattr(self, "botao_revelar", None)
        if botao is not None and botao.parent is not None:
            self.col.remove_widget(botao)
        for _, b in zip(self.CONFIANCA, self.grade_confianca.children):
            b.disabled = True

        self.col.add_widget(Texto(
            text=f"[b]{m['valor_ref_min']} a {m['valor_ref_max']} {m['unidade']}[/b]",
            markup=True, font_size="18sp", color=COR["primaria"]))
        self.col.add_widget(Texto(text="[b]Elevado[/b]", markup=True,
                                  font_size="13sp", color=COR["erro"]))
        self.col.add_widget(Texto(text=m.get("interpretacao_alta", "-"),
                                  font_size="12sp"))
        self.col.add_widget(Texto(text="[b]Baixo[/b]", markup=True,
                                  font_size="13sp", color=COR["cobalto"]))
        self.col.add_widget(Texto(text=m.get("interpretacao_baixa", "-"),
                                  font_size="12sp"))

        self.col.add_widget(Texto(text="Como foi lembrar disso?",
                                  font_size="12sp", color=COR["texto2"]))
        grade = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(5))
        for rotulo, qualidade, cor in self.AVALIACOES:
            b = Botao(text=f"{rotulo}\n{self._previsao(sigla, qualidade)}",
                      cor=cor, font_size="11sp", halign="center", valign="middle")
            b.bind(size=lambda w, *_: setattr(w, "text_size", (w.width - dp(6), None)))
            b.bind(on_press=lambda _, q=qualidade: self._responder(q))
            grade.add_widget(b)
        self.col.add_widget(grade)
        self.col.add_widget(Texto(
            text="A escolha define quando este marcador volta a aparecer.",
            font_size="10sp", color=COR["texto2"]))

    def _previsao(self, sigla, qualidade):
        from progresso import (INTERVALO_1, INTERVALO_2,
                               INTERVALO_FACIL_INICIAL)
        e = self.progresso.estado(sigla)
        if qualidade < 3:
            dias = INTERVALO_1
        elif e["repeticoes"] == 0:
            dias = INTERVALO_FACIL_INICIAL if qualidade == 5 else INTERVALO_1
        elif e["repeticoes"] == 1:
            dias = INTERVALO_2
        else:
            dias = max(1, round(e["intervalo"] * e["facilidade"]))
        if dias == 1:
            return "amanha"
        return f"{dias}d" if dias < 30 else f"{dias // 30}m"

    def _responder(self, qualidade):
        sigla = self.fila[self.posicao]
        self.progresso.registrar_resposta(sigla, qualidade, confianca=self.confianca)
        if qualidade >= 3:
            self.acertos += 1
        self.posicao += 1
        self._mostrar()

    def _vazio(self):
        scroll, col = coluna_rolavel(padding=dp(18), spacing=dp(10))
        col.add_widget(Texto(text="[b]Nada para revisar agora[/b]", markup=True,
                             font_size="18sp"))
        col.add_widget(Texto(
            text="Todos os marcadores estao em dia. Voltar antes da hora reforca "
                 "menos do que esperar o intervalo certo.",
            font_size="12sp", color=COR["texto2"]))
        b = Botao(text="Voltar ao inicio", cor=COR["primaria"],
                  size_hint_y=None, height=dp(48))
        b.bind(on_press=lambda _: self.app.ir_para("inicio"))
        col.add_widget(b)
        self.area.add_widget(scroll)

    def _fim(self):
        scroll, col = coluna_rolavel(padding=dp(18), spacing=dp(10))
        col.add_widget(Texto(text="[b]Sessao concluida[/b]", markup=True,
                             font_size="20sp"))
        col.add_widget(Texto(text=f"{self.acertos} de {len(self.fila)} lembrados",
                             font_size="13sp", color=COR["texto2"]))

        restante = self.progresso.fila_do_dia(list(self.por_sigla))
        if restante:
            col.add_widget(Texto(
                text=f"Ainda ha {len(restante)} item(ns) para hoje, incluindo os "
                     "que voce marcou como 'de novo'.",
                font_size="12sp", color=COR["texto2"]))
            b = Botao(text="Continuar revisando", cor=COR["primaria"],
                      size_hint_y=None, height=dp(48))
            b.bind(on_press=lambda _: self.app.ir_para("revisao"))
            col.add_widget(b)
        else:
            col.add_widget(Texto(
                text="Sua fila de hoje acabou. Os itens voltam sozinhos quando a "
                     "memoria comecar a ceder.",
                font_size="12sp", color=COR["texto2"]))

        b2 = Botao(text="Voltar ao inicio", cor=COR["texto2"],
                   size_hint_y=None, height=dp(48))
        b2.bind(on_press=lambda _: self.app.ir_para("inicio"))
        col.add_widget(b2)
        self.area.add_widget(scroll)


# ─────────────────────────────────────────────
# APLICATIVO
# ─────────────────────────────────────────────
class BioquimicaApp(App):
    title = "BioquimicaEDU"

    TELAS = {
        "inicio": TelaInicial,
        "revisao": TelaRevisao,
        "estudo": TelaEstudo,
        "flashcards": TelaFlashcards,
        "quiz": TelaQuiz,
        "diagnostico": TelaDiagnostico,
        "tutor": TelaTutor,
    }

    def build(self):
        from progresso import Progresso
        self.progresso = Progresso()

        # Mantidos porque quiz e diagnostico ainda leem estes contadores
        self.xp = 0
        self.streak = 0
        self.casos_resolvidos = set()

        self.marcadores = carregar_marcadores()
        self.flashcards = carregar_flashcards()
        self.extras = carregar_extras()
        self.imagens = carregar_imagens()
        self.quiz = carregar_quiz()
        self.casos = carregar_casos()
        self.ia = self._iniciar_ia()

        self.raiz = BoxLayout()
        self.ir_para("inicio")
        return self.raiz

    @staticmethod
    def _iniciar_ia():
        """Usa Ollama local se estiver rodando; caso contrario segue offline."""
        try:
            from ollama_ia import OllamaIA
        except ImportError:
            return None
        try:
            ia = OllamaIA()
            if getattr(ia, "disponivel", False) or getattr(ia, "conectado", False):
                print("[tutor] Ollama local disponivel")
                return ia
        except Exception as e:
            print(f"[tutor] Ollama indisponivel ({type(e).__name__}), usando modo offline")
        return None

    def alimentar_memoria(self, texto, acertou, peso):
        """Liga quiz e diagnostico ao motor de repeticao espacada."""
        from progresso import marcadores_no_texto
        siglas = [m["sigla"] for m in self.marcadores]
        nomes = {m["sigla"]: m["nome"] for m in self.marcadores}
        alvos = marcadores_no_texto(texto, siglas, nomes)
        if alvos:
            self.progresso.registrar_atividade(alvos, acertou, peso=peso)
        return alvos

    def registrar_acerto(self, pontos):
        self.xp += pontos
        self.streak += 1

    def registrar_erro(self):
        self.streak = 0

    def ir_para(self, destino, foco=None):
        """Troca de tela. `foco` abre o Estudo direto em um marcador."""
        self.raiz.clear_widgets()
        Classe = self.TELAS.get(destino, TelaInicial)
        tela = Classe(self)
        self.raiz.add_widget(tela)
        if foco and destino == "estudo":
            Clock.schedule_once(lambda _: self._focar(tela, foco), 0.1)

    @staticmethod
    def _focar(tela, sigla):
        alvo = next((m for m in tela.marcadores if m["sigla"] == sigla), None)
        if alvo is not None:
            tela._detalhe(alvo)


if __name__ == "__main__":
    BioquimicaApp().run()
