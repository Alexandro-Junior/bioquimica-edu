"""Prática: quiz rápido e casos clínicos, lado a lado.

Os dois ficam na mesma aba porque respondem à mesma intenção — testar o
que se lembra — e diferem só no formato: o quiz cobra um fato, o caso
cobra a interpretação de vários marcadores juntos. Todo acerto e todo
erro alimentam a revisão espaçada dos marcadores envolvidos.
"""

import random

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from mobile import componentes as C
from mobile.dados import formatar_numero
from mobile.tema import COR, cor_categoria, cor_categoria_texto, dpt, texto_grande
from mobile.telas.base import TelaBase

LETRAS = "ABCDEF"


def texto_da_questao(enunciado, alternativas):
    """Enunciado e alternativas em frases, para a leitura em voz alta."""
    opcoes = " ".join(f"Alternativa {LETRAS[i]}: {a}." for i, a in enumerate(alternativas))
    return f"{enunciado} {opcoes}"


def titulo_caso(caso):
    titulo = caso.get("titulo", "")
    return titulo.split("—", 1)[1].strip() if "—" in titulo else titulo


class TelaPratica(TelaBase):

    LARGURA_MAXIMA = 760   # dp, em tablet e computador

    def montar(self, modo="quiz", iniciar=False, **_):
        raiz = BoxLayout(orientation="vertical")
        cabecalho = C.titulo_pagina("Prática", "Teste o que você lembra")
        seletor = C.Superficie(size_hint_y=None, height=max(dp(52), dpt(46)),
                               cor_fundo=COR["superficie_alt"],
                               raio=dp(15), padding=dp(4), spacing=dp(4))
        # padding (8 + 6) + espaço entre título e seletor (12)
        self.altura_topo = cabecalho.height + seletor.height + dp(26)
        self.topo = BoxLayout(orientation="vertical", size_hint_y=None,
                              height=self.altura_topo,
                              padding=(dp(16), dp(8), dp(16), dp(6)), spacing=dp(12))
        self.topo.add_widget(cabecalho)

        self.seg_quiz = C.Botao("Quiz", variante="claro", height=dp(44), raio=dp(12),
                                tamanho_fonte="14.5sp")
        self.seg_casos = C.Botao("Casos clínicos", variante="claro", height=dp(44),
                                 raio=dp(12), tamanho_fonte="14.5sp")
        for botao in (self.seg_quiz, self.seg_casos):
            botao.size_hint_y = 1
        self.seg_quiz.bind(on_release=lambda *_: self.trocar_modo("quiz"))
        self.seg_casos.bind(on_release=lambda *_: self.trocar_modo("casos"))
        seletor.add_widget(self.seg_quiz)
        seletor.add_widget(self.seg_casos)
        self.topo.add_widget(seletor)
        raiz.add_widget(self.topo)

        self.corpo = BoxLayout(orientation="vertical")
        raiz.add_widget(self.corpo)
        self.add_widget(raiz)

        self.perguntas, self.indice, self.acertos = [], 0, 0
        self.opcoes, self.respondido = [], False
        self.trocar_modo(modo, iniciar=iniciar)

    # ── estrutura ───────────────────────────────────────────────────
    def _topo_visivel(self, visivel):
        self.topo.height = self.altura_topo if visivel else 0
        self.topo.opacity = 1 if visivel else 0
        self.topo.disabled = not visivel

    def trocar_modo(self, modo, iniciar=False):
        self.modo = modo
        for botao, ativo in ((self.seg_quiz, modo == "quiz"),
                             (self.seg_casos, modo == "casos")):
            botao.pintar(COR["superficie"] if ativo else COR["transparente"],
                         COR["tinta"] if ativo else COR["tinta2"])
            botao.elevacao = 1 if ativo else 0
        self._topo_visivel(True)
        if modo == "quiz":
            if iniciar:
                self.iniciar_quiz()
            else:
                self._hub_quiz()
        else:
            self._lista_casos()

    def _barra_sessao(self, ao_fechar, fracao, texto):
        barra = BoxLayout(size_hint_y=None, height=max(dp(64), dpt(56)),
                          padding=(dp(6), dp(8), dp(18), dp(8)), spacing=dp(10))
        fechar = C.BotaoIcone("fechar", pos_hint={"center_y": 0.5}, descricao="Fechar")
        fechar.bind(on_release=lambda *_: ao_fechar())
        barra.add_widget(fechar)
        progresso = C.BarraProgresso(cor=COR["indigo"], pos_hint={"center_y": 0.5})
        barra.add_widget(progresso)
        Clock.schedule_once(lambda _dt: progresso.animar(fracao), 0.05)
        barra.add_widget(C.rotulo(texto, "13.5sp", COR["tinta2"], negrito=True,
                                  alinhar="right", size_hint_x=None, width=dp(48)))
        return barra

    def _opcao(self, indice, texto):
        opcao = C.LinhaToque(auto_altura=True, elevacao=1, raio=dp(16),
                             padding=(dp(12), dp(13), dp(14), dp(13)), spacing=dp(12))
        selo = C.Superficie(size_hint=(None, None), size=(dp(32), dp(32)), raio=dp(16),
                            cor_fundo=COR["superficie_alt"], pos_hint={"center_y": 0.5})
        letra = C.rotulo(LETRAS[indice], "14sp", COR["tinta2"], negrito=True,
                         alinhar="center")
        selo.add_widget(letra)
        opcao.add_widget(selo)
        corpo = C.Texto(text=texto, estilo="corpo", valign="middle")
        opcao.add_widget(corpo)
        opcao.selo, opcao.letra, opcao.corpo = selo, letra, corpo
        return opcao

    @staticmethod
    def _marcar(opcao, estado):
        """Pinta a opção depois da resposta, sem desabilitar o widget.

        Desabilitar faria o Kivy apagar o texto com a cor de "desabilitado";
        a trava contra duplo toque fica na flag `respondido`.
        """
        if estado in ("certo", "errado"):
            certo = estado == "certo"
            opcao.cor_fundo = COR["acento_suave"] if certo else COR["rubro_suave"]
            opcao.cor_borda = COR["acento"] if certo else COR["rubro"]
            opcao.elevacao = 0
            opcao.selo.cor_fundo = COR["acento"] if certo else COR["rubro"]
            # a letra vira ✓ ou ✗: o resultado não depende só da cor
            opcao.selo.clear_widgets()
            opcao.selo.add_widget(C.Icone("check" if certo else "erro", tamanho=dp(16),
                                          color=COR["branco"], size_hint=(1, 1)))
            opcao.descricao = f"{'Correta' if certo else 'Sua resposta, errada'}: " \
                              f"{opcao.corpo.text}"
        else:
            Clock.schedule_once(lambda _dt: setattr(opcao, "opacity", 0.5), 0)

    def _feedback(self, acertou, titulo, texto, acoes, destaque=None):
        cor = COR["acento"] if acertou else COR["rubro"]
        cartao = C.Cartao(elevacao=0, cor_fundo=COR["acento_suave"] if acertou
                          else COR["rubro_suave"], padding=dp(18), spacing=dp(10),
                          raio=dp(20))
        cab = BoxLayout(size_hint_y=None, height=dpt(32), spacing=dp(10))
        cab.add_widget(C.SeloIcone("check" if acertou else "erro", cor_fundo=cor,
                                   cor_icone=COR["branco"], tamanho=dp(32),
                                   pos_hint={"center_y": 0.5}))
        cab.add_widget(C.rotulo(titulo, "17sp", COR["acento_escuro"] if acertou
                                else COR["rubro"], negrito=True))
        cartao.add_widget(cab)
        if destaque:
            cartao.add_widget(C.Texto(text=destaque, estilo="corpo", bold=True))
        if texto:
            cartao.add_widget(C.Texto(text=texto, estilo="corpo"))
            ouvir = C.botao_ouvir(self.app, lambda: f"{titulo}. {destaque or ''} {texto}")
            if ouvir is not None:
                cartao.add_widget(C.linha_acoes(ouvir))
        for rotulo_botao, variante, funcao in acoes:
            botao = C.Botao(rotulo_botao, variante=variante)
            botao.bind(on_release=lambda *_, f=funcao: f())
            cartao.add_widget(botao)
        return cartao

    def _mostrar_feedback(self, cartao):
        self.col.add_widget(cartao)
        C.aparecer([cartao], atraso=0.0, passo=0.0)
        Clock.schedule_once(
            lambda _dt: self.scroll.scroll_to(cartao, padding=dp(16), animate=True), 0.1)

    # ════════════════════════════════════════════════════════════════
    # QUIZ
    # ════════════════════════════════════════════════════════════════
    def _hub_quiz(self):
        app = self.app
        self.corpo.clear_widgets()
        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(8), dp(16), dp(24)), spacing=dp(14))

        cartao = C.Cartao(padding=dp(20), spacing=dp(12), raio=dp(24))
        cartao.add_widget(C.SeloIcone("pratica", cor_fundo=COR["indigo_suave"],
                                      cor_icone=COR["indigo"], tamanho=dp(48)))
        cartao.add_widget(C.Texto(text="Quiz rápido", estilo="titulo"))
        n = min(10, len(app.quiz))
        cartao.add_widget(C.Texto(
            text=f"{n} questões sorteadas de um banco de {len(app.quiz)}. Cada acerto "
                 "conta para a revisão dos marcadores envolvidos.", estilo="apoio"))
        if app.ultimo_quiz:
            feitos, total = app.ultimo_quiz
            cartao.add_widget(C.Texto(text=f"Último resultado: {feitos} de {total}",
                                      estilo="micro"))
        comecar = C.Botao("Começar quiz", variante="primario", icone="play")
        comecar.bind(on_release=lambda *_: self.iniciar_quiz())
        cartao.add_widget(comecar)
        col.add_widget(cartao)

        dica = C.Cartao(elevacao=0, cor_fundo=COR["superficie_alt"], padding=dp(18), spacing=dp(6))
        dica.add_widget(C.Texto(text="Por que testar em vez de reler", estilo="secao"))
        dica.add_widget(C.Texto(
            text="Tentar lembrar antes de ver a resposta fixa mais do que reler o "
                 "conteúdo. Errar aqui não custa nada: o marcador só volta mais cedo "
                 "para revisão.", estilo="apoio"))
        col.add_widget(dica)

        self.corpo.add_widget(scroll)
        C.aparecer([cartao, dica])

    def iniciar_quiz(self):
        banco = list(self.app.quiz)
        random.shuffle(banco)
        self.perguntas = banco[:10]
        self.indice = 0
        self.acertos = 0
        self._mostrar_pergunta()

    def _mostrar_pergunta(self):
        self._topo_visivel(False)
        self.corpo.clear_widgets()
        if not self.perguntas:
            self.corpo.add_widget(C.Texto(text="Nenhuma pergunta disponível.",
                                          estilo="apoio", halign="center"))
            return
        if self.indice >= len(self.perguntas):
            self._resultado()
            return

        p = self.perguntas[self.indice]
        total = len(self.perguntas)
        self.respondido = False
        self.corpo.add_widget(self._barra_sessao(lambda: self.trocar_modo("quiz"),
                                                 self.indice / total,
                                                 f"{self.indice + 1}/{total}"))

        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(4), dp(16), dp(28)), spacing=dp(12))
        self.scroll, self.col = scroll, col
        categoria = p.get("categoria", "")
        cor = cor_categoria(categoria)
        etiquetas = BoxLayout(size_hint_y=None, height=dpt(24))
        etiquetas.add_widget(C.Etiqueta(categoria, (*cor[:3], 0.14),
                                        cor_categoria_texto(categoria)))
        etiquetas.add_widget(Widget())
        col.add_widget(etiquetas)
        col.add_widget(C.Texto(text=p["pergunta"], estilo="titulo", font_size="19.5sp"))
        ouvir = C.botao_ouvir(self.app, lambda: texto_da_questao(p["pergunta"],
                                                                 p["alternativas"]))
        if ouvir is not None:
            col.add_widget(C.linha_acoes(ouvir))
        col.add_widget(C.espacador(dp(2)))

        self.opcoes = []
        for i, alternativa in enumerate(p["alternativas"]):
            opcao = self._opcao(i, alternativa)
            opcao.bind(on_release=lambda *_, idx=i, perg=p: self.responder_quiz(idx, perg))
            col.add_widget(opcao)
            self.opcoes.append(opcao)

        self.corpo.add_widget(scroll)
        C.aparecer(self.opcoes, atraso=0.05, passo=0.04)

    def responder_quiz(self, escolha, pergunta):
        if self.respondido:
            return
        self.respondido = True
        correta = pergunta["resposta_correta"]
        acertou = escolha == correta
        if acertou:
            self.acertos += 1

        texto = " ".join([pergunta.get("pergunta", ""), *pergunta.get("alternativas", []),
                          pergunta.get("explicacao", "")])
        self.app.alimentar_memoria(texto, acertou, peso="quiz")

        for i, opcao in enumerate(self.opcoes):
            if i == correta:
                self._marcar(opcao, "certo")
            elif i == escolha:
                self._marcar(opcao, "errado")
            else:
                self._marcar(opcao, "apagado")

        final = self.indice + 1 >= len(self.perguntas)
        self._mostrar_feedback(self._feedback(
            acertou, "Correto" if acertou else "Não foi dessa vez",
            pergunta.get("explicacao", ""),
            [("Ver resultado" if final else "Continuar", "primario", self._avancar)]))

    def _avancar(self):
        self.indice += 1
        self._mostrar_pergunta()

    def _resultado(self):
        total = len(self.perguntas)
        pct = round(self.acertos / total * 100) if total else 0
        self.app.ultimo_quiz = (self.acertos, total)
        self.corpo.clear_widgets()

        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(24), dp(16), dp(24)), spacing=dp(14))
        cartao = C.Cartao(padding=dp(24), spacing=dp(12), raio=dp(24))
        caixa = BoxLayout(size_hint_y=None, height=dp(150))
        caixa.add_widget(Widget())
        anel = C.AnelDia(size=(dp(146), dp(146)), tamanho_numero="34sp",
                         cor_arco=COR["acento"] if pct >= 70 else COR["ambar"])
        caixa.add_widget(anel)
        caixa.add_widget(Widget())
        cartao.add_widget(caixa)
        Clock.schedule_once(lambda _dt: anel.mostrar(
            self.acertos / total if total else 0, f"{pct}%", "de acerto"), 0.2)

        cartao.add_widget(C.Texto(text="Quiz concluído", estilo="titulo", halign="center"))
        cartao.add_widget(C.Texto(text=f"{self.acertos} de {total} corretas",
                                  estilo="apoio", halign="center"))
        if pct >= 70:
            recado = "Bom domínio. Os marcadores que você acertou demoram mais a voltar."
        elif pct >= 50:
            recado = "No caminho. Os marcadores que você errou entram na revisão de hoje."
        else:
            recado = "Os marcadores que você errou voltam hoje na revisão — é lá que eles fixam."
        cartao.add_widget(C.Texto(text=recado, estilo="corpo", halign="center"))

        novo = C.Botao("Novo quiz", variante="primario", icone="repetir")
        novo.bind(on_release=lambda *_: self.iniciar_quiz())
        cartao.add_widget(novo)
        voltar = C.Botao("Voltar à prática", variante="neutro")
        voltar.bind(on_release=lambda *_: self.trocar_modo("quiz"))
        cartao.add_widget(voltar)

        col.add_widget(cartao)
        self.corpo.add_widget(scroll)
        C.aparecer([cartao])

    # ════════════════════════════════════════════════════════════════
    # CASOS CLÍNICOS
    # ════════════════════════════════════════════════════════════════
    def _sistemas_do_caso(self, caso):
        from progresso import marcadores_no_texto
        marcadores = self.app.marcadores
        siglas = [m["sigla"] for m in marcadores]
        nomes = {m["sigla"]: m["nome"] for m in marcadores}
        categoria = {m["sigla"]: m["categoria"] for m in marcadores}
        sistemas = []
        for sigla in marcadores_no_texto(" ".join(caso.get("exames", {})), siglas, nomes):
            if categoria[sigla] not in sistemas:
                sistemas.append(categoria[sigla])
        return sistemas

    def _lista_casos(self):
        app = self.app
        self.corpo.clear_widgets()
        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(8), dp(16), dp(24)), spacing=dp(12))
        col.add_widget(C.Texto(
            text=f"{len(app.casos_resolvidos)} de {len(app.casos)} resolvidos. Leia a "
                 "história, interprete os exames e escolha o diagnóstico.",
            estilo="apoio"))
        itens = []
        for caso in app.casos:
            item = self._item_caso(caso)
            col.add_widget(item)
            itens.append(item)
        self.corpo.add_widget(scroll)
        C.aparecer(itens[:6], atraso=0.0, passo=0.04)

    def _item_caso(self, caso):
        resolvido = caso["id"] in self.app.casos_resolvidos
        item = C.LinhaToque(auto_altura=True, orientation="vertical", elevacao=1,
                            padding=dp(16), spacing=dp(8), raio=dp(20))
        etiquetas = BoxLayout(size_hint_y=None, height=dpt(24), spacing=dp(6))
        etiquetas.add_widget(C.Etiqueta(f"Caso {caso['id']}", COR["superficie_alt"],
                                        COR["tinta2"]))
        for sistema in self._sistemas_do_caso(caso)[:2]:
            cor = cor_categoria(sistema)
            etiquetas.add_widget(C.Etiqueta(sistema, (*cor[:3], 0.13),
                                            cor_categoria_texto(sistema)))
        etiquetas.add_widget(Widget())
        if resolvido:
            etiquetas.add_widget(C.Etiqueta("Resolvido", COR["acento_suave"],
                                            COR["acento_escuro"]))
        item.add_widget(etiquetas)
        item.add_widget(C.Texto(text=titulo_caso(caso), estilo="subtitulo"))
        historia = caso.get("historia", "")
        if len(historia) > 110:
            # sem pontuação antes das reticências ("constante.…")
            historia = historia[:107].rsplit(" ", 1)[0].rstrip(".,;:") + "…"
        item.add_widget(C.Texto(text=historia, estilo="apoio"))
        item.bind(on_release=lambda *_: self.abrir_caso(caso))
        return item

    def abrir_caso(self, caso):
        self._topo_visivel(False)
        self.corpo.clear_widgets()
        self.caso_atual = caso
        self.respondido = False
        self.corpo.add_widget(C.Cabecalho(f"Caso {caso['id']}",
                                          ao_voltar=lambda: self.trocar_modo("casos"),
                                          subtitulo="Caso clínico"))

        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(2), dp(16), dp(28)), spacing=dp(14))
        self.scroll, self.col = scroll, col
        col.add_widget(C.Texto(text=titulo_caso(caso), estilo="titulo"))

        historia = C.Cartao(spacing=dp(8))
        historia.add_widget(C.Texto(text="HISTÓRIA CLÍNICA", estilo="secao"))
        historia.add_widget(C.Texto(text=caso.get("historia", ""), estilo="corpo"))
        ouvir = C.botao_ouvir(self.app, lambda: caso.get("historia", ""))
        if ouvir is not None:
            historia.add_widget(C.linha_acoes(ouvir))
        col.add_widget(historia)

        exames = C.Cartao(spacing=dp(10))
        exames.add_widget(C.Texto(text="EXAMES", estilo="secao"))
        itens = list(caso.get("exames", {}).items())
        for i, (nome, dados) in enumerate(itens):
            exames.add_widget(self._linha_exame(nome, dados))
            if i < len(itens) - 1:
                exames.add_widget(C.Divisor())
        col.add_widget(exames)

        col.add_widget(C.Texto(text="Qual é o diagnóstico?", estilo="subtitulo"))
        self.alternativas_caso = list(caso["alternativas"])
        random.shuffle(self.alternativas_caso)
        self.opcoes = []
        for i, alternativa in enumerate(self.alternativas_caso):
            opcao = self._opcao(i, alternativa)
            opcao.bind(on_release=lambda *_, a=alternativa: self.responder_caso(a, caso))
            col.add_widget(opcao)
            self.opcoes.append(opcao)

        self.corpo.add_widget(scroll)
        C.aparecer([historia, exames, *self.opcoes], atraso=0.03, passo=0.04)

    @staticmethod
    def _linha_exame(nome, dados):
        valor = dados.get("valor")
        unidade = dados.get("unidade", "")
        if unidade == "unidades":  # pH é adimensional
            unidade = ""
        minimo, maximo = dados.get("ref_min"), dados.get("ref_max")
        numerico = all(isinstance(x, (int, float)) for x in (valor, minimo, maximo))

        if numerico:
            if valor > maximo:
                situacao, fundo, tinta = "ALTO", COR["rubro_suave"], COR["rubro"]
            elif valor < minimo:
                situacao, fundo, tinta = "BAIXO", COR["indigo_suave"], COR["indigo"]
            else:
                situacao, fundo, tinta = "NORMAL", COR["acento_suave"], COR["acento_escuro"]
            referencia = f"ref. {formatar_numero(minimo)} – {formatar_numero(maximo)} {unidade}"
            texto_valor = f"{formatar_numero(valor)} {unidade}"
        else:
            # exames qualitativos, como cetonas "MASSIVAS"
            situacao, fundo, tinta = "ALTERADO", COR["ambar_suave"], COR["ambar"]
            referencia = f"ref. {str(minimo).lower()}" if minimo else ""
            texto_valor = str(valor).capitalize()

        if texto_grande():
            # letra grande: nome inteiro numa linha, valor e situação na de baixo,
            # em vez de espremer tudo lado a lado e cortar o nome do exame
            bloco = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
            bloco.bind(minimum_height=bloco.setter("height"))
            bloco.add_widget(C.Texto(text=nome, estilo="corpo", bold=True))
            if referencia:
                bloco.add_widget(C.Texto(text=referencia, estilo="micro"))
            baixo = BoxLayout(size_hint_y=None, height=dpt(28), spacing=dp(10))
            baixo.add_widget(C.rotulo(texto_valor, "15sp", COR["tinta"], negrito=True))
            baixo.add_widget(C.Etiqueta(situacao, fundo, tinta))
            bloco.add_widget(baixo)
            return bloco

        linha = BoxLayout(size_hint_y=None, height=dpt(46), spacing=dp(10))
        textos = BoxLayout(orientation="vertical")
        textos.add_widget(C.rotulo(nome, "14.5sp", COR["tinta"], vertical="bottom",
                                   encurtar=True))
        textos.add_widget(C.rotulo(referencia, "12sp", COR["tinta3"], vertical="top",
                                   encurtar=True))
        linha.add_widget(textos)
        linha.add_widget(C.rotulo(texto_valor, "14.5sp", COR["tinta"], negrito=True,
                                  alinhar="right", size_hint_x=None, width=dp(100)))
        caixa = BoxLayout(size_hint_x=None, width=dpt(80))
        caixa.add_widget(Widget())
        caixa.add_widget(C.Etiqueta(situacao, fundo, tinta))
        linha.add_widget(caixa)
        return linha

    def responder_caso(self, escolha, caso):
        if self.respondido:
            return
        self.respondido = True
        acertou = escolha == caso["resposta_correta"]
        if acertou:
            self.app.registrar_caso_resolvido(caso["id"])
        # interpretar um caso é recuperação sobre vários marcadores de uma vez
        self.app.alimentar_memoria(" ".join(caso.get("exames", {}).keys()), acertou,
                                   peso="diagnostico")

        for opcao, alternativa in zip(self.opcoes, self.alternativas_caso):
            if alternativa == caso["resposta_correta"]:
                self._marcar(opcao, "certo")
            elif alternativa == escolha:
                self._marcar(opcao, "errado")
            else:
                self._marcar(opcao, "apagado")

        acoes = [("Outros casos", "primario", lambda: self.trocar_modo("casos"))]
        if not acertou:
            acoes.insert(0, ("Tentar de novo", "neutro", lambda: self.abrir_caso(caso)))
        self._mostrar_feedback(self._feedback(
            acertou, "Diagnóstico correto" if acertou else "Não é esse",
            caso.get("explicacao", ""), acoes,
            destaque=None if acertou else f"Correto: {caso['resposta_correta']}"))
