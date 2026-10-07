"""Sessão de revisão — o modo de estudo principal.

O ciclo de cada marcador tem uma ordem deliberada:

  1. Pergunta       recuperação ativa: tentar lembrar antes de ver
  2. Confiança      declarar o quanto acha que sabe, ANTES da resposta
  3. Resposta       conferir
  4. Autoavaliação  dizer como foi, o que reagenda o marcador

A confiança vem antes porque, depois de ver a resposta, todo mundo acha
que sabia. E a autoavaliação tem quatro níveis porque o SM-2 precisa de
graduação: "lembrei com esforço" e "lembrei na hora" levam a intervalos
diferentes. Cada botão mostra quando o marcador volta.
"""

from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.utils import escape_markup

from mobile import componentes as C
from mobile.dados import formatar_numero
from mobile.tema import COR, cor_categoria, cor_categoria_texto, dpt, texto_grande
from mobile.telas.base import TelaBase

AVALIACOES = [
    ("De novo", 0, "rubro"),
    ("Difícil", 3, "ambar"),
    ("Bom",     4, "acento"),
    ("Fácil",   5, "indigo"),
]

CONFIANCA = [(1, "Nada"), (2, "Pouco"), (3, "Médio"), (4, "Bem"), (5, "Total")]


def grade_botoes(botoes, colunas, altura, espaco=dp(8)):
    """Botões em grade; com texto grande, mais linhas e menos colunas."""
    linhas = -(-len(botoes) // colunas)
    grade = GridLayout(cols=colunas, size_hint_y=None, spacing=espaco,
                       height=linhas * altura + (linhas - 1) * espaco)
    for botao in botoes:
        grade.add_widget(botao)
    return grade


def falar_numero(texto):
    """'3,5 – 5' é lido como "três vírgula cinco traço cinco"; "a" soa natural."""
    return texto.replace(" – ", " a ")


def texto_intervalo(dias):
    if dias <= 1:
        return "amanhã"
    if dias < 30:
        return f"{dias} dias"
    meses = dias // 30
    return "1 mês" if meses == 1 else f"{meses} meses"


class TelaRevisao(TelaBase):

    LARGURA_MAXIMA = 720   # dp, em tablet e computador

    def montar(self, **_):
        app = self.app
        self.progresso = app.progresso
        self.por_sigla = {m["sigla"]: m for m in app.marcadores}
        self.limite = app.prefs["itens_por_sessao"]
        self.fila = self.progresso.fila_do_dia(list(self.por_sigla), self.limite)
        self.posicao = 0
        self.acertos = 0
        self.confianca = None
        self.revelado = False

        raiz = BoxLayout(orientation="vertical")
        topo = BoxLayout(size_hint_y=None, height=max(dp(64), dpt(56)),
                         padding=(dp(6), dp(8), dp(18), dp(8)), spacing=dp(10))
        fechar = C.BotaoIcone("fechar", pos_hint={"center_y": 0.5},
                              descricao="Encerrar a revisão")
        fechar.bind(on_release=lambda *_: app.voltar())
        topo.add_widget(fechar)
        self.barra = C.BarraProgresso(pos_hint={"center_y": 0.5})
        topo.add_widget(self.barra)
        self.contador = C.rotulo("", "13.5sp", COR["tinta2"], negrito=True,
                                 alinhar="right", size_hint_x=None, width=dp(48))
        topo.add_widget(self.contador)
        raiz.add_widget(topo)

        self.palco = BoxLayout(orientation="vertical")
        raiz.add_widget(self.palco)
        self.add_widget(raiz)
        self._mostrar()

    # ── ciclo ───────────────────────────────────────────────────────
    def _mostrar(self):
        self.palco.clear_widgets()
        self.confianca = None
        self.revelado = False

        if not self.fila:
            self._vazio()
            return
        if self.posicao >= len(self.fila):
            self._fim()
            return

        total = len(self.fila)
        self.barra.animar(self.posicao / total)
        self.contador.text = f"{self.posicao + 1}/{total}"

        sigla = self.fila[self.posicao]
        m = self.por_sigla[sigla]
        cor = cor_categoria(m["categoria"])

        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(4), dp(16), dp(28)),
                                       spacing=dp(14))
        self.scroll, self.col = scroll, col

        cartao = C.Cartao(padding=dp(22), spacing=dp(10), raio=dp(22))
        etiquetas = BoxLayout(size_hint_y=None, height=dpt(24))
        etiquetas.add_widget(C.Etiqueta(m["categoria"], (*cor[:3], 0.14),
                                        cor_categoria_texto(m["categoria"])))
        etiquetas.add_widget(Widget())
        cartao.add_widget(etiquetas)
        cartao.add_widget(C.Texto(text=m["nome"], estilo="titulo"))
        cartao.add_widget(C.Texto(text=f"Sigla {sigla}", estilo="micro"))
        cartao.add_widget(C.espacador(dp(2)))
        cartao.add_widget(C.Divisor())
        cartao.add_widget(C.espacador(dp(2)))
        pergunta = "Qual é a faixa de referência e o que significa estar alterado?"
        cartao.add_widget(C.Texto(text=pergunta, estilo="corpo", font_size="16.5sp"))
        acoes = C.linha_acoes(C.botao_ouvir(self.app, lambda: f"{m['nome']}. {pergunta}"))
        if acoes is not None:
            cartao.add_widget(acoes)
        col.add_widget(cartao)

        self.bloco_confianca = BoxLayout(orientation="vertical", size_hint_y=None,
                                         spacing=dp(10))
        self.bloco_confianca.bind(minimum_height=self.bloco_confianca.setter("height"))
        self.bloco_confianca.add_widget(C.Texto(
            text="Antes de ver: quanto você acha que sabe?", estilo="apoio"))
        self.botoes_confianca = []
        for valor, texto in CONFIANCA:
            botao = C.Botao(texto, variante="claro", cor_texto=COR["tinta2"],
                            cor_borda=COR["borda_forte"], tamanho_fonte="14sp",
                            height=dp(48), raio=dp(12), padding=(dp(4), 0))
            botao.descricao = f"Confiança: {texto}"
            botao.bind(on_release=lambda *_, v=valor: self._definir_confianca(v))
            self.botoes_confianca.append((valor, botao))
        botoes = [b for _, b in self.botoes_confianca]
        self.bloco_confianca.add_widget(grade_botoes(
            botoes, 3 if texto_grande() else 5, botoes[0].height, espaco=dp(6)))
        col.add_widget(self.bloco_confianca)

        self.botao_revelar = C.Botao("Mostrar resposta", variante="primario")
        self.botao_revelar.bind(on_release=lambda *_: self._revelar())
        col.add_widget(self.botao_revelar)

        self.area_resposta = BoxLayout(orientation="vertical", size_hint_y=None,
                                       spacing=dp(14))
        self.area_resposta.bind(minimum_height=self.area_resposta.setter("height"))
        col.add_widget(self.area_resposta)

        self.palco.add_widget(scroll)
        C.aparecer([cartao, self.bloco_confianca])
        # a resposta só libera depois da estimativa: é o que torna a medida honesta
        self.botao_revelar.disabled = True

    def _definir_confianca(self, valor):
        if self.revelado:
            return  # a estimativa vale antes de ver a resposta, não depois
        self.confianca = valor
        for v, botao in self.botoes_confianca:
            if v == valor:
                botao.pintar(COR["tinta"], COR["branco"])
                botao.cor_borda = COR["tinta"]
            else:
                botao.pintar(COR["superficie"], COR["tinta2"])
                botao.cor_borda = COR["borda_forte"]
        self.botao_revelar.disabled = False

    def _revelar(self):
        if self.revelado:
            return
        self.revelado = True
        sigla = self.fila[self.posicao]
        m = self.por_sigla[sigla]

        # a escolha fica registrada na tela; as demais esmaecem
        for v, botao in self.botoes_confianca:
            botao.opacity = 1 if v == self.confianca else 0.35
        if self.botao_revelar.parent is not None:
            self.col.remove_widget(self.botao_revelar)

        resposta = C.Superficie(orientation="vertical", size_hint_y=None, height=dpt(96),
                                cor_fundo=COR["acento_suave"], raio=dp(18),
                                padding=(dp(18), dp(14)))
        resposta.add_widget(C.rotulo("FAIXA DE REFERÊNCIA", "12sp", COR["acento_escuro"],
                                     negrito=True, vertical="bottom"))
        faixa = (f"{formatar_numero(m['valor_ref_min'])} – "
                 f"{formatar_numero(m['valor_ref_max'])}")
        resposta.add_widget(C.rotulo(
            f"[b]{escape_markup(faixa)}[/b]  "
            f"[size={int(sp(15))}]{escape_markup(m['unidade'])}[/size]",
            "30sp", COR["acento_escuro"], vertical="top", markup=True))

        alto = self._interpretacao("sobe", "Quando está elevado",
                                   m.get("interpretacao_alta"),
                                   COR["rubro"], COR["rubro_suave"])
        baixo = self._interpretacao("desce", "Quando está baixo",
                                    m.get("interpretacao_baixa"),
                                    COR["indigo"], COR["indigo_suave"])

        texto_lido = (f"{m['nome']}. Faixa de referência: {falar_numero(faixa)} "
                      f"{m['unidade']}. Quando está elevado: {m.get('interpretacao_alta', '')}. "
                      f"Quando está baixo: {m.get('interpretacao_baixa', '')}.")
        libras = None
        if self.app.prefs["atalho_libras"]:
            libras = C.Botao("Libras", variante="neutro", icone="libras", height=dp(44),
                             tamanho_fonte="14sp", size_hint_x=None, width=dpt(112))
            libras.bind(on_release=lambda *_: self.app.abrir_libras(texto_lido))
        acoes = C.linha_acoes(C.botao_ouvir(self.app, lambda: texto_lido), libras)

        avaliacao = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        avaliacao.bind(minimum_height=avaliacao.setter("height"))
        avaliacao.add_widget(C.Texto(text="Como foi lembrar?", estilo="apoio"))
        botoes = []
        for texto, qualidade, chave in AVALIACOES:
            dias = self._previsao(sigla, qualidade)
            quando = texto_intervalo(dias)
            botao = C.Botao(f"{texto}\n[size={int(sp(12.5))}]{quando}[/size]",
                            cor=COR[chave], cor_texto=COR["branco"], height=dp(66),
                            tamanho_fonte="15sp", raio=dp(14), padding=(dp(4), 0))
            botao.rotulo.markup = True
            botao.descricao = f"{texto}: volta {quando if dias > 1 else 'amanhã'}"
            botao.bind(on_release=lambda *_, q=qualidade: self._responder(q))
            botoes.append(botao)
        avaliacao.add_widget(grade_botoes(botoes, 2 if texto_grande() else 4,
                                          botoes[0].height))
        avaliacao.add_widget(C.Texto(text="A escolha define quando este marcador volta.",
                                     estilo="micro", halign="center"))

        blocos = [resposta, *([acoes] if acoes is not None else []), alto, baixo, avaliacao]
        for bloco in blocos:
            self.area_resposta.add_widget(bloco)
        C.aparecer(blocos, atraso=0.0, passo=0.06)
        Clock.schedule_once(
            lambda _dt: self.scroll.scroll_to(resposta, padding=dp(12), animate=True), 0.12)

    def _interpretacao(self, icone, titulo, texto, cor, fundo):
        cartao = C.Cartao(padding=dp(16), spacing=dp(8))
        cab = BoxLayout(size_hint_y=None, height=dpt(30), spacing=dp(10))
        cab.add_widget(C.SeloIcone(icone, cor_fundo=fundo, cor_icone=cor, tamanho=dp(30),
                                   pos_hint={"center_y": 0.5}))
        cab.add_widget(C.rotulo(titulo, "16sp", COR["tinta"], negrito=True))
        cartao.add_widget(cab)
        cartao.add_widget(C.Texto(text=texto or "—", estilo="corpo"))
        return cartao

    def _previsao(self, sigla, qualidade):
        """Dias até o marcador voltar: a mesma conta que o motor usa."""
        from progresso import proximo_intervalo
        return proximo_intervalo(self.progresso.estado(sigla), qualidade)

    def _responder(self, qualidade):
        sigla = self.fila[self.posicao]
        self.progresso.registrar_resposta(sigla, qualidade, confianca=self.confianca)
        if qualidade >= 3:
            self.acertos += 1
        self.posicao += 1
        self._mostrar()

    # ── estados finais ──────────────────────────────────────────────
    def _vazio(self):
        self.contador.text = ""
        self.barra.valor = 1.0
        scroll, col = C.coluna_rolavel(padding=(dp(24), dp(48), dp(24), dp(24)),
                                       spacing=dp(14))
        selo = BoxLayout(size_hint_y=None, height=dp(88))
        selo.add_widget(Widget())
        selo.add_widget(C.SeloIcone("check", tamanho=dp(84), tamanho_icone=dp(38)))
        selo.add_widget(Widget())
        blocos = [
            selo,
            C.Texto(text="Nada para revisar agora", estilo="titulo", halign="center"),
            C.Texto(text="Todos os marcadores estão em dia. Voltar antes da hora "
                         "reforça menos do que esperar o intervalo certo.",
                    estilo="apoio", halign="center"),
        ]
        for bloco in blocos:
            col.add_widget(bloco)
        voltar = C.Botao("Voltar ao início", variante="primario")
        voltar.bind(on_release=lambda *_: self.app.voltar())
        col.add_widget(C.espacador(dp(8)))
        col.add_widget(voltar)
        self.palco.add_widget(scroll)
        C.aparecer(blocos + [voltar])

    def _fim(self):
        total = len(self.fila)
        self.barra.animar(1.0)
        self.contador.text = f"{total}/{total}"
        pct = round(self.acertos / total * 100) if total else 0

        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(20), dp(16), dp(24)),
                                       spacing=dp(14))
        cartao = C.Cartao(padding=dp(24), spacing=dp(12), raio=dp(24))
        caixa = BoxLayout(size_hint_y=None, height=dp(150))
        caixa.add_widget(Widget())
        anel = C.AnelDia(size=(dp(146), dp(146)), tamanho_numero="34sp",
                         cor_arco=COR["acento"] if pct >= 70 else COR["ambar"])
        caixa.add_widget(anel)
        caixa.add_widget(Widget())
        cartao.add_widget(caixa)
        Clock.schedule_once(lambda _dt: anel.mostrar(
            self.acertos / total if total else 0, f"{pct}%", "lembrados"), 0.2)

        cartao.add_widget(C.Texto(text="Sessão concluída", estilo="titulo", halign="center"))
        cartao.add_widget(C.Texto(text=f"{self.acertos} de {total} marcadores lembrados",
                                  estilo="apoio", halign="center"))

        restante = self.progresso.fila_do_dia(list(self.por_sigla), self.limite)
        if restante:
            cartao.add_widget(C.Texto(
                text=f"Ainda há {len(restante)} para hoje, incluindo os que você "
                     "marcou como “De novo”.", estilo="corpo", halign="center"))
            continuar = C.Botao("Continuar revisando", variante="primario", icone="repetir")
            continuar.bind(on_release=lambda *_: self.app.ir_para("revisao"))
            cartao.add_widget(continuar)
        else:
            cartao.add_widget(C.Texto(
                text="Sua fila de hoje acabou. Cada marcador volta sozinho quando a "
                     "memória começar a ceder.", estilo="corpo", halign="center"))
        voltar = C.Botao("Voltar ao início", variante="neutro")
        voltar.bind(on_release=lambda *_: self.app.voltar())
        cartao.add_widget(voltar)

        col.add_widget(cartao)
        self.palco.add_widget(scroll)
        C.aparecer([cartao])
