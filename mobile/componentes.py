"""Peças visuais da versão mobile.

Tudo aqui nasce de uma base só, a Superficie: fundo arredondado, sombra
suave opcional, borda opcional e três propriedades de movimento — escala
(resposta ao toque), escala horizontal (o card que vira) e deslocamento
vertical (a entrada escalonada das seções). Assim cartões, botões e
etiquetas se mexem do mesmo jeito, e a interface parece uma coisa só.

As animações são curtas e comunicam algo: o botão afunda ao toque (foi
registrado), as seções sobem ao entrar (a tela carregou), as barras
crescem até o valor real (quanto você domina). Nada anima por enfeite.
"""

import math
from datetime import date

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import (Color, Line, PopMatrix, PushMatrix, Rectangle,
                           RoundedRectangle, Scale, Translate)
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from mobile.tema import (COR, COR_ESTAGIO, ESTILO_TEXTO, ICONE, RAIO_BOTAO,
                         RAIO_CARTAO)


# ════════════════════════════════════════════════════════════════════
# BASE
# ════════════════════════════════════════════════════════════════════
class Superficie(BoxLayout):
    """BoxLayout com fundo arredondado, sombra, borda e movimento."""

    cor_fundo = ListProperty([0, 0, 0, 0])
    cor_borda = ListProperty([0, 0, 0, 0])
    raio = NumericProperty(RAIO_CARTAO)
    elevacao = NumericProperty(0)     # 0 sem sombra, 1 suave, 2 destacada
    escala = NumericProperty(1.0)
    escala_x = NumericProperty(1.0)   # só na horizontal: o card que vira
    desloc_y = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            PushMatrix()
            self._translacao = Translate(0, 0)
            self._escala = Scale(1, 1, 1)
            self._cor_sombra_1 = Color(0, 0, 0, 0)
            self._sombra_1 = RoundedRectangle()
            self._cor_sombra_2 = Color(0, 0, 0, 0)
            self._sombra_2 = RoundedRectangle()
            self._cor_fundo = Color(0, 0, 0, 0)
            self._fundo = RoundedRectangle()
            self._cor_borda = Color(0, 0, 0, 0)
            self._borda = Line(width=dp(1))
        with self.canvas.after:
            PopMatrix()
        self.bind(pos=self._redesenhar, size=self._redesenhar,
                  cor_fundo=self._redesenhar, cor_borda=self._redesenhar,
                  raio=self._redesenhar, elevacao=self._redesenhar,
                  escala=self._redesenhar, escala_x=self._redesenhar,
                  desloc_y=self._redesenhar)
        self._redesenhar()

    def _redesenhar(self, *_):
        x, y = self.pos
        w, h = self.size
        r = min(self.raio, h / 2, w / 2) if w and h else self.raio

        self._translacao.y = self.desloc_y
        self._escala.origin = self.center
        self._escala.x = max(0.001, self.escala * self.escala_x)
        self._escala.y = self.escala

        if self.elevacao and self.cor_fundo[3] > 0:
            # duas camadas deslocadas para baixo imitam luz vinda de cima
            sombra = COR["sombra"]
            self._cor_sombra_1.rgba = (*sombra[:3], 0.045 * self.elevacao)
            self._sombra_1.pos = (x, y - dp(1.5) * self.elevacao)
            self._sombra_1.size = (w, h)
            self._sombra_1.radius = [r]
            self._cor_sombra_2.rgba = (*sombra[:3], 0.028 * self.elevacao)
            self._sombra_2.pos = (x - dp(1), y - dp(3.5) * self.elevacao)
            self._sombra_2.size = (w + dp(2), h + dp(1))
            self._sombra_2.radius = [r + dp(2)]
        else:
            self._cor_sombra_1.rgba = (0, 0, 0, 0)
            self._cor_sombra_2.rgba = (0, 0, 0, 0)

        self._cor_fundo.rgba = self.cor_fundo
        self._fundo.pos = (x, y)
        self._fundo.size = (w, h)
        self._fundo.radius = [r]

        self._cor_borda.rgba = self.cor_borda
        if w > 2 and h > 2:
            self._borda.rounded_rectangle = (x, y, w, h, r)


def aparecer(widgets, atraso=0.05, passo=0.055):
    """Entrada escalonada: cada seção sobe e surge logo depois da anterior.

    Guia o olho de cima para baixo, na ordem de importância, sem prender o
    estudante esperando (menos de meio segundo no total).
    """
    for i, w in enumerate(widgets):
        w.opacity = 0
        if hasattr(w, "desloc_y"):
            w.desloc_y = -dp(14)

        def iniciar(_dt, alvo=w):
            props = {"opacity": 1}
            if hasattr(alvo, "desloc_y"):
                props["desloc_y"] = 0
            Animation(duration=0.38, t="out_cubic", **props).start(alvo)

        Clock.schedule_once(iniciar, atraso + i * passo)


