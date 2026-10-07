"""Peças visuais da versão mobile.

Tudo aqui nasce de uma base só, a Superficie: fundo arredondado, sombra
suave opcional, borda opcional e três propriedades de movimento — escala
(resposta ao toque), escala horizontal (o card que vira) e deslocamento
vertical (a entrada escalonada das seções). Assim cartões, botões e
etiquetas se mexem do mesmo jeito, e a interface parece uma coisa só.

As animações são curtas e comunicam algo: o botão afunda ao toque (foi
registrado), as seções sobem ao entrar (a tela carregou), as barras
crescem até o valor real (quanto você domina). Nada anima por enfeite —
e, com "reduzir animações" ligado, tudo vira mudança instantânea.

Regras de acessibilidade que valem para todas as peças:
- alvos de toque com pelo menos 44 dp (48 nos botões de ícone);
- caixas que contêm texto crescem com a escala de texto (`dpt`);
- no alto contraste, bordas visíveis substituem as sombras.
"""

from datetime import date

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import (Color, Line, PopMatrix, PushMatrix, Rectangle,
                           RoundedRectangle, Scale, Translate)
from kivy.metrics import Metrics, dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from mobile.icones import Icone  # noqa: F401  (reexportado para as telas)
from mobile.tema import (COR, COR_ESTAGIO, ESTILO_TEXTO, RAIO_BOTAO, RAIO_CARTAO,
                         alto_contraste, dpt, movimento, texto_grande)


def _animar(alvo, duracao, t="out_cubic", **valores):
    """Anima, ou aplica na hora quando o estudante pediu menos movimento."""
    if not movimento():
        Animation.cancel_all(alvo, *valores)
        for chave, valor in valores.items():
            setattr(alvo, chave, valor)
        return None
    anim = Animation(duration=duracao, t=t, **valores)
    anim.start(alvo)
    return anim


def _afundar(widget, estado, escala_baixo, volta=0.2):
    """Resposta ao toque: o elemento afunda e volta."""
    if not movimento():
        return
    Animation.cancel_all(widget, "escala")
    if estado == "down":
        Animation(escala=escala_baixo, duration=0.07, t="out_quad").start(widget)
    else:
        Animation(escala=1.0, duration=volta, t="out_back").start(widget)


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
        # de pos e size: self.center ainda estaria desatualizado aqui
        self._escala.origin = (x + w / 2, y + h / 2)
        self._escala.x = max(0.001, self.escala * self.escala_x)
        self._escala.y = self.escala

        contraste = alto_contraste()
        if self.elevacao and self.cor_fundo[3] > 0 and not contraste:
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

        borda = self.cor_borda
        if borda[3] == 0 and contraste and self.elevacao and self.cor_fundo[3] > 0:
            # sem sombra, o cartão precisa de contorno para se separar do fundo
            borda = COR["borda"]
        self._cor_borda.rgba = borda
        self._borda.width = dp(1.4) if contraste else dp(1)
        if w > 2 and h > 2:
            self._borda.rounded_rectangle = (x, y, w, h, r)


def aparecer(widgets, atraso=0.05, passo=0.055):
    """Entrada escalonada: cada seção sobe e surge logo depois da anterior.

    Guia o olho de cima para baixo, na ordem de importância, sem prender o
    estudante esperando (menos de meio segundo no total).
    """
    if not movimento():
        for w in widgets:
            w.opacity = 1
            if hasattr(w, "desloc_y"):
                w.desloc_y = 0
        return
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
    scroll = ScrollView(do_scroll_x=False, bar_width=dp(4),
                        bar_color=(*COR["tinta3"][:3], 0.6),
                        bar_inactive_color=(*COR["tinta3"][:3], 0.2),
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
# TEXTO
# ════════════════════════════════════════════════════════════════════
class Texto(Label):
    """Label que quebra linha e cresce conforme o conteúdo."""

    def __init__(self, estilo="corpo", **kwargs):
        for chave, valor in ESTILO_TEXTO.get(estilo, {}).items():
            kwargs.setdefault(chave, valor)
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "top")
        kwargs.setdefault("line_height", 1.15)
        super().__init__(**kwargs)
        self.bind(width=self._largura, texture_size=self._altura)

    def _largura(self, *_):
        self.text_size = (self.width, None)

    def _altura(self, *_):
        self.height = self.texture_size[1]


