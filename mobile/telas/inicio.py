"""Tela inicial: a decisão do dia primeiro, o contexto depois.

A pergunta que esta tela responde é uma só — "o que eu faço agora?" — e
o cartão verde do topo responde em poucos segundos. Tudo abaixo é
contexto, na ordem em que ajuda a decidir: o que existe para praticar,
como está a memória, onde está frágil, e por fim a autoavaliação, a
constância e os marcos.

No modo foco (TDAH, dificuldade de concentração), a tela para no que
decide o dia: o cartão de hoje e os atalhos. O restante continua a um
toque, em "Ver meu progresso", em vez de competir pela atenção.
"""

from datetime import datetime

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

from mobile import componentes as C
from mobile.dados import contar
from mobile.tema import (COR, COR_ESTAGIO, ROTULO_ESTAGIO, cor_categoria, dpt,
                         texto_grande)
from mobile.telas.base import TelaBase

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


class TelaInicio(TelaBase):

    LARGURA_MAXIMA = 1120   # dp, em tablet e computador

    def _foco(self, expandido):
        return self.app.prefs["modo_foco"] and not expandido

    def largura_maxima(self, expandido=False, **_):
        # o modo foco é uma coluna só, estreita, mesmo em tela larga
        return 720 if self._foco(expandido) else self.LARGURA_MAXIMA

    def montar(self, expandido=False, **_):
        app = self.app
        self.siglas = [m["sigla"] for m in app.marcadores]
        self.categorias = {m["sigla"]: m["categoria"] for m in app.marcadores}
        self.nomes = {m["sigla"]: m["nome"] for m in app.marcadores}
        self.resumo = app.progresso.resumo(self.siglas, self.categorias,
                                           limite=app.prefs["itens_por_sessao"])

        scroll, coluna = C.coluna_rolavel(padding=(dp(16), dp(6), dp(16), dp(22)),
                                          spacing=dp(14))
        hoje = [self._heroi(), self._atalhos()]
        if self._foco(expandido):
            hoje.append(self._ver_progresso())
            acompanhamento = []
        else:
            hoje += [self._memoria(), self._focar()]
            acompanhamento = [self._sistemas(), self._calibracao(), self._constancia(),
                              self._marcos()]
        hoje = [s for s in hoje if s is not None]
        acompanhamento = [s for s in acompanhamento if s is not None]
        topo = self._topo()
        coluna.add_widget(topo)

        if acompanhamento and self.largura_util() >= dp(840):
            # tela larga: à esquerda o que fazer hoje, à direita o acompanhamento
            linha = BoxLayout(size_hint_y=None, spacing=dp(16))
            for secoes in (hoje, acompanhamento):
                lado = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(14),
                                 pos_hint={"top": 1})
                lado.bind(minimum_height=lado.setter("height"))
                for secao in secoes:
                    lado.add_widget(secao)
                linha.add_widget(lado)

            def ajustar(*_):
                linha.height = max(lado.height for lado in linha.children)
            for lado in linha.children:
                lado.bind(height=ajustar)
            coluna.add_widget(linha)
        else:
            for secao in hoje + acompanhamento:
                coluna.add_widget(secao)
        self.add_widget(scroll)
        C.aparecer([topo, *hoje, *acompanhamento])

    # ── topo ────────────────────────────────────────────────────────
    def _topo(self):
        agora = datetime.now()
        linha = BoxLayout(size_hint_y=None, height=dpt(66), padding=(dp(2), dp(8), 0, 0),
                          spacing=dp(10))
        textos = BoxLayout(orientation="vertical")
        textos.add_widget(C.rotulo("Hoje", "26sp", COR["tinta"], negrito=True,
                                   vertical="bottom"))
        textos.add_widget(C.rotulo(
            f"{DIAS[agora.weekday()].capitalize()}, {agora.day} de {MESES[agora.month - 1]}",
            "13.5sp", COR["tinta3"], vertical="top"))
        linha.add_widget(textos)
        ajustes = C.BotaoIcone("acessibilidade", cor=COR["superficie"], elevacao=1,
                               cor_icone=COR["tinta"], descricao="Acessibilidade",
                               pos_hint={"center_y": 0.45})
        ajustes.bind(on_release=lambda *_: self.app.ir_para("acessibilidade"))
        linha.add_widget(ajustes)
        conta = C.BotaoIcone("pessoa", cor=COR["superficie"], elevacao=1,
                             cor_icone=COR["tinta"], descricao="Conta",
                             pos_hint={"center_y": 0.45})
        conta.bind(on_release=lambda *_: self.app.ir_para("conta"))
        linha.add_widget(conta)
        return linha

    # ── 1. hoje ─────────────────────────────────────────────────────
    def _heroi(self):
        app, r = self.app, self.resumo
        fila, vencidos, reforco = r["fila"], r["vencidos"], r["reforco"]
        novos, feitos = r["novos"], r["revisados_hoje"]

        if novos == len(self.siglas):
            titulo, acao = "Comece por aqui", "Estudar os primeiros"
            detalhe = (f"São {len(self.siglas)} marcadores. Poucos por vez, e "
                       "cada um volta pouco antes de você esquecer.")
        elif reforco:
            titulo, acao = "Corrija o que errou hoje", "Retomar os que errei"
            errados = "1 marcador errado" if reforco == 1 else f"{reforco} marcadores errados"
            detalhe = f"{errados} hoje. Rever agora, com o erro fresco, fixa a correção."
        elif vencidos:
            titulo, acao = "Revisão de hoje pronta", "Começar revisão"
            detalhe = (f"{contar(vencidos, 'marcador', 'marcadores')} no ponto de "
                       "revisão, entre lembrar e esquecer.")
        elif fila:
            titulo, acao = "Revisões em dia", "Aprender algo novo"
            n = min(len(fila), novos)
            detalhe = (f"Nada vencido. Dá para avançar em "
                       f"{contar(n, 'marcador novo', 'marcadores novos')}.")
        else:
            titulo, acao = "Tudo revisado", "Praticar com casos"
            detalhe = ("Nenhum marcador venceu hoje. O app chama de volta "
                       "quando a memória precisar.")

        heroi = C.Cartao(cor_fundo=COR["acento"], elevacao=1, padding=dp(18),
                         spacing=dp(16), raio=dp(22))

        textos = BoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None)
        textos.bind(minimum_height=textos.setter("height"))
        textos.add_widget(C.Texto(text=titulo, estilo="subtitulo", color=COR["branco"],
                                  font_size="19sp"))
        textos.add_widget(C.Texto(text=detalhe, estilo="apoio", color=COR["branco"]))
        if fila:
            textos.add_widget(C.Texto(
                text=f"{contar(len(fila), 'item', 'itens')} · cerca de "
                     f"{r['minutos_estimados']} min",
                estilo="micro", color=COR["branco"], bold=True))

        if texto_grande():
            # com letra grande o anel tomaria metade da largura do texto
            heroi.add_widget(textos)
        else:
            linha = BoxLayout(spacing=dp(16), size_hint_y=None)
            anel = C.AnelDia(cor_arco=COR["branco"], cor_trilho=(1, 1, 1, 0.25),
                             cor_texto=COR["branco"], size=(dp(100), dp(100)),
                             pos_hint={"center_y": 0.5})
            linha.add_widget(anel)
            linha.add_widget(textos)
            textos.bind(height=lambda *_: setattr(linha, "height",
                                                  max(dp(108), textos.height)))
            heroi.add_widget(linha)
            Clock.schedule_once(lambda _dt: anel.definir(feitos, feitos + len(fila)), 0.3)

        destino = "revisao" if fila else "diagnostico"
        botao = C.Botao(acao, variante="claro", cor_texto=COR["acento_escuro"],
                        icone="play")
        botao.bind(on_release=lambda *_: app.ir_para(destino))
        heroi.add_widget(botao)
        self.botao_heroi = botao
        return heroi

    # ── 2. atalhos de prática ───────────────────────────────────────
    def _atalhos(self):
        app = self.app
        resolvidos = len(app.casos_resolvidos)
        itens = [
            ("cartas", "Cards", f"{len(app.flashcards)} cards", "cartas"),
            ("pratica", "Quiz", f"{len(app.quiz)} questões", "quiz"),
            ("frasco", "Casos", f"{resolvidos} de {len(app.casos)}", "diagnostico"),
        ]
        colunas = 1 if texto_grande() else 3
        altura_item = dpt(54) if colunas == 1 else dpt(112)
        grade = GridLayout(cols=colunas, spacing=dp(10), size_hint_y=None,
                           height=altura_item * (3 // colunas) + dp(10) * (3 // colunas - 1))
        for icone, titulo, detalhe, destino in itens:
            atalho = C.LinhaToque(orientation="vertical" if colunas == 3 else "horizontal",
                                  padding=dp(14), spacing=dp(6 if colunas == 3 else 14),
                                  elevacao=1)
            atalho.descricao = titulo
            atalho.add_widget(C.SeloIcone(icone, cor_fundo=COR["acento_suave"],
                                          cor_icone=COR["acento_escuro"], tamanho=dp(38),
                                          quadrado=True, pos_hint={"center_y": 0.5}))
            if colunas == 3:
                atalho.add_widget(Widget())
            textos = BoxLayout(orientation="vertical")
            textos.add_widget(C.rotulo(titulo, "15sp", COR["tinta"], negrito=True,
                                       vertical="bottom"))
            textos.add_widget(C.rotulo(detalhe, "12.5sp", COR["tinta3"], vertical="top"))
            if colunas == 3:
                textos.size_hint_y = None
                textos.height = dpt(40)
            atalho.add_widget(textos)
            atalho.bind(on_release=lambda *_, d=destino: app.ir_para(d))
            grade.add_widget(atalho)
        return grade

    def _ver_progresso(self):
        caixa = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        caixa.bind(minimum_height=caixa.setter("height"))
        r = self.resumo
        caixa.add_widget(C.Texto(
            text=f"Modo foco ligado. Domínio geral: {r['dominio_geral'] * 100:.0f}%.",
            estilo="apoio", halign="center"))
        ver = C.Botao("Ver meu progresso", variante="neutro", icone="avancar")
        ver.bind(on_release=lambda *_: self.preparar(expandido=True))
        caixa.add_widget(ver)
        return caixa

    # ── 3. memória ──────────────────────────────────────────────────
    def _memoria(self):
        r = self.resumo
        cartao = C.Cartao(spacing=dp(14))

        cab = BoxLayout(size_hint_y=None, height=dpt(50))
        textos = BoxLayout(orientation="vertical")
        textos.add_widget(C.rotulo("Estado da memória", "17sp", COR["tinta"],
                                   negrito=True, vertical="bottom"))
        textos.add_widget(C.rotulo("Cresce com revisões em intervalos maiores",
                                   "12.5sp", COR["tinta3"], vertical="top", encurtar=True))
        cab.add_widget(textos)
        valor = BoxLayout(orientation="vertical", size_hint_x=None, width=dpt(74))
        valor.add_widget(C.rotulo(f"{r['dominio_geral'] * 100:.0f}%", "26sp",
                                  COR["acento"], negrito=True, alinhar="right",
                                  vertical="bottom"))
        valor.add_widget(C.rotulo("domínio", "12sp", COR["tinta3"],
                                  alinhar="right", vertical="top"))
        cab.add_widget(valor)
        cartao.add_widget(cab)

        barra = C.BarraEstagios()
        cartao.add_widget(barra)
        Clock.schedule_once(lambda _dt: barra.animar(r["estagios"]), 0.35)

        colunas = 1 if texto_grande() else 2
        legenda = GridLayout(cols=colunas, size_hint_y=None,
                             height=dpt(23) * (4 // colunas) + dp(6) * (4 // colunas - 1),
                             spacing=(dp(12), dp(6)))
        for chave in ("consolidado", "firmando", "aprendendo", "novo"):
            item = BoxLayout(spacing=dp(7))
            item.add_widget(C.Ponto(COR_ESTAGIO[chave]))
            item.add_widget(C.rotulo(ROTULO_ESTAGIO[chave], "13sp", COR["tinta2"]))
            item.add_widget(C.rotulo(str(r["estagios"].get(chave, 0)), "13.5sp",
                                     COR["tinta"], negrito=True, alinhar="right",
                                     size_hint_x=None, width=dp(26)))
            legenda.add_widget(item)
        cartao.add_widget(legenda)
        return cartao

    # ── 4. onde focar ───────────────────────────────────────────────
    def _focar(self):
        fracos = self.resumo["pontos_fracos"]
        if not fracos:
            return None
        cartao = C.Cartao(spacing=dp(6))
        cartao.add_widget(C.rotulo("Onde focar", "17sp", COR["tinta"], negrito=True,
                                   size_hint_y=None, height=dp(24)))
        cartao.add_widget(C.rotulo("Seus marcadores mais frágeis agora", "13sp",
                                   COR["tinta3"], size_hint_y=None, height=dp(20)))
        for sigla, dominio in fracos:
            categoria = self.categorias.get(sigla, "")
            linha = C.LinhaToque(size_hint_y=None, height=max(dp(58), dpt(50)),
                                 padding=(dp(4), dp(6), dp(2), dp(6)),
                                 spacing=dp(12), cor_fundo=COR["transparente"],
                                 raio=dp(14))
            linha.descricao = f"{sigla}, {self.nomes.get(sigla, '')}"
            linha.add_widget(C.Ponto(cor_categoria(categoria), tamanho=dp(10)))
            textos = BoxLayout(orientation="vertical")
            textos.add_widget(C.rotulo(sigla, "15sp", COR["tinta"], negrito=True,
                                       vertical="bottom"))
            textos.add_widget(C.rotulo(self.nomes.get(sigla, ""), "13sp",
                                       COR["tinta2"], vertical="top", encurtar=True))
            linha.add_widget(textos)
            barra = C.BarraDominio(size_hint_x=None, width=dp(52),
                                   pos_hint={"center_y": 0.5},
                                   cor=COR["rubro"] if dominio < 0.3 else COR["ambar"])
            linha.add_widget(barra)
            Clock.schedule_once(lambda _dt, b=barra, v=dominio: b.animar(max(v, 0.04)), 0.4)
            linha.add_widget(C.rotulo(f"{dominio * 100:.0f}%", "13sp", COR["tinta2"],
                                      negrito=True, alinhar="right",
                                      size_hint_x=None, width=dp(36)))
            linha.add_widget(C.Icone("avancar", tamanho=dp(18), color=COR["tinta3"],
                                     pos_hint={"center_y": 0.5}))
            linha.bind(on_release=lambda *_, s=sigla: self.app.ir_para("detalhe", sigla=s))
            cartao.add_widget(linha)
        return cartao

    # ── 5. sistemas ─────────────────────────────────────────────────
    def _sistemas(self):
        itens = sorted(self.resumo["dominio_categoria"].items(), key=lambda kv: -kv[1])
        cartao = C.Cartao(spacing=dp(10))
        cartao.add_widget(C.rotulo("Por sistema", "17sp", COR["tinta"], negrito=True,
                                   size_hint_y=None, height=dp(26)))
        for i, (categoria, valor) in enumerate(itens):
            cor = cor_categoria(categoria)
            linha = BoxLayout(size_hint_y=None, height=dpt(24), spacing=dp(10))
            linha.add_widget(C.Ponto(cor))
            linha.add_widget(C.rotulo(categoria, "13.5sp", COR["tinta"],
                                      size_hint_x=None, width=dp(84)))
            barra = C.BarraDominio(cor=cor, pos_hint={"center_y": 0.5})
            linha.add_widget(barra)
            linha.add_widget(C.rotulo(f"{valor * 100:.0f}%", "13sp", COR["tinta2"],
                                      negrito=True, alinhar="right",
                                      size_hint_x=None, width=dp(38)))
            cartao.add_widget(linha)
            Clock.schedule_once(lambda _dt, b=barra, v=valor: b.animar(v), 0.45 + i * 0.05)
        return cartao

    # ── 6. autoavaliação ────────────────────────────────────────────
    def _calibracao(self):
        cal = self.resumo["calibracao"]
        cartao = C.Cartao(spacing=dp(10))
        cab = BoxLayout(size_hint_y=None, height=dpt(26))
        cab.add_widget(C.rotulo("Autoavaliação", "17sp", COR["tinta"], negrito=True))
        cartao.add_widget(cab)

        if not cal or not cal.get("suficiente"):
            amostra = (cal or {}).get("amostra", 0)
            faltam = max(1, 10 - amostra)
            cartao.add_widget(C.Texto(
                text=f"Faça mais {faltam} revisões dizendo o quanto tem certeza. "
                     "Depois comparamos sua confiança com seus acertos — a "
                     "diferença que ninguém enxerga sozinho.",
                estilo="apoio"))
            barra = C.BarraProgresso(cor=COR["indigo"])
            cartao.add_widget(barra)
            Clock.schedule_once(lambda _dt: barra.animar(amostra / 10), 0.5)
            return cartao

        cab.add_widget(C.rotulo(f"{cal['amostra']} respostas", "12.5sp", COR["tinta3"],
                                alinhar="right"))
        regua = C.ReguaCalibracao()
        cartao.add_widget(regua)
        Clock.schedule_once(lambda _dt: regua.animar(cal["confianca"], cal["acerto"]), 0.5)
        cartao.add_widget(C.Texto(text=cal["leitura"], estilo="corpo"))
        return cartao

    # ── 7. constância ───────────────────────────────────────────────
    def _constancia(self):
        atividade = self.resumo["atividade"]
        ativos = sum(1 for _, v in atividade if v)
        seguidos = self.resumo["sequencia"]
        cartao = C.Cartao(spacing=dp(12))
        cab = BoxLayout(size_hint_y=None, height=dpt(26), spacing=dp(8))
        cab.add_widget(C.rotulo("Constância", "17sp", COR["tinta"], negrito=True))
        if seguidos > 1:
            cab.add_widget(C.Icone("calendario", tamanho=dp(16), color=COR["acento"],
                                   pos_hint={"center_y": 0.5}))
            cab.add_widget(C.rotulo(f"{seguidos} dias seguidos", "13sp", COR["acento_escuro"],
                                    negrito=True, alinhar="right", size_hint_x=None,
                                    width=dp(120)))
        cartao.add_widget(cab)
        grafico = C.Constancia()
        cartao.add_widget(grafico)
        Clock.schedule_once(lambda _dt: grafico.animar(atividade), 0.55)
        dias = "1 dia" if ativos == 1 else f"{ativos} dias"
        cartao.add_widget(C.Texto(text=f"{dias} com estudo nas últimas 4 semanas",
                                  estilo="micro"))
        return cartao

    # ── 8. marcos ───────────────────────────────────────────────────
    def _marcos(self):
        conquistas = self.resumo["conquistas"]
        obtidas = sum(1 for c in conquistas if c["alcancada"])
        cartao = C.Cartao(spacing=dp(12), padding=(dp(18), dp(18), 0, dp(18)))
        cab = BoxLayout(size_hint_y=None, height=dpt(26), padding=(0, 0, dp(18), 0))
        cab.add_widget(C.rotulo("Marcos", "17sp", COR["tinta"], negrito=True))
        cab.add_widget(C.rotulo(f"{obtidas} de {len(conquistas)}", "12.5sp",
                                COR["tinta3"], alinhar="right"))
        cartao.add_widget(cab)

        # altura para a descrição mais longa ("Consolidou um marcador na
        # memória de longo prazo") caber sem empurrar a estrela para fora
        largura = dpt(152)
        faixa, linha = C.faixa_rolavel(dpt(140), spacing=dp(10), padding=(0, 0, dp(18), 0))
        # os alcançados primeiro: é o que o estudante já conquistou
        for marco in sorted(conquistas, key=lambda c: not c["alcancada"]):
            feito = marco["alcancada"]
            selo = C.Superficie(orientation="vertical", size_hint=(None, None),
                                size=(largura, dpt(136)), raio=dp(16),
                                padding=dp(12), spacing=dp(4),
                                cor_fundo=COR["acento_suave"] if feito else COR["superficie_alt"])
            selo.add_widget(C.Icone("estrela" if feito else "estrela_v", tamanho=dp(20),
                                    color=COR["acento"] if feito else COR["tinta3"]))
            selo.add_widget(C.rotulo(marco["titulo"], "13.5sp",
                                     COR["acento_escuro"] if feito else COR["tinta2"],
                                     negrito=True, size_hint_y=None, height=dp(20),
                                     encurtar=True))
            descricao = C.Texto(text=marco["descricao"], estilo="micro",
                                color=COR["tinta2"])
            selo.add_widget(descricao)
            selo.add_widget(Widget())
            linha.add_widget(selo)
        cartao.add_widget(faixa)
        return cartao