def coluna_rolavel(padding=(dp(16), dp(8), dp(16), dp(24)), spacing=dp(14)):
    """ScrollView vertical com uma coluna que cresce conforme o conteúdo."""
    scroll = ScrollView(do_scroll_x=False, bar_width=dp(3),
                        bar_color=(*COR["tinta3"][:3], 0.5),
                        bar_inactive_color=(*COR["tinta3"][:3], 0.15),
                        scroll_type=["bars", "content"])
    coluna = BoxLayout(orientation="vertical", size_hint_y=None,
                       padding=padding, spacing=spacing)
    coluna.bind(minimum_height=coluna.setter("height"))
    scroll.add_widget(coluna)
    return scroll, coluna


def faixa_rolavel(altura, spacing=dp(8), padding=(0, 0)):
    """ScrollView horizontal, para chips e selos."""
    scroll = ScrollView(do_scroll_y=False, size_hint_y=None, height=altura,
                        bar_width=0, scroll_type=["content"])
    linha = BoxLayout(size_hint_x=None, spacing=spacing, padding=padding)
    linha.bind(minimum_width=linha.setter("width"))
    scroll.add_widget(linha)
    return scroll, linha


def espacador(altura=None, largura=None):
    if largura is not None:
        return Widget(size_hint_x=None, width=largura)
    if altura is not None:
        return Widget(size_hint_y=None, height=altura)
    return Widget()


# ════════════════════════════════════════════════════════════════════
# TEXTO E ÍCONES
# ════════════════════════════════════════════════════════════════════
class Texto(Label):
    """Label que quebra linha e cresce conforme o conteúdo."""

    def __init__(self, estilo="corpo", **kwargs):
        for chave, valor in ESTILO_TEXTO.get(estilo, {}).items():
            kwargs.setdefault(chave, valor)
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "top")
        kwargs.setdefault("line_height", 1.12)
        super().__init__(**kwargs)
        self.bind(width=self._largura, texture_size=self._altura)

    def _largura(self, *_):
        self.text_size = (self.width, None)

    def _altura(self, *_):
        self.height = self.texture_size[1]


def rotulo(texto, tamanho="14sp", cor=None, negrito=False, alinhar="left",
           vertical="middle", encurtar=False, **kwargs):
    """Label de uma linha que respeita o alinhamento dentro da sua caixa."""
    r = Label(text=texto, font_size=tamanho, color=cor or COR["tinta"],
              bold=negrito, halign=alinhar, valign=vertical,
              shorten=encurtar, shorten_from="right", **kwargs)
    r.bind(size=lambda l, *_: setattr(l, "text_size", l.size))
    return r


class Icone(Label):
    """Símbolo da fonte de ícones."""

    def __init__(self, nome, tamanho=dp(22), **kwargs):
        kwargs.setdefault("font_name", "Icones")
        kwargs.setdefault("font_size", tamanho)
        kwargs.setdefault("color", COR["tinta2"])
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (tamanho * 1.25, tamanho * 1.25))
        kwargs.setdefault("halign", "center")
        kwargs.setdefault("valign", "middle")
        super().__init__(text=ICONE.get(nome, nome), **kwargs)
        self.bind(size=lambda *_: setattr(self, "text_size", self.size))


class Lupa(Widget):
    """Ícone de busca desenhado — a fonte de ícones não tem lupa."""

    def __init__(self, cor=None, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(22), dp(22)))
        super().__init__(**kwargs)
        self.cor = cor or COR["tinta3"]
        self.bind(pos=self._desenhar, size=self._desenhar)

    def _desenhar(self, *_):
        self.canvas.clear()
        r = self.width * 0.30
        cx, cy = self.x + self.width * 0.42, self.y + self.height * 0.58
        with self.canvas:
            Color(*self.cor)
            Line(circle=(cx, cy, r), width=dp(1.6))
            Line(points=[cx + r * 0.72, cy - r * 0.72,
                         self.x + self.width * 0.86, self.y + self.height * 0.14],
                 width=dp(1.8), cap="round")


