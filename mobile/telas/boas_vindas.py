"""Apresentação (tutorial) do primeiro acesso: quatro passos, sem obrigar ninguém.

1. O que é o app.
2. O que há em cada parte dele (as cinco abas).
3. Como ele ajuda a lembrar (o ciclo da revisão), para que o primeiro
   "quanto você acha que sabe?" não pareça estranho.
4. Ajustes de leitura e foco — oferecidos logo no começo, porque quem
   precisa de letra maior ou de alto contraste não deveria ter de
   atravessar o app inteiro até achar a tela de acessibilidade.

"Pular" leva direto ao Início. Concluir ou pular marca o tutorial como
visto (mobile/conta.py): no aparelho e, com conta Google, na conta, para
não aparecer de novo em nenhum aparelho. Dá para revê-lo na tela Conta.
"""

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from mobile import componentes as C
from mobile.tema import COR
from mobile.telas.acessibilidade import ajustes_foco, ajustes_leitura, ajustes_voz
from mobile.telas.base import TelaBase

SIMBOLO = Path(__file__).resolve().parents[2] / "assets" / "logo" / "simbolo.png"
TOTAL = 4
PARTES = [
    ("inicio", "Início", "A revisão do dia, o estado da sua memória e o que está mais frágil."),
    ("estudo", "Estudo", "Os marcadores, com faixa de referência, casos, imagens e fontes."),
    ("cartas", "Cards", "Pergunta de um lado, resposta do outro, para treinar a memória."),
    ("pratica", "Prática", "Quiz, casos clínicos com vários exames juntos e dois jogos."),
    ("tutor", "Tutor", "Tire dúvidas sobre os marcadores, como faria com um colega."),
]


class TelaBoasVindas(TelaBase):

    LARGURA_MAXIMA = 640   # dp, em tablet e computador

    def montar(self, passo=1, **_):
        self.passo = max(1, min(TOTAL, passo))
        raiz = BoxLayout(orientation="vertical", padding=(dp(20), dp(10), dp(20), dp(18)),
                         spacing=dp(12))

        topo = BoxLayout(size_hint_y=None, height=dp(48))
        pontos = BoxLayout(size_hint_x=None, width=dp(80), spacing=dp(8))
        for i in range(1, TOTAL + 1):
            pontos.add_widget(C.Ponto(COR["acento"] if i == self.passo else COR["borda_forte"],
                                      tamanho=dp(10 if i == self.passo else 8)))
        topo.add_widget(pontos)
        topo.add_widget(Widget())
        if self.passo < TOTAL:
            pular = C.Botao("Pular", variante="fantasma", height=dp(44), size_hint_x=None,
                            width=dp(84), tamanho_fonte="14.5sp")
            pular.bind(on_release=lambda *_: self._concluir())
            topo.add_widget(pular)
        raiz.add_widget(topo)

        scroll, col = C.coluna_rolavel(padding=(0, dp(4), 0, dp(8)), spacing=dp(14))
        {1: self._apresentacao, 2: self._partes, 3: self._como_funciona,
         4: self._ajustes}[self.passo](col)
        raiz.add_widget(scroll)

        acoes = BoxLayout(size_hint_y=None, height=max(dp(52), C.dpt(46)), spacing=dp(10))
        if self.passo > 1:
            voltar = C.Botao("Voltar", variante="neutro", size_hint_x=0.4)
            voltar.bind(on_release=lambda *_: self.preparar(passo=self.passo - 1))
            acoes.add_widget(voltar)
        ultimo = self.passo == TOTAL
        seguir = C.Botao("Começar a estudar" if ultimo else "Continuar", variante="primario",
                         icone=None if ultimo else "seta")
        seguir.bind(on_release=lambda *_: self._concluir() if ultimo
                    else self.preparar(passo=self.passo + 1))
        acoes.add_widget(seguir)
        raiz.add_widget(acoes)
        self.add_widget(raiz)
        C.aparecer(list(col.children)[::-1])

    # ── passos ──────────────────────────────────────────────────────
    def _apresentacao(self, col):
        caixa = AnchorLayout(size_hint_y=None, height=dp(150))
        caixa.add_widget(Image(source=str(SIMBOLO), size_hint=(None, None),
                               size=(dp(120), dp(120)), fit_mode="contain"))
        col.add_widget(caixa)
        col.add_widget(C.Texto(text="Marcadores bioquímicos, do valor ao diagnóstico",
                               estilo="display", halign="center"))
        col.add_widget(C.Texto(
            text=f"{len(self.app.marcadores)} marcadores de seis sistemas, com faixa de "
                 "referência, o que significa estar alto ou baixo, casos clínicos e "
                 "bibliografia para conferir.",
            estilo="corpo", halign="center", color=COR["tinta2"]))

    def _partes(self, col):
        col.add_widget(C.Texto(text="O que você encontra no app", estilo="display"))
        col.add_widget(C.Texto(text="Cada parte fica numa aba: embaixo, no celular; na "
                                    "lateral, no tablet e no computador.", estilo="apoio"))
        self._linhas(col, PARTES)

    def _linhas(self, col, itens):
        for icone, titulo, texto in itens:
            linha = C.Cartao(orientation="horizontal", spacing=dp(14), elevacao=0,
                             cor_fundo=COR["superficie"])
            linha.add_widget(C.SeloIcone(icone, cor_fundo=COR["acento_suave"],
                                         cor_icone=COR["acento_escuro"], tamanho=dp(44),
                                         quadrado=True, pos_hint={"top": 1}))
            textos = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
            textos.bind(minimum_height=textos.setter("height"))
            textos.add_widget(C.Texto(text=titulo, estilo="subtitulo"))
            textos.add_widget(C.Texto(text=texto, estilo="apoio"))
            linha.add_widget(textos)
            linha.bind(minimum_height=linha.setter("height"))
            col.add_widget(linha)

    def _como_funciona(self, col):
        col.add_widget(C.Texto(text="Como o app ajuda você a lembrar", estilo="display"))
        passos = [
            ("estudo", "Tente lembrar antes de ver",
             "Puxar da memória fixa mais do que reler a resposta."),
            ("info", "Diga o quanto tem certeza",
             "Comparar sua confiança com seus acertos mostra o que você acha que sabe."),
            ("calendario", "Cada marcador volta na hora certa",
             "Acertou, ele demora mais a voltar; errou, volta ainda hoje."),
        ]
        self._linhas(col, passos)

    def _ajustes(self, col):
        col.add_widget(C.Texto(text="Deixe a leitura do seu jeito", estilo="display"))
        col.add_widget(C.Texto(text="Dá para mudar depois em Acessibilidade, no Início.",
                               estilo="apoio"))
        leitura = C.Cartao(spacing=dp(12))
        ajustes_leitura(self.app, leitura)
        col.add_widget(leitura)
        voz = C.Cartao(spacing=dp(12))
        ajustes_voz(self.app, voz)
        col.add_widget(voz)
        foco = C.Cartao(spacing=dp(12))
        ajustes_foco(self.app, foco)
        col.add_widget(foco)

    def _concluir(self):
        """Concluir e pular dão no mesmo: o tutorial fica marcado como visto."""
        self.app.acesso.marcar_tutorial_visto()
        self.app.ir_para("inicio")