def rotulo(texto, tamanho="14sp", cor=None, negrito=False, alinhar="left",
           vertical="middle", encurtar=False, **kwargs):
    """Label de uma linha que respeita o alinhamento dentro da sua caixa.

    Altura e largura fixas pedidas aqui são sempre de texto, então crescem
    com a escala de texto — senão a letra grande sairia cortada.
    """
    fator = max(1.0, Metrics.fontscale)
    if kwargs.get("size_hint_y", 1) is None and "height" in kwargs:
        kwargs["height"] *= fator
    if kwargs.get("size_hint_x", 1) is None and "width" in kwargs:
        kwargs["width"] *= fator
    r = Label(text=texto, font_size=tamanho, color=cor or COR["tinta"],
              bold=negrito, halign=alinhar, valign=vertical,
              shorten=encurtar, shorten_from="right", **kwargs)
    r.bind(size=lambda l, *_: setattr(l, "text_size", l.size))
    return r


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
        kwargs.setdefault("raio", dp(16))
        if auto_altura:
            kwargs["size_hint_y"] = None
        super().__init__(**kwargs)
        if auto_altura:
            self.bind(minimum_height=self.setter("height"))

    def on_state(self, _instancia, estado):
        _afundar(self, estado, 0.975)


class SeloIcone(Superficie):
    """Ícone dentro de um círculo colorido."""

    def __init__(self, icone, cor_fundo=None, cor_icone=None, tamanho=dp(40),
                 tamanho_icone=None, quadrado=False, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (tamanho, tamanho))
        raio = tamanho * 0.3 if quadrado else tamanho / 2
        super().__init__(cor_fundo=cor_fundo or COR["acento_suave"], raio=raio, **kwargs)
        self.icone = Icone(icone, tamanho=tamanho_icone or tamanho * 0.5,
                           color=cor_icone or COR["acento"], size_hint=(1, 1))
        self.add_widget(self.icone)


class Etiqueta(Superficie):
    """Pílula pequena e estática: ALTO, BAIXO, categoria, estágio."""

    def __init__(self, text, fundo, tinta, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("height", dpt(24))
        kwargs.setdefault("padding", (dp(10), 0))
        kwargs.setdefault("pos_hint", {"center_y": 0.5})
        super().__init__(cor_fundo=fundo, raio=kwargs["height"] / 2, **kwargs)
        self.rotulo = Label(text=text, font_size="12sp", bold=True, color=tinta)
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
        if "height" in kwargs:
            # a altura pedida é o mínimo; com texto grande, o botão cresce
            kwargs["height"] = max(kwargs["height"], dpt(kwargs["height"] / dp(1) * 0.86))
        else:
            kwargs["height"] = max(dp(52), dpt(46))
        kwargs.setdefault("raio", RAIO_BOTAO)
        kwargs.setdefault("padding", (dp(14), 0))
        kwargs.setdefault("spacing", dp(8))
        super().__init__(cor_fundo=fundo, **kwargs)
        if alto_contraste() and variante in ("claro", "neutro", "fantasma") and cor is None:
            self.cor_borda = COR["borda_forte"]

        if icone:
            # ícone e texto formam um grupo centralizado
            self.add_widget(Widget())
            self.icone = Icone(icone, tamanho=dp(18), color=tinta,
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
                                              0.45 if self.disabled else 1))

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
        _afundar(self, estado, 0.965, volta=0.18)