class Ponto(Widget):
    """Pequeno círculo de cor: sistema, estágio, legenda."""

    def __init__(self, cor, tamanho=dp(9), **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (tamanho, tamanho))
        kwargs.setdefault("pos_hint", {"center_y": 0.5})
        super().__init__(**kwargs)
        with self.canvas:
            self._cor = Color(*cor)
            self._forma = RoundedRectangle(radius=[tamanho / 2])
        self.bind(pos=self._desenhar, size=self._desenhar)

    def _desenhar(self, *_):
        self._forma.pos = self.pos
        self._forma.size = self.size


class Divisor(Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(1))
        super().__init__(**kwargs)
        with self.canvas:
            Color(*COR["borda"])
            self._linha = Rectangle()
        self.bind(pos=self._desenhar, size=self._desenhar)

    def _desenhar(self, *_):
        self._linha.pos = self.pos
        self._linha.size = self.size


# ════════════════════════════════════════════════════════════════════
# SUPERFÍCIES
# ════════════════════════════════════════════════════════════════════
class Cartao(Superficie):
    """A unidade visual das telas: superfície branca, cantos largos."""

    def __init__(self, auto_altura=None, **kwargs):
        if auto_altura is None:
            auto_altura = "height" not in kwargs
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", dp(18))
        kwargs.setdefault("spacing", dp(10))
        kwargs.setdefault("cor_fundo", COR["superficie"])
        kwargs.setdefault("elevacao", 1)
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)
        if auto_altura:
            self.bind(minimum_height=self.setter("height"))


class LinhaToque(ButtonBehavior, Superficie):
    """Superfície tocável: linhas de lista, opções de resposta, atalhos."""

    def __init__(self, auto_altura=False, **kwargs):
        kwargs.setdefault("cor_fundo", COR["superficie"])
        kwargs.setdefault("raio", dp(18))
        if auto_altura:
            kwargs["size_hint_y"] = None
        super().__init__(**kwargs)
        if auto_altura:
            self.bind(minimum_height=self.setter("height"))

    def on_state(self, _instancia, estado):
        Animation.cancel_all(self, "escala")
        if estado == "down":
            Animation(escala=0.975, duration=0.07, t="out_quad").start(self)
        else:
            Animation(escala=1.0, duration=0.2, t="out_back").start(self)


class SeloIcone(Superficie):
    """Ícone dentro de um círculo colorido."""

    def __init__(self, icone, cor_fundo=None, cor_icone=None, tamanho=dp(40),
                 tamanho_icone=None, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (tamanho, tamanho))
        super().__init__(cor_fundo=cor_fundo or COR["acento_suave"],
                         raio=tamanho / 2, **kwargs)
        self.icone = Icone(icone, tamanho=tamanho_icone or tamanho * 0.46,
                           color=cor_icone or COR["acento"], size_hint=(1, 1))
        self.add_widget(self.icone)


