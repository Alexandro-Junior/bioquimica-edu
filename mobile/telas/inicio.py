"""Tela inicial: a decisão do dia primeiro, o contexto depois.

A pergunta que esta tela responde é uma só — "o que eu faço agora?" — e
o cartão verde do topo responde em poucos segundos. Tudo abaixo é
contexto, na ordem em que ajuda a decidir: o que existe para praticar,
como está a memória, onde está frágil, e por fim a autoavaliação, a
constância e os marcos.
"""

from datetime import datetime

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

from mobile import componentes as C
from mobile.dados import contar
from mobile.tema import COR, COR_ESTAGIO, ROTULO_ESTAGIO, cor_categoria
from mobile.telas.base import TelaBase

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def saudacao(agora):
    if 5 <= agora.hour < 12:
        return "Bom dia"
    if 12 <= agora.hour < 18:
        return "Boa tarde"
    return "Boa noite"


class TelaInicio(TelaBase):

    def montar(self, **_):
        app = self.app
        self.siglas = [m["sigla"] for m in app.marcadores]
        self.categorias = {m["sigla"]: m["categoria"] for m in app.marcadores}
        self.nomes = {m["sigla"]: m["nome"] for m in app.marcadores}
        self.resumo = app.progresso.resumo(self.siglas, self.categorias)

        scroll, coluna = C.coluna_rolavel(padding=(dp(16), dp(6), dp(16), dp(22)),
                                          spacing=dp(14))
        secoes = [self._topo(), self._heroi(), self._atalhos(), self._memoria(),
                  self._focar(), self._sistemas(), self._calibracao(),
                  self._constancia(), self._marcos()]
        secoes = [s for s in secoes if s is not None]
        for secao in secoes:
            coluna.add_widget(secao)
        self.add_widget(scroll)
        C.aparecer(secoes)

    # ── topo ────────────────────────────────────────────────────────
    def _topo(self):
        agora = datetime.now()
        linha = BoxLayout(size_hint_y=None, height=dp(68), padding=(dp(2), dp(10), 0, 0))
        textos = BoxLayout(orientation="vertical")
        textos.add_widget(C.rotulo(saudacao(agora), "25sp", COR["tinta"],
                                   negrito=True, vertical="bottom"))
        textos.add_widget(C.rotulo(
            f"{DIAS[agora.weekday()]}, {agora.day} de {MESES[agora.month - 1]}",
            "13sp", COR["tinta3"], vertical="top"))
        linha.add_widget(textos)
        linha.add_widget(self._selo_sequencia())
        return linha

    def _selo_sequencia(self):
        dias = self.resumo["sequencia"]
        ativo = dias > 0
        texto = "1 dia" if dias == 1 else f"{dias} dias"
        selo = C.Superficie(size_hint=(None, None), size=(dp(90), dp(36)),
                            raio=dp(18), padding=(dp(12), 0), spacing=dp(4),
                            pos_hint={"center_y": 0.4},
                            cor_fundo=COR["ambar_suave"] if ativo else COR["superficie_alt"])
        cor = COR["ambar"] if ativo else COR["tinta3"]
        selo.add_widget(C.Icone("raio", tamanho=dp(15), color=cor,
                                pos_hint={"center_y": 0.5}))
        selo.add_widget(C.rotulo(texto, "13.5sp", cor, negrito=True))
        return selo

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
                         spacing=dp(16), raio=dp(24))
        C.decorar_com_moleculas(heroi)

        linha = BoxLayout(spacing=dp(16), size_hint_y=None, height=dp(122))
        anel = C.AnelDia(cor_arco=COR["branco"], cor_trilho=(1, 1, 1, 0.22),
                         cor_texto=COR["branco"], size=(dp(106), dp(106)),
                         pos_hint={"center_y": 0.5})
        linha.add_widget(anel)

        textos = BoxLayout(orientation="vertical", spacing=dp(5))
        textos.add_widget(Widget())
        textos.add_widget(C.Texto(text=titulo, estilo="subtitulo", color=COR["branco"],
                                  font_size="18sp"))
        textos.add_widget(C.Texto(text=detalhe, estilo="apoio", color=(1, 1, 1, 0.88)))
        if fila:
            textos.add_widget(C.Texto(
                text=f"{contar(len(fila), 'item', 'itens')} · cerca de "
                     f"{r['minutos_estimados']} min",
                estilo="micro", color=(1, 1, 1, 0.68)))
        textos.add_widget(Widget())
        linha.add_widget(textos)
        heroi.add_widget(linha)

        destino = "revisao" if fila else "diagnostico"
        botao = C.Botao(acao, variante="claro", cor_texto=COR["acento_escuro"],
                        icone="play")
        botao.bind(on_release=lambda *_: app.ir_para(destino))
        heroi.add_widget(botao)
        self.botao_heroi = botao

        Clock.schedule_once(lambda _dt: anel.definir(feitos, feitos + len(fila)), 0.3)
        return heroi

    # ── 2. atalhos de prática ───────────────────────────────────────
    def _atalhos(self):
        app = self.app
        grade = GridLayout(cols=3, spacing=dp(10), size_hint_y=None, height=dp(116))
        resolvidos = len(app.casos_resolvidos)
        itens = [
            ("cartas", "Cards", f"{len(app.flashcards)} cards", "cartas",
             COR["ambar"], COR["ambar_suave"]),
            ("pratica", "Quiz", f"{len(app.quiz)} questões", "quiz",
             COR["indigo"], COR["indigo_suave"]),
            ("frasco", "Casos", f"{resolvidos} de {len(app.casos)}", "diagnostico",
             COR["rubro"], COR["rubro_suave"]),
        ]
        for icone, titulo, detalhe, destino, cor, suave in itens:
            atalho = C.LinhaToque(orientation="vertical", padding=dp(14),
                                  spacing=dp(4), elevacao=1)
            atalho.add_widget(C.SeloIcone(icone, cor_fundo=suave, cor_icone=cor,
                                          tamanho=dp(38)))
            atalho.add_widget(Widget())
            atalho.add_widget(C.rotulo(titulo, "15sp", COR["tinta"], negrito=True,
                                       size_hint_y=None, height=dp(20)))
            atalho.add_widget(C.rotulo(detalhe, "12sp", COR["tinta3"],
                                       size_hint_y=None, height=dp(16)))
            atalho.bind(on_release=lambda *_, d=destino: app.ir_para(d))
            grade.add_widget(atalho)
        return grade

    # ── 3. memória ──────────────────────────────────────────────────
    def _memoria(self):
        r = self.resumo
        cartao = C.Cartao(spacing=dp(14))

        cab = BoxLayout(size_hint_y=None, height=dp(48))
        textos = BoxLayout(orientation="vertical")
        textos.add_widget(C.rotulo("Estado da memória", "17sp", COR["tinta"],
                                   negrito=True, vertical="bottom"))
        textos.add_widget(C.rotulo("Cresce com revisões em intervalos maiores",
                                   "12sp", COR["tinta3"], vertical="top"))
        cab.add_widget(textos)
        valor = BoxLayout(orientation="vertical", size_hint_x=None, width=dp(74))
        valor.add_widget(C.rotulo(f"{r['dominio_geral'] * 100:.0f}%", "26sp",
                                  COR["acento"], negrito=True, alinhar="right",
                                  vertical="bottom"))
        valor.add_widget(C.rotulo("domínio", "11.5sp", COR["tinta3"],
                                  alinhar="right", vertical="top"))
        cab.add_widget(valor)
        cartao.add_widget(cab)

        barra = C.BarraEstagios()
        cartao.add_widget(barra)
        Clock.schedule_once(lambda _dt: barra.animar(r["estagios"]), 0.35)

        legenda = GridLayout(cols=2, size_hint_y=None, height=dp(52),
                             spacing=(dp(12), dp(6)))
        for chave in ("consolidado", "firmando", "aprendendo", "novo"):
            item = BoxLayout(spacing=dp(7))
            item.add_widget(C.Ponto(COR_ESTAGIO[chave]))
            item.add_widget(C.rotulo(ROTULO_ESTAGIO[chave], "12.5sp", COR["tinta2"]))
            item.add_widget(C.rotulo(str(r["estagios"].get(chave, 0)), "13sp",
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
        cartao.add_widget(C.rotulo("Seus marcadores mais frágeis agora", "12.5sp",
                                   COR["tinta3"], size_hint_y=None, height=dp(20)))
        for sigla, dominio in fracos:
            categoria = self.categorias.get(sigla, "")
            linha = C.LinhaToque(size_hint_y=None, height=dp(58),
                                 padding=(dp(4), dp(6), dp(2), dp(6)),
                                 spacing=dp(12), cor_fundo=COR["transparente"],
                                 raio=dp(14))
            linha.add_widget(C.Ponto(cor_categoria(categoria), tamanho=dp(10)))
            textos = BoxLayout(orientation="vertical")
            textos.add_widget(C.rotulo(sigla, "15sp", COR["tinta"], negrito=True,
                                       vertical="bottom"))
            textos.add_widget(C.rotulo(self.nomes.get(sigla, ""), "12.5sp",
                                       COR["tinta2"], vertical="top", encurtar=True))
            linha.add_widget(textos)
            barra = C.BarraDominio(size_hint_x=None, width=dp(52),
                                   pos_hint={"center_y": 0.5},
                                   cor=COR["rubro"] if dominio < 0.3 else COR["ambar"])
            linha.add_widget(barra)
            Clock.schedule_once(lambda _dt, b=barra, v=dominio: b.animar(max(v, 0.04)), 0.4)
            linha.add_widget(C.rotulo(f"{dominio * 100:.0f}%", "12.5sp", COR["tinta2"],
                                      negrito=True, alinhar="right",
                                      size_hint_x=None, width=dp(34)))
            linha.add_widget(C.Icone("avancar", tamanho=dp(20), color=COR["tinta3"],
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
            linha = BoxLayout(size_hint_y=None, height=dp(24), spacing=dp(10))
            linha.add_widget(C.Ponto(cor))
            linha.add_widget(C.rotulo(categoria, "13.5sp", COR["tinta"],
                                      size_hint_x=None, width=dp(84)))
            barra = C.BarraDominio(cor=cor, pos_hint={"center_y": 0.5})
            linha.add_widget(barra)
            linha.add_widget(C.rotulo(f"{valor * 100:.0f}%", "12.5sp", COR["tinta2"],
                                      negrito=True, alinhar="right",
                                      size_hint_x=None, width=dp(38)))
            cartao.add_widget(linha)
            Clock.schedule_once(lambda _dt, b=barra, v=valor: b.animar(v), 0.45 + i * 0.05)
        return cartao

    # ── 6. autoavaliação ────────────────────────────────────────────
    def _calibracao(self):
        cal = self.resumo["calibracao"]
        cartao = C.Cartao(spacing=dp(10))
        cab = BoxLayout(size_hint_y=None, height=dp(26))
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

        cab.add_widget(C.rotulo(f"{cal['amostra']} respostas", "12sp", COR["tinta3"],
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
        cartao = C.Cartao(spacing=dp(12))
        cab = BoxLayout(size_hint_y=None, height=dp(26))
        cab.add_widget(C.rotulo("Constância", "17sp", COR["tinta"], negrito=True))
        cab.add_widget(C.rotulo("28 dias", "12sp", COR["tinta3"], alinhar="right"))
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
        cab = BoxLayout(size_hint_y=None, height=dp(26), padding=(0, 0, dp(18), 0))
        cab.add_widget(C.rotulo("Marcos", "17sp", COR["tinta"], negrito=True))
        cab.add_widget(C.rotulo(f"{obtidas} de {len(conquistas)}", "12sp",
                                COR["tinta3"], alinhar="right"))
        cartao.add_widget(cab)

        # altura para a descrição mais longa ("Consolidou um marcador na
        # memória de longo prazo") caber sem empurrar a estrela para fora
        faixa, linha = C.faixa_rolavel(dp(140), spacing=dp(10), padding=(0, 0, dp(18), 0))
        # os alcançados primeiro: é o que o estudante já conquistou
        for marco in sorted(conquistas, key=lambda c: not c["alcancada"]):
            feito = marco["alcancada"]
            selo = C.Superficie(orientation="vertical", size_hint=(None, None),
                                size=(dp(152), dp(136)), raio=dp(18),
                                padding=dp(12), spacing=dp(4),
                                cor_fundo=COR["acento_suave"] if feito else COR["superficie_alt"])
            selo.add_widget(C.Icone("estrela" if feito else "estrela_v", tamanho=dp(20),
                                    color=COR["acento"] if feito else COR["tinta3"]))
            selo.add_widget(C.rotulo(marco["titulo"], "13sp",
                                     COR["acento_escuro"] if feito else COR["tinta2"],
                                     negrito=True, size_hint_y=None, height=dp(20),
                                     encurtar=True))
            descricao = C.Texto(text=marco["descricao"], estilo="micro",
                                color=COR["tinta2"] if feito else COR["tinta3"])
            selo.add_widget(descricao)
            selo.add_widget(Widget())
            linha.add_widget(selo)
        cartao.add_widget(faixa)
        return cartao