def titulo_pagina(titulo, subtitulo="", acao=None):
    """Título grande das abas principais, com subtítulo e ação opcional.

    A linha do título tem altura própria: dividir a caixa ao meio cortava
    o acento de títulos como "Prática".
    """
    linha = BoxLayout(size_hint_y=None, height=dpt(60))
    textos = BoxLayout(orientation="vertical")
    textos.add_widget(rotulo(titulo, "26sp", COR["tinta"], negrito=True,
                             vertical="bottom", size_hint_y=None, height=dp(38)))
    if subtitulo:
        r = rotulo(subtitulo, "13.5sp", COR["tinta3"], vertical="top",
                   size_hint_y=None, height=dp(22))
        textos.add_widget(r)
        linha.subtitulo = r
    linha.add_widget(textos)
    if acao is not None:
        acao.pos_hint = {"center_y": 0.5}
        linha.add_widget(acao)
    return linha


class BotaoIcone(ButtonBehavior, Superficie):
    """Botão redondo só com ícone (voltar, fechar, embaralhar, enviar).

    `descricao` diz o que o botão faz; é o texto que um leitor de tela
    leria, e o que aparece no teste automatizado.
    """

    def __init__(self, icone, cor_icone=None, cor=None, tamanho=dp(48),
                 descricao="", **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (tamanho, tamanho))
        super().__init__(cor_fundo=cor or COR["transparente"],
                         raio=tamanho / 2, **kwargs)
        self.descricao = descricao or icone
        self.icone = Icone(icone, tamanho=dp(22), color=cor_icone or COR["tinta"],
                           size_hint=(1, 1))
        self.add_widget(self.icone)

    def on_state(self, _instancia, estado):
        _afundar(self, estado, 0.86, volta=0.22)


class Chip(ButtonBehavior, Superficie):
    """Etiqueta em pílula, selecionável — filtros e abas."""

    selecionado = BooleanProperty(False)

    def __init__(self, text, cor_ponto=None, **kwargs):
        altura = max(dp(44), dpt(38))
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("height", altura)
        kwargs.setdefault("padding", (dp(16), 0))
        kwargs.setdefault("spacing", dp(8))
        kwargs.setdefault("pos_hint", {"center_y": 0.5})
        super().__init__(raio=altura / 2, **kwargs)
        self.tem_ponto = cor_ponto is not None
        if self.tem_ponto:
            self.add_widget(Ponto(cor_ponto, tamanho=dp(8)))
        self.rotulo = Label(text=text, font_size="14sp", bold=True,
                            size_hint_x=None)
        self.rotulo.bind(texture_size=self._medir)
        self.add_widget(self.rotulo)
        self.bind(selecionado=self._aplicar)
        self._aplicar()

    def _medir(self, *_):
        self.rotulo.width = self.rotulo.texture_size[0]
        extra = dp(16) if self.tem_ponto else 0
        self.width = self.rotulo.width + dp(32) + extra

    def _aplicar(self, *_):
        if self.selecionado:
            self.cor_fundo = COR["tinta"]
            self.cor_borda = COR["tinta"]
            self.rotulo.color = COR["branco"]
        else:
            self.cor_fundo = COR["superficie"]
            self.cor_borda = COR["borda_forte"] if alto_contraste() else COR["borda"]
            self.rotulo.color = COR["tinta2"]

    def on_state(self, _instancia, estado):
        _afundar(self, estado, 0.95, volta=0.18)