class Etiqueta(Superficie):
    """Pílula pequena e estática: ALTO, BAIXO, categoria, estágio."""

    def __init__(self, text, fundo, tinta, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("height", dp(24))
        kwargs.setdefault("padding", (dp(10), 0))
        kwargs.setdefault("pos_hint", {"center_y": 0.5})
        super().__init__(cor_fundo=fundo, raio=dp(12), **kwargs)
        self.rotulo = Label(text=text, font_size="11.5sp", bold=True, color=tinta)
        self.rotulo.bind(texture_size=lambda *_: setattr(
            self, "width", self.rotulo.texture_size[0] + dp(20)))
        self.add_widget(self.rotulo)

    def pintar(self, text, fundo, tinta):
        self.rotulo.text = text
        self.cor_fundo = fundo
        self.rotulo.color = tinta


# ════════════════════════════════════════════════════════════════════
# BOTÕES
# ════════════════════════════════════════════════════════════════════
class Botao(ButtonBehavior, Superficie):
    """Botão arredondado que afunda levemente ao toque."""

    VARIANTES = {
        #             fundo                  texto
        "primario":   (COR["acento"],         COR["branco"]),
        "secundario": (COR["acento_suave"],   COR["acento_escuro"]),
        "neutro":     (COR["superficie_alt"], COR["tinta"]),
        "claro":      (COR["superficie"],     COR["tinta"]),
        "fantasma":   (COR["transparente"],   COR["tinta2"]),
        "perigo":     (COR["rubro"],          COR["branco"]),
        "atencao":    (COR["ambar"],          COR["branco"]),
    }

    def __init__(self, text="", variante="primario", icone=None, cor=None,
                 cor_texto=None, tamanho_fonte="15sp", negrito=True, **kwargs):
        fundo, tinta = self.VARIANTES.get(variante, self.VARIANTES["primario"])
        if cor is not None:
            fundo = cor
        tinta = cor_texto or tinta

        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(52))
        kwargs.setdefault("raio", RAIO_BOTAO)
        kwargs.setdefault("padding", (dp(14), 0))
        kwargs.setdefault("spacing", dp(8))
        super().__init__(cor_fundo=fundo, **kwargs)

        if icone:
            # ícone e texto formam um grupo centralizado
            self.add_widget(Widget())
            self.icone = Icone(icone, tamanho=dp(17), color=tinta,
                               pos_hint={"center_y": 0.5})
            self.add_widget(self.icone)
            self.rotulo = Label(text=text, color=tinta, bold=negrito,
                                font_size=tamanho_fonte, size_hint_x=None)
            self.rotulo.bind(texture_size=lambda r, *_: setattr(r, "width", r.texture_size[0]))
            self.add_widget(self.rotulo)
            self.add_widget(Widget())
        else:
            self.icone = None
            self.rotulo = Label(text=text, color=tinta, bold=negrito,
                                font_size=tamanho_fonte, halign="center",
                                valign="middle", line_height=1.1)
            self.rotulo.bind(size=lambda r, *_: setattr(r, "text_size", r.size))
            self.add_widget(self.rotulo)

        # Desabilitado, o Kivy troca a cor do texto por um cinza translúcido
        # que some no fundo do botão. A opacidade já comunica o estado.
        self._manter_cor_desabilitado(tinta)
        self.bind(disabled=lambda *_: setattr(self, "opacity",
                                              0.42 if self.disabled else 1))

    def _manter_cor_desabilitado(self, tinta):
        self.rotulo.disabled_color = tinta
        if self.icone is not None:
            self.icone.disabled_color = tinta

    @property
    def text(self):
        return self.rotulo.text

    @text.setter
    def text(self, valor):
        self.rotulo.text = valor

    def pintar(self, fundo, tinta):
        self.cor_fundo = fundo
        self.rotulo.color = tinta
        if self.icone is not None:
            self.icone.color = tinta
        self._manter_cor_desabilitado(tinta)

    def on_state(self, _instancia, estado):
        Animation.cancel_all(self, "escala")
        if estado == "down":
            Animation(escala=0.965, duration=0.07, t="out_quad").start(self)
        else:
            Animation(escala=1.0, duration=0.18, t="out_back").start(self)


def titulo_pagina(titulo, subtitulo="", acao=None):
    """Título grande das abas principais, com subtítulo e ação opcional.

    A linha do título tem altura própria: dividir a caixa ao meio cortava
    o acento de títulos como "Prática".
    """
    linha = BoxLayout(size_hint_y=None, height=dp(60))
    textos = BoxLayout(orientation="vertical")
    textos.add_widget(rotulo(titulo, "26sp", COR["tinta"], negrito=True,
                             vertical="bottom", size_hint_y=None, height=dp(38)))
    if subtitulo:
        r = rotulo(subtitulo, "13sp", COR["tinta3"], vertical="top",
                   size_hint_y=None, height=dp(22))
        textos.add_widget(r)
        linha.subtitulo = r
    linha.add_widget(textos)
    if acao is not None:
        acao.pos_hint = {"center_y": 0.5}
        linha.add_widget(acao)
    return linha


class BotaoIcone(ButtonBehavior, Superficie):
    """Botão redondo só com ícone (voltar, fechar, embaralhar, enviar)."""

    def __init__(self, icone, cor_icone=None, cor=None, tamanho=dp(44), **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (tamanho, tamanho))
        super().__init__(cor_fundo=cor or COR["transparente"],
                         raio=tamanho / 2, **kwargs)
        self.icone = Icone(icone, tamanho=dp(21), color=cor_icone or COR["tinta"],
                           size_hint=(1, 1))
        self.add_widget(self.icone)

    def on_state(self, _instancia, estado):
        Animation.cancel_all(self, "escala")
        Animation(escala=0.86 if estado == "down" else 1.0,
                  duration=0.08 if estado == "down" else 0.22,
                  t="out_quad" if estado == "down" else "out_back").start(self)


