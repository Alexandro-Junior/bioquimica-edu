"""Cards: recuperação rápida, com um card que vira de verdade.

A animação de virar não é enfeite: ela separa, com um gesto físico, o
momento de tentar lembrar do momento de conferir. A face da resposta é
escura, para que não haja dúvida de qual lado está à mostra.

Depois de virar, dois botões — "Não lembrei" e "Lembrei" — alimentam a
revisão espaçada. São dois, e não quatro como na revisão, para manter o
ritmo rápido que é a razão de ser deste modo.
"""

import random

from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from mobile import componentes as C
from mobile.tema import COR, dpt, movimento
from mobile.telas.base import TelaBase


class CartaoVirar(ButtonBehavior, C.Superficie):
    """Superfície tocável cujo retorno visual é o próprio giro."""


class TelaCartas(TelaBase):

    LARGURA_MAXIMA = 640   # dp, em tablet e computador

    def montar(self, **_):
        app = self.app
        self.cards = list(app.flashcards)
        self.indice = 0
        self.virado = False
        self.avaliados = set()

        raiz = BoxLayout(orientation="vertical", padding=(dp(16), dp(12), dp(16), dp(14)),
                         spacing=dp(12))

        embaralhar = C.BotaoIcone("embaralhar", cor=COR["superficie"], elevacao=1,
                                  descricao="Embaralhar os cards")
        embaralhar.bind(on_release=lambda *_: self._embaralhar())
        raiz.add_widget(C.titulo_pagina("Cards", "Toque no card para virar",
                                        acao=embaralhar))

        andamento = BoxLayout(size_hint_y=None, height=dpt(20), spacing=dp(12))
        self.barra = C.BarraProgresso(pos_hint={"center_y": 0.5})
        andamento.add_widget(self.barra)
        self.contador = C.rotulo("", "13sp", COR["tinta2"], negrito=True,
                                 alinhar="right", size_hint_x=None, width=dp(64))
        andamento.add_widget(self.contador)
        raiz.add_widget(andamento)

        self.cartao = CartaoVirar(orientation="vertical", padding=(dp(24), dp(22)),
                                  spacing=dp(10), raio=dp(28), elevacao=2,
                                  cor_fundo=COR["superficie"])
        self.cartao.bind(on_release=lambda *_: self._virar())
        self.cartao.descricao = "Virar o card"
        topo = BoxLayout(size_hint_y=None, height=dpt(26))
        self.etiqueta = C.Etiqueta("Pergunta", COR["acento_suave"], COR["acento_escuro"])
        topo.add_widget(self.etiqueta)
        topo.add_widget(Widget())
        self.cartao.add_widget(topo)
        self.cartao.add_widget(Widget())
        self.texto_face = C.Texto(text="", estilo="titulo", halign="center")
        self.cartao.add_widget(self.texto_face)
        self.cartao.add_widget(Widget())
        dica = BoxLayout(size_hint_y=None, height=dpt(22), spacing=dp(6))
        dica.add_widget(Widget())
        self.icone_dica = C.Icone("repetir", tamanho=dp(14), color=COR["tinta3"],
                                  pos_hint={"center_y": 0.5})
        dica.add_widget(self.icone_dica)
        self.texto_dica = Label(text="", font_size="12.5sp", color=COR["tinta3"],
                                size_hint_x=None)
        self.texto_dica.bind(texture_size=lambda r, *_: setattr(r, "width", r.texture_size[0]))
        dica.add_widget(self.texto_dica)
        dica.add_widget(Widget())
        self.cartao.add_widget(dica)
        raiz.add_widget(self.cartao)

        ouvir = C.botao_ouvir(self.app, self._texto_da_face)
        if ouvir is not None:
            raiz.add_widget(C.linha_acoes(ouvir))

        self.aviso = C.rotulo("", "13sp", COR["acento_escuro"], negrito=True,
                              alinhar="center", size_hint_y=None, height=dp(18))
        raiz.add_widget(self.aviso)

        self.area_avaliacao = BoxLayout(orientation="vertical", size_hint_y=None,
                                        height=0, spacing=dp(8))
        raiz.add_widget(self.area_avaliacao)

        anterior = C.Botao("Anterior", variante="neutro", icone="voltar", height=dp(50),
                           tamanho_fonte="14.5sp")
        anterior.bind(on_release=lambda *_: self._mover(-1))
        proximo = C.Botao("Próximo", variante="neutro", icone="avancar", height=dp(50),
                          tamanho_fonte="14.5sp")
        navegacao = BoxLayout(size_hint_y=None, height=anterior.height, spacing=dp(10))
        proximo.bind(on_release=lambda *_: self._mover(1))
        navegacao.add_widget(anterior)
        navegacao.add_widget(proximo)
        raiz.add_widget(navegacao)

        self.add_widget(raiz)
        self._atualizar()

    # ── face do card ────────────────────────────────────────────────
    def _texto_da_face(self):
        if not self.cards:
            return ""
        card = self.cards[self.indice]
        return card["resposta"] if self.virado else card["pergunta"]

    def _pintar_face(self):
        if not self.cards:
            self.texto_face.text = "Nenhum card disponível"
            self.texto_dica.text = "verifique data/flashcards.json"
            return
        card = self.cards[self.indice]
        if self.virado:
            self.cartao.cor_fundo = COR["tinta"]
            self.etiqueta.pintar("Resposta", (1, 1, 1, 0.14), COR["branco"])
            self.texto_face.text = card["resposta"]
            self.texto_face.color = COR["branco"]
            self.texto_face.bold = False
            self.texto_face.font_size = "19sp"
            self.icone_dica.color = (1, 1, 1, 0.55)
            self.texto_dica.color = (1, 1, 1, 0.55)
            self.texto_dica.text = "toque para voltar à pergunta"
        else:
            self.cartao.cor_fundo = COR["superficie"]
            self.etiqueta.pintar("Pergunta", COR["acento_suave"], COR["acento_escuro"])
            self.texto_face.text = card["pergunta"]
            self.texto_face.color = COR["tinta"]
            self.texto_face.bold = True
            self.texto_face.font_size = "23sp"
            self.icone_dica.color = COR["tinta3"]
            self.texto_dica.color = COR["tinta3"]
            self.texto_dica.text = "toque para ver a resposta"

    def _atualizar(self):
        total = len(self.cards)
        if total:
            self.contador.text = f"{self.indice + 1} / {total}"
            self.barra.animar((self.indice + 1) / total, duracao=0.35)
        else:
            self.contador.text = ""
        self.cartao.escala_x = 1.0
        self._pintar_face()
        self._montar_avaliacao()

    def _virar(self):
        if not self.cards:
            return
        self.virado = not self.virado
        self.app.parar_fala()
        # O estado muda na hora; só a face espera o meio do giro para trocar,
        # exatamente quando o card está de lado e nenhuma face aparece.
        self._montar_avaliacao()
        if not movimento():
            self._pintar_face()
            return
        Animation.cancel_all(self.cartao, "escala_x")
        ida = Animation(escala_x=0.0, duration=0.13, t="in_quad")

        def meio(*_):
            self._pintar_face()
            Animation(escala_x=1.0, duration=0.17, t="out_quad").start(self.cartao)

        ida.bind(on_complete=meio)
        ida.start(self.cartao)

    def _mover(self, passo):
        if not self.cards:
            return
        self.indice = (self.indice + passo) % len(self.cards)
        self.virado = False
        self.app.parar_fala()
        self._atualizar()
        if not movimento():
            return
        self.cartao.opacity = 0
        self.cartao.desloc_y = -dp(10)
        Animation(opacity=1, desloc_y=0, duration=0.24, t="out_cubic").start(self.cartao)

    def _embaralhar(self):
        random.shuffle(self.cards)
        self.indice = 0
        self.virado = False
        self._atualizar()
        self.aviso.text = "Cards embaralhados"

    # ── autoavaliação ───────────────────────────────────────────────
    def _alvos(self, card):
        """Marcadores que o card cobre (vazio se for de exame fora da base)."""
        from progresso import marcadores_no_texto
        siglas = [m["sigla"] for m in self.app.marcadores]
        nomes = {m["sigla"]: m["nome"] for m in self.app.marcadores}
        return marcadores_no_texto(card["pergunta"] + " " + card["resposta"], siglas, nomes)

    def _montar_avaliacao(self):
        area = self.area_avaliacao
        area.clear_widgets()
        area.height = 0
        if not (self.cards and self.virado):
            return

        card = self.cards[self.indice]
        alvos = self._alvos(card)
        if not alvos:
            area.add_widget(C.Texto(
                text="Este card é de um exame fora dos 20 marcadores da base, "
                     "então não entra nas suas revisões.",
                estilo="micro", halign="center"))
            area.height = dpt(34)
            return
        if card["pergunta"] in self.avaliados:
            area.add_widget(C.Texto(text="Você já avaliou este card nesta sessão.",
                                    estilo="micro", halign="center"))
            area.height = dpt(22)
            return

        area.add_widget(C.Texto(text="Você lembrou antes de virar?", estilo="apoio",
                                halign="center"))
        nao = C.Botao("Não lembrei", cor=COR["rubro_suave"], cor_texto=COR["rubro"],
                      icone="erro")
        nao.bind(on_release=lambda *_: self._avaliar(False))
        sim = C.Botao("Lembrei", variante="primario", icone="check")
        sim.bind(on_release=lambda *_: self._avaliar(True))
        botoes = BoxLayout(size_hint_y=None, height=sim.height, spacing=dp(10))
        botoes.add_widget(nao)
        botoes.add_widget(sim)
        area.add_widget(botoes)
        area.height = sim.height + dpt(24)
        C.aparecer([nao, sim], atraso=0.14, passo=0.04)

    def _avaliar(self, lembrou):
        """Registra no motor e avança para o próximo card."""
        if not self.cards:
            return
        card = self.cards[self.indice]
        if card["pergunta"] in self.avaliados:
            return
        alvos = self._alvos(card)
        if not alvos:
            return
        self.app.progresso.registrar_atividade(alvos, lembrou, peso="flashcard")
        self.avaliados.add(card["pergunta"])
        self.aviso.text = self.app.progresso.efeito_resumido(alvos, lembrou)
        if movimento():
            self.aviso.opacity = 0
            Animation(opacity=1, duration=0.3).start(self.aviso)
        self._mover(1)