class Alternador(ButtonBehavior, Superficie):
    """Linha de ajuste com chave liga/desliga, tocável em toda a extensão.

    O estado também vai em texto ("Ligado"), para não depender só da cor
    nem da posição da bolinha.
    """

    ativo = BooleanProperty(False)

    def __init__(self, titulo, descricao="", ativo=False, icone=None,
                 ao_mudar=None, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("padding", (dp(14), dp(12), dp(14), dp(12)))
        kwargs.setdefault("spacing", dp(12))
        kwargs.setdefault("raio", dp(14))
        kwargs.setdefault("cor_fundo", COR["transparente"])
        super().__init__(**kwargs)
        self.ao_mudar = ao_mudar
        if icone:
            self.add_widget(Icone(icone, tamanho=dp(22), color=COR["tinta2"],
                                  pos_hint={"center_y": 0.5}))
        textos = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        textos.bind(minimum_height=textos.setter("height"))
        textos.add_widget(Texto(text=titulo, estilo="corpo", bold=True))
        if descricao:
            textos.add_widget(Texto(text=descricao, estilo="apoio"))
        self.estado_texto = Texto(text="", estilo="micro")
        textos.add_widget(self.estado_texto)
        self.add_widget(textos)
        self.chave = Widget(size_hint=(None, None), size=(dp(48), dp(28)),
                            pos_hint={"center_y": 0.5})
        self.add_widget(self.chave)
        self.bind(minimum_height=lambda *_: setattr(
            self, "height", max(dp(56), self.minimum_height)))
        self.chave.bind(pos=self._desenhar, size=self._desenhar)
        self.bind(ativo=self._desenhar)
        self.bind(disabled=lambda *_: setattr(self, "opacity", 0.5 if self.disabled else 1))
        self.descricao = titulo
        self.ativo = ativo
        self._desenhar()

    def on_release(self):
        self.ativo = not self.ativo
        if self.ao_mudar:
            self.ao_mudar(self.ativo)

    def _desenhar(self, *_):
        c = self.chave
        self.estado_texto.text = "Ligado" if self.ativo else "Desligado"
        c.canvas.clear()
        with c.canvas:
            Color(*(COR["acento"] if self.ativo else COR["superficie_alt"]))
            RoundedRectangle(pos=c.pos, size=c.size, radius=[c.height / 2])
            Color(*(COR["acento"] if self.ativo else COR["tinta3"]))
            Line(rounded_rectangle=(c.x, c.y, c.width, c.height, c.height / 2),
                 width=dp(1.1))
            Color(*COR["branco"])
            d = c.height - dp(8)
            x = c.right - d - dp(4) if self.ativo else c.x + dp(4)
            RoundedRectangle(pos=(x, c.y + dp(4)), size=(d, d), radius=[d / 2])
            if not self.ativo:
                Color(*COR["tinta3"])
                Line(circle=(x + d / 2, c.y + dp(4) + d / 2, d / 2), width=dp(1))

    def on_state(self, _instancia, estado):
        _afundar(self, estado, 0.985)


class Segmentado(Superficie):
    """Escolha única entre poucas opções (tamanho do texto, da sessão...).

    Com texto grande, as opções passam para duas colunas em vez de
    espremer cada rótulo até quebrar no meio da palavra.
    """

    def __init__(self, opcoes, valor, ao_escolher, **kwargs):
        from kivy.uix.gridlayout import GridLayout

        colunas = 2 if texto_grande() and len(opcoes) > 2 else len(opcoes)
        linhas = -(-len(opcoes) // colunas)
        altura_botao = max(dp(44), dpt(38))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", linhas * altura_botao + (linhas - 1) * dp(4) + dp(8))
        kwargs.setdefault("padding", dp(4))
        super().__init__(cor_fundo=COR["superficie_alt"], raio=dp(14), **kwargs)
        if alto_contraste():
            self.cor_borda = COR["borda_forte"]
        self.ao_escolher = ao_escolher
        self.botoes = {}
        grade = GridLayout(cols=colunas, spacing=dp(4))
        for chave, texto in opcoes:
            botao = Botao(texto, variante="claro", height=dp(44), raio=dp(11),
                          tamanho_fonte="13.5sp", padding=(dp(4), 0))
            botao.size_hint_y = 1
            botao.bind(on_release=lambda *_, k=chave: self.escolher(k))
            grade.add_widget(botao)
            self.botoes[chave] = botao
        self.add_widget(grade)
        self._marcar(valor)

    def _marcar(self, valor):
        self.valor = valor
        for chave, botao in self.botoes.items():
            ativo = chave == valor
            botao.pintar(COR["superficie"] if ativo else COR["transparente"],
                         COR["tinta"] if ativo else COR["tinta2"])
            botao.elevacao = 1 if ativo else 0
            botao.cor_borda = (COR["tinta"] if ativo and alto_contraste()
                               else COR["transparente"])
            botao.rotulo.bold = ativo

    def escolher(self, valor):
        self._marcar(valor)
        self.ao_escolher(valor)


# ════════════════════════════════════════════════════════════════════
# CAMPOS
# ════════════════════════════════════════════════════════════════════
class CampoTexto(Superficie):
    """Campo arredondado; com `lupa=True` vira busca."""

    def __init__(self, dica="", lupa=False, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", max(dp(52), dpt(46)))
        kwargs.setdefault("padding", (dp(14), dp(2), dp(8), dp(2)))
        kwargs.setdefault("spacing", dp(10))
        super().__init__(cor_fundo=COR["superficie"],
                         cor_borda=COR["borda_forte"] if alto_contraste() else COR["borda"],
                         raio=dp(16), **kwargs)
        if lupa:
            self.add_widget(Icone("busca", tamanho=dp(20), color=COR["tinta3"],
                                  pos_hint={"center_y": 0.5}))
        self.campo = TextInput(
            hint_text=dica, multiline=False, font_size="15.5sp",
            background_normal="", background_active="",
            background_color=(0, 0, 0, 0), foreground_color=COR["tinta"],
            hint_text_color=COR["tinta3"], cursor_color=COR["acento"],
            cursor_width=dp(2), write_tab=False)
        # texto centrado na vertical em qualquer escala de fonte
        self.campo.bind(size=self._centrar, line_height=self._centrar)
        self.campo.bind(focus=self._foco)
        self.add_widget(self.campo)

    def _centrar(self, *_):
        folga = max(0, (self.campo.height - self.campo.line_height) / 2)
        self.campo.padding = (0, folga, 0, folga)

    def _foco(self, _campo, focado):
        # foco visível: borda mais grossa e na cor de ação
        self.cor_borda = COR["acento"] if focado else (
            COR["borda_forte"] if alto_contraste() else COR["borda"])
        self._borda.width = dp(2) if focado else dp(1)


# ════════════════════════════════════════════════════════════════════
# MENSAGENS E ESTADOS
# ════════════════════════════════════════════════════════════════════
AVISOS = {
    #            ícone     texto            fundo
    "info":     ("info",   "indigo",        "indigo_suave"),
    "sucesso":  ("check",  "acento_escuro", "acento_suave"),
    "atencao":  ("alerta", "ambar",         "ambar_suave"),
    "erro":     ("alerta", "rubro",         "rubro_suave"),
}


class Aviso(Superficie):
    """Mensagem curta no fluxo da tela: informação, sucesso, atenção, erro.

    Sempre com ícone e texto, nunca só cor, para quem não distingue cores.
    """

    def __init__(self, texto, tipo="info", titulo=None, **kwargs):
        icone, tinta, fundo = AVISOS.get(tipo, AVISOS["info"])
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("padding", (dp(14), dp(12)))
        kwargs.setdefault("spacing", dp(12))
        super().__init__(cor_fundo=COR[fundo], raio=dp(14), **kwargs)
        if alto_contraste():
            self.cor_borda = COR[tinta]
        caixa = BoxLayout(orientation="vertical", size_hint=(None, None),
                          size=(dp(22), dp(22)), pos_hint={"top": 1})
        caixa.add_widget(Icone(icone, tamanho=dp(20), color=COR[tinta], size_hint=(1, 1)))
        self.add_widget(caixa)
        textos = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        textos.bind(minimum_height=textos.setter("height"))
        if titulo:
            textos.add_widget(Texto(text=titulo, estilo="corpo", bold=True, color=COR[tinta]))
        self.texto = Texto(text=texto, estilo="apoio", color=COR["tinta"])
        textos.add_widget(self.texto)
        self.add_widget(textos)
        self.bind(minimum_height=self.setter("height"))


class Digitando(Superficie):
    """Indicador de que o tutor está respondendo: três pontos que pulsam.

    Com movimento reduzido, vira um texto parado.
    """

    def __init__(self, texto="Pensando", **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(76), dp(44)))
        super().__init__(cor_fundo=COR["superficie"], raio=dp(20), elevacao=1,
                         padding=(dp(18), 0), spacing=dp(7), **kwargs)
        self.descricao = texto
        if not movimento():
            self.width = dp(130)
            self.add_widget(rotulo(f"{texto}…", "14sp", COR["tinta2"]))
            return
        self.pontos = []
        for i in range(3):
            ponto = Ponto(COR["tinta3"], tamanho=dp(8))
            self.add_widget(ponto)
            self.pontos.append(ponto)
            Clock.schedule_once(lambda _dt, p=ponto: self._pulsar(p), i * 0.16)

    def _pulsar(self, ponto):
        anim = (Animation(opacity=0.25, duration=0.4, t="in_out_sine")
                + Animation(opacity=1, duration=0.4, t="in_out_sine"))
        anim.repeat = True
        anim.start(ponto)

    def parar(self):
        for ponto in getattr(self, "pontos", []):
            Animation.cancel_all(ponto)


def botao_ouvir(app, obter_texto, rotulo_botao="Ouvir"):
    """Botão de leitura em voz alta, ou None se a voz estiver desligada.

    Recebe uma função, e não o texto, para ler o que estiver na tela no
    momento do toque.
    """
    if not app.voz_ligada():
        return None
    botao = Botao(rotulo_botao, variante="neutro", icone="voz", height=dp(44),
                  tamanho_fonte="14sp", size_hint_x=None, padding=(dp(14), 0))
    # rótulo + ícone (caixa de 1,25 × 18 dp) + três vãos de 8 dp + margens
    botao.rotulo.bind(texture_size=lambda r, *_: setattr(
        botao, "width", r.texture_size[0] + dp(22.5) + dp(24) + dp(28) + dp(4)))
    botao.descricao = "Ler em voz alta"
    botao.bind(on_release=lambda *_: app.falar(obter_texto()))
    return botao


def linha_acoes(*widgets):
    """Fileira de botões pequenos alinhados à esquerda (ouvir, Libras)."""
    widgets = [w for w in widgets if w is not None]
    if not widgets:
        return None
    linha = BoxLayout(size_hint_y=None, height=max(w.height for w in widgets),
                      spacing=dp(8))
    for w in widgets:
        linha.add_widget(w)
    linha.add_widget(Widget())
    return linha


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
        _animar(self, duracao, valor=max(0.0, min(1.0, alvo)))

    def _desenhar(self, *_):
        self.canvas.clear()
        if self.width <= 1:
            return
        r = self.height / 2
        with self.canvas:
            Color(*self.cor_trilho)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[r])
            if alto_contraste():
                Color(*COR["tinta3"])
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, r),
                     width=dp(0.8))
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
        self.legenda = Label(text="", font_size="11.5sp", color=cor_texto,
                             size_hint=(1, None), height=dp(16),
                             pos_hint={"center_x": 0.5, "center_y": 0.31})
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
        _animar(self, 0.9, fracao=max(0.0, min(1.0, fracao)))

    def _desenhar(self, *_):
        self.canvas.before.clear()
        lado = min(self.width, self.height)
        if lado <= 1:
            return
        # do pos e do size, não de self.center (ver Icone._desenhar)
        cx, cy = self.x + self.width / 2, self.y + self.height / 2
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
        _animar(self, 0.8, avanco=1.0)

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
        kwargs.setdefault("height", dpt(64))
        super().__init__(**kwargs)
        self.confianca = 0.0
        self.acerto = 0.0
        self._rotulos = []
        self.bind(pos=self._desenhar, size=self._desenhar, avanco=self._desenhar)

    def animar(self, confianca, acerto):
        self.confianca, self.acerto = confianca, acerto
        self.avanco = 0.0
        _animar(self, 0.9, avanco=1.0)

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
        deslocamento = dpt(20)
        for px, texto, cor, dy in ((ax, "acerto", COR["acento"], -deslocamento),
                                   (cx, "confiança", COR["indigo"], deslocamento)):
            r = Label(text=texto, font_size="12sp", bold=True, color=cor,
                      size_hint=(None, None), size=(dpt(80), dpt(16)),
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
        _animar(self, 0.8, avanco=1.0)

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
        kwargs.setdefault("height", max(dp(64), dpt(58)))
        kwargs.setdefault("padding", (dp(4), dp(6), dp(12), dp(6)))
        kwargs.setdefault("spacing", dp(4))
        super().__init__(**kwargs)
        if ao_voltar is not None:
            self.botao_voltar = BotaoIcone(icone_voltar, pos_hint={"center_y": 0.5},
                                           descricao="Voltar")
            self.botao_voltar.bind(on_release=lambda *_: ao_voltar())
            self.add_widget(self.botao_voltar)
        else:
            self.add_widget(espacador(largura=dp(10)))

        textos = BoxLayout(orientation="vertical", padding=(dp(4), dp(2)))
        textos.add_widget(rotulo(titulo, "19sp", COR["tinta"], negrito=True,
                                 vertical="bottom" if subtitulo else "middle"))
        if subtitulo:
            textos.add_widget(rotulo(subtitulo, "13sp", COR["tinta3"], vertical="top"))
        self.add_widget(textos)
        if acao is not None:
            acao.pos_hint = {"center_y": 0.5}
            self.add_widget(acao)


class ItemNavegacao(ButtonBehavior, BoxLayout):
    def __init__(self, chave, icone, texto, **kwargs):
        super().__init__(orientation="vertical", padding=(0, dp(8), 0, dp(6)),
                         spacing=dp(2), **kwargs)
        self.chave = chave
        self.descricao = texto
        caixa = FloatLayout(size_hint_y=None, height=dp(32))
        self.icone = Icone(icone, tamanho=dp(22), color=COR["tinta3"],
                           pos_hint={"center_x": 0.5, "center_y": 0.5})
        caixa.add_widget(self.icone)
        self.add_widget(caixa)
        self.rotulo = Label(text=texto, font_size="12sp", color=COR["tinta3"],
                            size_hint_y=None, height=dpt(16))
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

    ITENS = [
        ("inicio",  "inicio",  "Início"),
        ("estudo",  "estudo",  "Estudo"),
        ("cartas",  "cartas",  "Cards"),
        ("pratica", "pratica", "Prática"),
        ("tutor",   "tutor",   "Tutor"),
    ]

    @staticmethod
    def altura():
        return dp(54) + dpt(16)

    def __init__(self, ao_escolher, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", self.altura())
        super().__init__(**kwargs)
        self.ao_escolher = ao_escolher
        self.ativa = None
        with self.canvas.before:
            Color(*COR["superficie"])
            self._fundo = Rectangle()
            Color(*(COR["borda_forte"] if alto_contraste() else COR["borda"]))
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
            item = self.itens[self.ativa]
            self.pilula_x = item.x + item.width / 2

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
            destino = item.x + item.width / 2
            Animation.cancel_all(self, "pilula_x")
            if animar and self.pilula_x > 0 and movimento():
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