class Chip(ButtonBehavior, Superficie):
    """Etiqueta em pílula, selecionável — filtros e abas."""

    selecionado = BooleanProperty(False)

    def __init__(self, text, cor_ponto=None, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("height", dp(36))
        kwargs.setdefault("padding", (dp(14), 0))
        kwargs.setdefault("spacing", dp(7))
        kwargs.setdefault("pos_hint", {"center_y": 0.5})
        super().__init__(raio=dp(18), **kwargs)
        self.tem_ponto = cor_ponto is not None
        if self.tem_ponto:
            self.add_widget(Ponto(cor_ponto, tamanho=dp(8)))
        self.rotulo = Label(text=text, font_size="13.5sp", bold=True,
                            size_hint_x=None)
        self.rotulo.bind(texture_size=self._medir)
        self.add_widget(self.rotulo)
        self.bind(selecionado=self._aplicar)
        self._aplicar()

    def _medir(self, *_):
        self.rotulo.width = self.rotulo.texture_size[0]
        extra = dp(15) if self.tem_ponto else 0
        self.width = self.rotulo.width + dp(28) + extra

    def _aplicar(self, *_):
        if self.selecionado:
            self.cor_fundo = COR["tinta"]
            self.cor_borda = COR["transparente"]
            self.rotulo.color = COR["branco"]
        else:
            self.cor_fundo = COR["superficie"]
            self.cor_borda = COR["borda"]
            self.rotulo.color = COR["tinta2"]

    def on_state(self, _instancia, estado):
        Animation.cancel_all(self, "escala")
        Animation(escala=0.94 if estado == "down" else 1.0,
                  duration=0.08 if estado == "down" else 0.18).start(self)


# ════════════════════════════════════════════════════════════════════
# CAMPOS
# ════════════════════════════════════════════════════════════════════
class CampoTexto(Superficie):
    """Campo arredondado; com `lupa=True` vira busca."""

    def __init__(self, dica="", lupa=False, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(50))
        kwargs.setdefault("padding", (dp(14), dp(4), dp(8), dp(4)))
        kwargs.setdefault("spacing", dp(8))
        super().__init__(cor_fundo=COR["superficie"], cor_borda=COR["borda"],
                         raio=dp(16), **kwargs)
        if lupa:
            self.add_widget(Lupa(pos_hint={"center_y": 0.5}))
        self.campo = TextInput(
            hint_text=dica, multiline=False, font_size="15sp",
            background_normal="", background_active="",
            background_color=(0, 0, 0, 0), foreground_color=COR["tinta"],
            hint_text_color=COR["tinta3"], cursor_color=COR["acento"],
            padding=(0, dp(13), 0, dp(10)), write_tab=False)
        self.campo.bind(focus=self._foco)
        self.add_widget(self.campo)

    def _foco(self, _campo, focado):
        self.cor_borda = COR["acento"] if focado else COR["borda"]


# ════════════════════════════════════════════════════════════════════
# INDICADORES
# ════════════════════════════════════════════════════════════════════
class BarraProgresso(Widget):
    """Barra fina e arredondada, com preenchimento animado."""

    valor = NumericProperty(0.0)

    def __init__(self, cor=None, cor_trilho=None, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(8))
        super().__init__(**kwargs)
        self.cor = cor or COR["acento"]
        self.cor_trilho = cor_trilho or COR["superficie_alt"]
        self.bind(pos=self._desenhar, size=self._desenhar, valor=self._desenhar)

    def animar(self, alvo, duracao=0.6):
        Animation.cancel_all(self, "valor")
        Animation(valor=max(0.0, min(1.0, alvo)), duration=duracao,
                  t="out_cubic").start(self)

    def _desenhar(self, *_):
        self.canvas.clear()
        if self.width <= 1:
            return
        r = self.height / 2
        with self.canvas:
            Color(*self.cor_trilho)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[r])
            w = self.width * self.valor
            if w > 0.5:
                Color(*self.cor)
                RoundedRectangle(pos=self.pos, size=(max(w, self.height), self.height),
                                 radius=[r])


class BarraDominio(BarraProgresso):
    def __init__(self, **kwargs):
        kwargs.setdefault("height", dp(7))
        super().__init__(**kwargs)


class AnelDia(FloatLayout):
    """Anel de progresso com um número e uma legenda no centro."""

    fracao = NumericProperty(0.0)

    def __init__(self, cor_arco=None, cor_trilho=None, cor_texto=None,
                 espessura=dp(9), tamanho_numero="30sp", **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(112), dp(112)))
        super().__init__(**kwargs)
        self.cor_arco = cor_arco or COR["acento"]
        self.cor_trilho = cor_trilho or COR["superficie_alt"]
        self.espessura = espessura
        cor_texto = cor_texto or COR["tinta"]

        self.numero = Label(text="", font_size=tamanho_numero, bold=True,
                            color=cor_texto, size_hint=(1, None), height=dp(38),
                            pos_hint={"center_x": 0.5, "center_y": 0.56})
        self.legenda = Label(text="", font_size="11sp", color=cor_texto,
                             size_hint=(1, None), height=dp(16),
                             pos_hint={"center_x": 0.5, "center_y": 0.32})
        self.legenda.opacity = 0.8
        self.add_widget(self.numero)
        self.add_widget(self.legenda)
        self.bind(pos=self._desenhar, size=self._desenhar, fracao=self._desenhar)

    def definir(self, feitos, total, legenda=None):
        """Mostra o que falta: é isso que decide se o estudante começa agora."""
        restante = max(0, total - feitos)
        self.mostrar((feitos / total) if total else 1.0, str(restante),
                     legenda or ("para hoje" if restante else "em dia"))

    def mostrar(self, fracao, numero, legenda):
        self.numero.text = numero
        self.legenda.text = legenda
        self.fracao = 0.0
        Animation(fracao=max(0.0, min(1.0, fracao)), duration=0.9,
                  t="out_cubic").start(self)

    def _desenhar(self, *_):
        self.canvas.before.clear()
        lado = min(self.width, self.height)
        if lado <= 1:
            return
        cx, cy = self.center
        r = lado / 2 - self.espessura / 2 - dp(1)
        with self.canvas.before:
            Color(*self.cor_trilho)
            Line(circle=(cx, cy, r), width=self.espessura / 2)
            if self.fracao > 0.003:
                Color(*self.cor_arco)
                Line(circle=(cx, cy, r, 0, 360 * self.fracao),
                     width=self.espessura / 2, cap="round")


class BarraEstagios(Widget):
    """Barra segmentada pelos quatro estágios de memória."""

    avanco = NumericProperty(0.0)

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(14))
        super().__init__(**kwargs)
        self.contagem = {}
        self.bind(pos=self._desenhar, size=self._desenhar, avanco=self._desenhar)

    def animar(self, contagem):
        self.contagem = contagem
        self.avanco = 0.0
        Animation(avanco=1.0, duration=0.8, t="out_cubic").start(self)

    def _desenhar(self, *_):
        self.canvas.clear()
        if not self.contagem or self.width <= 1:
            return
        ordem = [k for k in ("consolidado", "firmando", "aprendendo", "novo")
                 if self.contagem.get(k)]
        total = sum(self.contagem.values()) or 1
        vao = dp(3)
        util = self.width - vao * (len(ordem) - 1)
        r = self.height / 2
        pequeno = (dp(2), dp(2))
        x = self.x
        with self.canvas:
            for i, chave in enumerate(ordem):
                w = util * self.contagem[chave] / total
                if i == len(ordem) - 1:
                    w = self.right - x
                visivel = w * self.avanco
                if visivel < 1:
                    x += w + vao
                    continue
                Color(*COR_ESTAGIO[chave])
                primeiro, ultimo = i == 0, i == len(ordem) - 1
                raios = [(r, r) if primeiro else pequeno,
                         (r, r) if ultimo else pequeno,
                         (r, r) if ultimo else pequeno,
                         (r, r) if primeiro else pequeno]
                RoundedRectangle(pos=(x, self.y), size=(visivel, self.height),
                                 radius=raios)
                x += w + vao


class ReguaCalibracao(Widget):
    """Duas marcas numa régua: o que você acha que sabe e o que acerta."""

    avanco = NumericProperty(0.0)

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(64))
        super().__init__(**kwargs)
        self.confianca = 0.0
        self.acerto = 0.0
        self._rotulos = []
        self.bind(pos=self._desenhar, size=self._desenhar, avanco=self._desenhar)

    def animar(self, confianca, acerto):
        self.confianca, self.acerto = confianca, acerto
        self.avanco = 0.0
        Animation(avanco=1.0, duration=0.9, t="out_cubic").start(self)

    def _desenhar(self, *_):
        self.canvas.clear()
        for r in self._rotulos:
            self.remove_widget(r)
        self._rotulos = []
        if self.width <= 1:
            return
        m = dp(10)
        util = self.width - 2 * m
        y = self.y + self.height / 2
        cx = self.x + m + util * self.confianca * self.avanco
        ax = self.x + m + util * self.acerto * self.avanco
        with self.canvas:
            Color(*COR["superficie_alt"])
            RoundedRectangle(pos=(self.x + m, y - dp(3)), size=(util, dp(6)),
                             radius=[dp(3)])
            if abs(cx - ax) > 2:
                Color(*COR["ambar"])
                RoundedRectangle(pos=(min(cx, ax), y - dp(3)),
                                 size=(abs(cx - ax), dp(6)), radius=[dp(3)])
            for px, cor in ((ax, COR["acento"]), (cx, COR["indigo"])):
                Color(*COR["branco"])
                RoundedRectangle(pos=(px - dp(9), y - dp(9)), size=(dp(18), dp(18)),
                                 radius=[dp(9)])
                Color(*cor)
                RoundedRectangle(pos=(px - dp(6.5), y - dp(6.5)),
                                 size=(dp(13), dp(13)), radius=[dp(6.5)])
        for px, texto, cor, dy in ((ax, "acerto", COR["acento"], -dp(20)),
                                   (cx, "confiança", COR["indigo"], dp(20))):
            r = Label(text=texto, font_size="11sp", bold=True, color=cor,
                      size_hint=(None, None), size=(dp(80), dp(16)),
                      center=(px, y + dy))
            self.add_widget(r)
            self._rotulos.append(r)


class Constancia(Widget):
    """28 dias de estudo, uma barra por dia; hoje em âmbar.

    Sem contador de ofensiva em destaque: sequência longa vira dívida, e
    quebrar depois de semanas desanima mais do que motiva.
    """

    avanco = NumericProperty(0.0)

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(52))
        super().__init__(**kwargs)
        self.dados = []
        self.bind(pos=self._desenhar, size=self._desenhar, avanco=self._desenhar)

    def animar(self, dados):
        self.dados = dados
        self.avanco = 0.0
        Animation(avanco=1.0, duration=0.8, t="out_cubic").start(self)

    def _desenhar(self, *_):
        self.canvas.clear()
        if self.width <= 1 or not self.dados:
            return
        n = len(self.dados)
        passo = self.width / n
        largura = max(dp(3), passo * 0.56)
        pico = max((v for _, v in self.dados), default=0) or 1
        hoje = date.today().isoformat()
        with self.canvas:
            for i, (dia, valor) in enumerate(self.dados):
                x = self.x + i * passo + (passo - largura) / 2
                if valor:
                    h = max(largura, (self.height - dp(4)) * min(1, valor / pico) * self.avanco)
                    Color(*(COR["ambar"] if dia == hoje else COR["acento"]))
                else:
                    h = largura
                    Color(*COR["superficie_alt"])
                RoundedRectangle(pos=(x, self.y), size=(largura, h),
                                 radius=[largura / 2])


# ════════════════════════════════════════════════════════════════════
# ESTRUTURA DE TELA
# ════════════════════════════════════════════════════════════════════
class Cabecalho(BoxLayout):
    """Topo das telas internas: voltar, título e uma ação opcional."""

    def __init__(self, titulo, ao_voltar=None, acao=None, subtitulo="",
                 icone_voltar="voltar", **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(64))
        kwargs.setdefault("padding", (dp(6), dp(8), dp(12), dp(8)))
        kwargs.setdefault("spacing", dp(4))
        super().__init__(**kwargs)
        if ao_voltar is not None:
            self.botao_voltar = BotaoIcone(icone_voltar, pos_hint={"center_y": 0.5})
            self.botao_voltar.bind(on_release=lambda *_: ao_voltar())
            self.add_widget(self.botao_voltar)
        else:
            self.add_widget(espacador(largura=dp(10)))

        textos = BoxLayout(orientation="vertical", padding=(dp(4), dp(2)))
        textos.add_widget(rotulo(titulo, "19sp", COR["tinta"], negrito=True,
                                 vertical="bottom" if subtitulo else "middle"))
        if subtitulo:
            textos.add_widget(rotulo(subtitulo, "12.5sp", COR["tinta3"], vertical="top"))
        self.add_widget(textos)
        if acao is not None:
            acao.pos_hint = {"center_y": 0.5}
            self.add_widget(acao)


class ItemNavegacao(ButtonBehavior, BoxLayout):
    def __init__(self, chave, icone, texto, **kwargs):
        super().__init__(orientation="vertical", padding=(0, dp(8), 0, dp(6)),
                         spacing=dp(2), **kwargs)
        self.chave = chave
        caixa = FloatLayout(size_hint_y=None, height=dp(32))
        self.icone = Icone(icone, tamanho=dp(20), color=COR["tinta3"],
                           pos_hint={"center_x": 0.5, "center_y": 0.5})
        caixa.add_widget(self.icone)
        self.add_widget(caixa)
        self.rotulo = Label(text=texto, font_size="11.5sp", color=COR["tinta3"],
                            size_hint_y=None, height=dp(16))
        self.add_widget(self.rotulo)

    def ativar(self, ativo):
        cor = COR["acento_escuro"] if ativo else COR["tinta3"]
        self.icone.color = cor
        self.rotulo.color = cor
        self.rotulo.bold = ativo


class BarraNavegacao(FloatLayout):
    """Navegação inferior, ao alcance do polegar.

    A pílula atrás do ícone desliza até a aba escolhida: o movimento mostra
    de onde você saiu e para onde foi, em vez de só trocar a cor.
    """

    pilula_x = NumericProperty(-1000.0)
    ALTURA = dp(70)

    ITENS = [
        ("inicio",  "inicio",  "Início"),
        ("estudo",  "estudo",  "Estudo"),
        ("cartas",  "cartas",  "Cards"),
        ("pratica", "pratica", "Prática"),
        ("tutor",   "tutor",   "Tutor"),
    ]

    def __init__(self, ao_escolher, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", self.ALTURA)
        super().__init__(**kwargs)
        self.ao_escolher = ao_escolher
        self.ativa = None
        with self.canvas.before:
            Color(*COR["superficie"])
            self._fundo = Rectangle()
            Color(*COR["borda"])
            self._linha = Rectangle()
            Color(*COR["acento_suave"])
            self._pilula = RoundedRectangle(radius=[dp(16)])
        self.faixa = BoxLayout(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.itens = {}
        self._animando = False
        for chave, icone, texto in self.ITENS:
            item = ItemNavegacao(chave, icone, texto)
            item.bind(on_release=lambda it: self.ao_escolher(it.chave))
            # A posição de cada aba só é conhecida depois do layout (e muda
            # se a tela girar); a pílula acompanha em vez de ficar onde o
            # item estava antes de ser posicionado.
            item.bind(pos=self._reposicionar, size=self._reposicionar)
            self.faixa.add_widget(item)
            self.itens[chave] = item
        self.add_widget(self.faixa)
        self.bind(pos=self._desenhar, size=self._desenhar, pilula_x=self._desenhar)

    def _reposicionar(self, *_):
        if self.ativa in self.itens and not self._animando:
            self.pilula_x = self.itens[self.ativa].center_x

    def _desenhar(self, *_):
        self._fundo.pos = self.pos
        self._fundo.size = self.size
        self._linha.pos = (self.x, self.top - dp(1))
        self._linha.size = (self.width, dp(1))
        self._pilula.size = (dp(58), dp(32))
        self._pilula.pos = (self.pilula_x - dp(29), self.top - dp(40))

    def selecionar(self, chave, animar=True):
        self.ativa = chave
        for k, item in self.itens.items():
            item.ativar(k == chave)
        item = self.itens.get(chave)
        if item is None:
            return

        def mover(_dt):
            destino = item.center_x
            Animation.cancel_all(self, "pilula_x")
            if animar and self.pilula_x > 0:
                self._animando = True
                anim = Animation(pilula_x=destino, duration=0.32, t="out_cubic")
                anim.bind(on_complete=self._fim_animacao)
                anim.start(self)
            else:
                self._animando = False
                self.pilula_x = destino
        Clock.schedule_once(mover, 0)

    def _fim_animacao(self, *_):
        self._animando = False
        self._reposicionar()


def _hexagono(cx, cy, r):
    pontos = []
    for i in range(7):
        ang = math.radians(60 * i + 30)
        pontos += [cx + r * math.cos(ang), cy + r * math.sin(ang)]
    return pontos


def decorar_com_moleculas(superficie, cor=(1, 1, 1, 0.10)):
    """Anéis hexagonais discretos no canto da superfície — a marca do app.

    São desenhados no próprio canvas da superfície, logo depois do fundo:
    ficam atrás do conteúdo, acompanham as animações dela e, calculados a
    partir das bordas dela, nunca vazam para fora do cartão.
    """
    with superficie.canvas.before:
        Color(*cor)
        aneis = [Line(width=dp(1.4)) for _ in range(3)]
        circulo = Line(width=dp(1.1))

    def atualizar(*_):
        r = dp(26)
        dx = r * math.sqrt(3)
        # metade da largura do hexágono é r·cos30; a margem mantém o anel
        # longe do canto arredondado
        cx = superficie.right - dp(18) - r * 0.866
        cy = superficie.top - dp(16) - r
        centros = ((cx, cy), (cx - dx, cy), (cx - dx / 2, cy - r * 1.5))
        for anel, (x, y) in zip(aneis, centros):
            anel.points = _hexagono(x, y, r)
        circulo.circle = (cx, cy, r * 0.55)

    superficie.bind(pos=atualizar, size=atualizar)
    atualizar()
