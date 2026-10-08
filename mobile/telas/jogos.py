"""Jogos da aba Prática: "Alto, normal ou baixo?" e o jogo da memória.

As regras (valores sorteados, pontos, pares) ficam em jogos.py, na raiz,
sem Kivy; aqui só a interface. A classe é um complemento da TelaPratica:
usa o mesmo corpo, a mesma barra de sessão e o mesmo cartão de retorno
do quiz, para que os três modos se comportem igual.
"""

import math

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from jogos import (PARES_MEMORIA, RODADAS, TEMPO_RODADA, SISTEMAS, classificar,
                   estrelas, estrelas_memoria, explicacao, forma_par, montar_memoria,
                   pontos, sortear_rodadas)
from mobile import componentes as C
from mobile.dados import formatar_numero
from mobile.tema import COR, cor_categoria, cor_categoria_texto, dpt, movimento

NOME_CLASSE = {"baixo": "BAIXO", "normal": "NORMAL", "alto": "ALTO"}
ICONE_CLASSE = {"baixo": "desce", "normal": "ponto", "alto": "sobe"}


def texto_valor(m, valor):
    unidade = "" if m["unidade"] == "unidades" else m["unidade"]
    return f"{formatar_numero(valor)} {unidade}".strip()


def faixa_texto(m):
    unidade = "" if m["unidade"] == "unidades" else m["unidade"]
    return (f"{formatar_numero(m['valor_ref_min'])} a "
            f"{formatar_numero(m['valor_ref_max'])} {unidade}").strip()


class Estrelas(BoxLayout):
    """Três estrelas, cheias ou vazias, com o número escrito ao lado."""

    def __init__(self, quantas, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dpt(34))
        kwargs.setdefault("spacing", dp(4))
        super().__init__(**kwargs)
        self.descricao = f"{quantas} de 3 estrelas"
        self.add_widget(Widget())
        for i in range(3):
            cheia = i < quantas
            self.add_widget(C.Icone("estrela" if cheia else "estrela_v", tamanho=dp(28),
                                    color=COR["ambar"] if cheia else COR["tinta3"],
                                    pos_hint={"center_y": 0.5}))
        self.add_widget(Widget())


class CartaMemoria(C.LinhaToque):
    """Carta do jogo da memória: virada para baixo, para cima ou já com par."""

    def __init__(self, indice, carta, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", (dp(5), dp(10)))
        kwargs.setdefault("spacing", dp(2))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dpt(104))
        kwargs.setdefault("raio", dp(16))
        super().__init__(**kwargs)
        self.indice, self.carta = indice, carta
        self.para_cima, self.com_par = False, False
        self._montar()

    def texto(self):
        c = self.carta
        if c["tipo"] == "marcador":
            return f"{c['titulo']}, {c['subtitulo']}"
        return f"Sistema: {c['titulo']}"

    def _montar(self):
        self.clear_widgets()
        c = self.carta
        if not self.para_cima:
            self.cor_fundo = COR["indigo"]
            self.cor_borda = COR["transparente"]
            self.elevacao = 1
            self.add_widget(C.Icone("frasco", tamanho=dp(30), color=COR["branco"],
                                    size_hint=(1, 1)))
            self.descricao = f"Carta {self.indice + 1}, virada para baixo"
            return
        if self.com_par:
            cor = cor_categoria(c["categoria"])
            self.cor_fundo = (*cor[:3], 0.16)
            self.cor_borda = cor_categoria_texto(c["categoria"])
            self.elevacao = 0
        else:
            self.cor_fundo = COR["superficie"]
            self.cor_borda = COR["borda_forte"]
            self.elevacao = 1
        tinta = COR["tinta"]
        if c["tipo"] == "marcador":
            self.add_widget(Widget(size_hint_y=0.15))
            self.add_widget(Label(text=c["titulo"], font_size="20sp", bold=True, color=tinta,
                                  size_hint_y=None, height=dpt(28)))
            # quebra a linha (até 3) em vez de cortar com reticências
            nome = Label(text=c["subtitulo"], font_size="11.5sp", color=COR["tinta2"],
                         halign="center", valign="top", max_lines=3)
            nome.bind(size=self._encaixar)
            self.add_widget(nome)
        else:
            self.add_widget(Label(text="SISTEMA", font_size="10.5sp", bold=True,
                                  color=COR["tinta3"], size_hint_y=None, height=dpt(18)))
            nome = Label(text=c["titulo"], font_size="14.5sp", bold=True, color=tinta,
                         halign="center", valign="middle", max_lines=3)
            nome.bind(size=self._encaixar)
            self.add_widget(nome)
        self.descricao = f"Carta {self.indice + 1}: {self.texto()}" + \
            (", par formado" if self.com_par else "")

    @staticmethod
    def _encaixar(rotulo, *_):
        """Faz a palavra mais longa caber na carta sem partir no meio.

        O Kivy só quebra linha em espaço: "Gama-Glutamiltransferase", numa
        carta estreita, seria partida numa letra qualquer. Primeiro a linha
        quebra no hífen; se ainda não couber, a letra diminui (até 80%).
        """
        rotulo.text_size = rotulo.size
        if rotulo.width <= 1:
            return
        from kivy.core.text import Label as CoreLabel
        if not hasattr(rotulo, "tamanho_original"):
            rotulo.tamanho_original = rotulo.font_size

        def largura(palavra, tamanho):
            return CoreLabel(font_size=tamanho, bold=rotulo.bold).get_extents(palavra)[0]

        palavra = max(rotulo.text.split(), key=len, default="")
        if "-" in palavra and largura(palavra, rotulo.tamanho_original) > rotulo.width:
            rotulo.text = rotulo.text.replace(palavra, palavra.replace("-", "-\n"))
            palavra = max(rotulo.text.split(), key=len, default="")
        tamanho = rotulo.tamanho_original
        while tamanho > rotulo.tamanho_original * 0.8 and \
                largura(palavra, tamanho) > rotulo.width:
            tamanho -= rotulo.tamanho_original * 0.05
        rotulo.font_size = tamanho

    def virar(self, para_cima):
        """Vira a carta: encolhe na horizontal, troca a face e volta."""
        self.para_cima = para_cima
        if not movimento():
            self._montar()
            return
        from kivy.animation import Animation
        Animation.cancel_all(self, "escala_x")
        metade = Animation(escala_x=0.0, duration=0.11, t="in_quad")
        metade.bind(on_complete=lambda *_: self._montar())
        (metade + Animation(escala_x=1.0, duration=0.13, t="out_quad")).start(self)

    def marcar_par(self):
        self.com_par = True
        self.para_cima = True
        self._montar()


class ModoJogos:
    """Os jogos dentro da TelaPratica (que fornece corpo, barra e retorno)."""

    _relogio = None
    _desvirar_evento = None

    # ── entrada ─────────────────────────────────────────────────────
    def _hub_jogos(self):
        app = self.app
        self.corpo.clear_widgets()
        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(8), dp(16), dp(24)), spacing=dp(14))

        faixas = C.Cartao(padding=dp(20), spacing=dp(12), raio=dp(24))
        faixas.add_widget(C.SeloIcone("jogo", cor_fundo=COR["ambar_suave"],
                                      cor_icone=COR["ambar"], tamanho=dp(48)))
        faixas.add_widget(C.Texto(text="Alto, normal ou baixo?", estilo="titulo"))
        faixas.add_widget(C.Texto(
            text=f"{RODADAS} resultados de exame. Diga se cada um está abaixo, dentro ou "
                 "acima da faixa de referência e veja na hora o que ele sugere.",
            estilo="apoio"))
        recorde = app.progresso.recorde("faixas")
        if recorde is not None:
            faixas.add_widget(C.Texto(text=f"Seu recorde: {recorde} pontos", estilo="micro"))
        self.alternador_relogio = C.Alternador(
            f"Relógio: {TEMPO_RODADA} segundos por rodada",
            "Um desafio a mais. Desligado, cada um responde no seu tempo.",
            ativo=app.prefs["relogio_jogo"], icone="relogio",
            cor_fundo=COR["superficie_alt"],
            ao_mudar=lambda valor: app.prefs.definir("relogio_jogo", valor))
        faixas.add_widget(self.alternador_relogio)
        jogar = C.Botao("Jogar", variante="primario", icone="play")
        jogar.bind(on_release=lambda *_: self.iniciar_faixas())
        faixas.add_widget(jogar)
        col.add_widget(faixas)

        memoria = C.Cartao(padding=dp(20), spacing=dp(12), raio=dp(24))
        memoria.add_widget(C.SeloIcone("cartas", cor_fundo=COR["indigo_suave"],
                                       cor_icone=COR["indigo"], tamanho=dp(48)))
        memoria.add_widget(C.Texto(text="Jogo da memória", estilo="titulo"))
        memoria.add_widget(C.Texto(
            text=f"Forme {PARES_MEMORIA} pares: cada marcador com o órgão ou o sistema "
                 "que ele avalia. A cada par, uma explicação curta.",
            estilo="apoio"))
        recorde = app.progresso.recorde("memoria")
        if recorde is not None:
            memoria.add_widget(C.Texto(text=f"Seu recorde: {recorde} jogadas",
                                       estilo="micro"))
        jogar = C.Botao("Jogar", variante="primario", icone="play")
        jogar.bind(on_release=lambda *_: self.iniciar_memoria())
        memoria.add_widget(jogar)
        col.add_widget(memoria)

        dica = C.Cartao(elevacao=0, cor_fundo=COR["superficie_alt"], padding=dp(18),
                        spacing=dp(6))
        dica.add_widget(C.Texto(text="Por que jogar", estilo="secao"))
        dica.add_widget(C.Texto(
            text="Saber se um resultado está fora da faixa, e o que isso sugere, é o "
                 "primeiro passo para interpretar qualquer exame. Os pontos medem só a "
                 "partida; para a sua revisão conta o que você acerta sem ver a faixa.",
            estilo="apoio"))
        col.add_widget(dica)

        self.corpo.add_widget(scroll)
        C.aparecer([faixas, memoria, dica])

    def _sair_do_jogo(self):
        self._parar_jogos()
        self.trocar_modo("jogos")

    def _parar_jogos(self):
        """Cancela relógio e cartas pendentes (ao sair do jogo ou da tela)."""
        self._parar_relogio()
        if self._desvirar_evento is not None:
            self._desvirar_evento.cancel()
            self._desvirar_evento = None

    def _marcador(self, sigla):
        return next(m for m in self.app.marcadores if m["sigla"] == sigla)

    # ════════════════════════════════════════════════════════════════
    # ALTO, NORMAL OU BAIXO?
    # ════════════════════════════════════════════════════════════════
    def iniciar_faixas(self):
        self.rodadas = sortear_rodadas(self.app.marcadores)
        self.rodada = 0
        self.pontos = 0
        self.sequencia = 0
        self.melhor_sequencia = 0
        self.acertos_jogo = 0
        self.errados = []
        self._rodada_faixas()

    def _rodada_faixas(self):
        self._parar_jogos()
        self._topo_visivel(False)
        self.corpo.clear_widgets()
        if self.rodada >= len(self.rodadas):
            self._resultado_faixas()
            return
        rodada = self.rodadas[self.rodada]
        m = self._marcador(rodada["sigla"])
        total = len(self.rodadas)
        self.respondido = False
        self.usou_dica = False
        self.corpo.add_widget(self._barra_sessao(self._sair_do_jogo, self.rodada / total,
                                                 f"{self.rodada + 1}/{total}"))

        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(4), dp(16), dp(28)), spacing=dp(12))
        self.scroll, self.col = scroll, col

        placar = BoxLayout(size_hint_y=None, height=dpt(26), spacing=dp(8))
        placar.add_widget(C.Etiqueta(f"{self.pontos} pontos", COR["ambar_suave"], COR["ambar"]))
        if self.sequencia >= 2:
            placar.add_widget(C.Etiqueta(f"{self.sequencia} acertos seguidos",
                                         COR["acento_suave"], COR["acento_escuro"]))
        placar.add_widget(Widget())
        col.add_widget(placar)

        self.barra_tempo = None
        if self.app.prefs["relogio_jogo"]:
            linha = BoxLayout(size_hint_y=None, height=dpt(24), spacing=dp(8))
            linha.add_widget(C.Icone("relogio", tamanho=dp(16), color=COR["tinta2"],
                                     pos_hint={"center_y": 0.5}))
            self.barra_tempo = C.BarraProgresso(cor=COR["ambar"], pos_hint={"center_y": 0.5})
            self.barra_tempo.valor = 1.0
            linha.add_widget(self.barra_tempo)
            self.rotulo_tempo = C.rotulo(f"{TEMPO_RODADA} s", "13sp", COR["tinta2"],
                                         negrito=True, alinhar="right", size_hint_x=None,
                                         width=dp(40))
            linha.add_widget(self.rotulo_tempo)
            col.add_widget(linha)

        exame = C.Cartao(padding=dp(20), spacing=dp(8), raio=dp(24))
        cor = cor_categoria(m["categoria"])
        etiquetas = BoxLayout(size_hint_y=None, height=dpt(24))
        etiquetas.add_widget(C.Etiqueta(m["categoria"], (*cor[:3], 0.14),
                                        cor_categoria_texto(m["categoria"])))
        etiquetas.add_widget(Widget())
        exame.add_widget(etiquetas)
        exame.add_widget(C.Texto(text=f"{m['nome']} ({m['sigla']})", estilo="subtitulo",
                                 halign="center"))
        exame.add_widget(C.Texto(text=texto_valor(m, rodada["valor"]), estilo="titulo",
                                 font_size="34sp", halign="center"))
        self.area_dica = BoxLayout(orientation="vertical", size_hint_y=None)
        self.area_dica.bind(minimum_height=self.area_dica.setter("height"))
        ver_faixa = C.Botao("Ver a faixa de referência (vale metade)", variante="fantasma",
                            icone="info", height=dp(44), tamanho_fonte="13.5sp")
        ver_faixa.bind(on_release=lambda *_: self._mostrar_dica(m))
        self.area_dica.add_widget(ver_faixa)
        exame.add_widget(self.area_dica)
        col.add_widget(exame)

        ouvir = C.botao_ouvir(self.app, lambda: (
            f"{m['nome']}: {texto_valor(m, rodada['valor'])}. "
            "Esse resultado está baixo, normal ou alto?"))
        if ouvir is not None:
            col.add_widget(C.linha_acoes(ouvir))

        col.add_widget(C.Texto(text="Esse resultado está…", estilo="subtitulo"))
        botoes = BoxLayout(size_hint_y=None, height=max(dp(60), dpt(54)), spacing=dp(10))
        self.botoes_classe = {}
        for classe in ("baixo", "normal", "alto"):
            botao = C.Botao(NOME_CLASSE[classe].capitalize(), variante="claro",
                            icone=ICONE_CLASSE[classe], height=max(dp(60), dpt(54)),
                            padding=(dp(6), 0), elevacao=1)
            botao.size_hint_y = 1
            botao.cor_borda = COR["borda_forte"]
            botao.bind(on_release=lambda *_, c=classe: self.responder_faixas(c))
            botoes.add_widget(botao)
            self.botoes_classe[classe] = botao
        col.add_widget(botoes)

        self.corpo.add_widget(scroll)
        C.aparecer([exame, botoes], atraso=0.03, passo=0.05)
        if self.barra_tempo is not None:
            self.restante = float(TEMPO_RODADA)
            self._relogio = Clock.schedule_interval(self._tique, 0.1)

    def _mostrar_dica(self, m):
        if self.respondido or self.usou_dica:
            return
        self.usou_dica = True
        self.area_dica.clear_widgets()
        self.area_dica.add_widget(C.Aviso(f"Faixa de referência: {faixa_texto(m)}",
                                          tipo="info"))

    # ── relógio ─────────────────────────────────────────────────────
    def _tique(self, dt):
        if self.respondido or self.barra_tempo is None:
            return False
        self.restante -= dt
        self.barra_tempo.valor = max(0.0, self.restante / TEMPO_RODADA)
        self.rotulo_tempo.text = f"{max(0, math.ceil(self.restante))} s"
        if self.restante <= 0:
            self._relogio = None
            self.responder_faixas(None)
            return False
        return True

    def _parar_relogio(self):
        if self._relogio is not None:
            self._relogio.cancel()
            self._relogio = None

    # ── resposta ────────────────────────────────────────────────────
    def responder_faixas(self, escolha):
        """escolha: "baixo", "normal", "alto", ou None quando o tempo acaba."""
        if self.respondido:
            return
        self.respondido = True
        self._parar_relogio()
        rodada = self.rodadas[self.rodada]
        m = self._marcador(rodada["sigla"])
        certa = classificar(rodada["valor"], m["valor_ref_min"], m["valor_ref_max"])
        acertou = escolha == certa
        if acertou:
            self.sequencia += 1
            self.acertos_jogo += 1
            self.melhor_sequencia = max(self.melhor_sequencia, self.sequencia)
            ganho = pontos(True, self.sequencia, self.usou_dica)
            self.pontos += ganho
        else:
            self.sequencia = 0
            self.errados.append(m["sigla"])
        # Com a faixa à vista, o acerto não prova que a faixa foi lembrada; e
        # o tempo esgotado não prova que ela foi esquecida.
        if escolha is not None and not self.usou_dica:
            self.app.progresso.registrar_atividade([m["sigla"]], acertou, peso="quiz")

        for classe, botao in self.botoes_classe.items():
            if classe == certa:
                botao.pintar(COR["acento"], COR["branco"])
                botao.cor_borda = COR["acento"]
            elif classe == escolha:
                botao.pintar(COR["rubro"], COR["branco"])
                botao.cor_borda = COR["rubro"]
            else:
                botao.opacity = 0.5

        if escolha is None:
            titulo = "Tempo esgotado"
        elif acertou:
            titulo = f"Certo! +{ganho} pontos"
        else:
            titulo = "Não foi dessa vez"
        regua = C.ReguaFaixas(m["valor_ref_min"], m["valor_ref_max"],
                              tem_baixo=m["valor_ref_min"] > 0, unidade=m["unidade"],
                              formatar=formatar_numero)
        Clock.schedule_once(lambda _dt: regua.mostrar(rodada["valor"]), 0.05)
        # fundo branco próprio: no cartão verde ou vermelho do retorno, a zona
        # da mesma cor sumiria
        painel = C.Cartao(elevacao=0, cor_fundo=COR["superficie"], raio=dp(14),
                          padding=(dp(12), dp(10)))
        painel.add_widget(regua)
        final = self.rodada + 1 >= len(self.rodadas)
        self._mostrar_feedback(self._feedback(
            acertou, titulo, explicacao(m, certa),
            [("Ver resultado" if final else "Próxima", "primario", self._avancar_faixas)],
            destaque=f"Está {NOME_CLASSE[certa]}. Referência: {faixa_texto(m)}.",
            extra=painel))

    def _avancar_faixas(self):
        self.rodada += 1
        self._rodada_faixas()

    def _resultado_faixas(self):
        app = self.app
        total = len(self.rodadas)
        batido = app.progresso.registrar_partida("faixas", self.pontos)
        recorde = app.progresso.recorde("faixas")
        self.corpo.clear_widgets()

        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(24), dp(16), dp(24)), spacing=dp(14))
        cartao = C.Cartao(padding=dp(24), spacing=dp(12), raio=dp(24))
        caixa = BoxLayout(size_hint_y=None, height=dp(150))
        caixa.add_widget(Widget())
        anel = C.AnelDia(size=(dp(146), dp(146)), tamanho_numero="34sp",
                         cor_arco=COR["acento"] if self.acertos_jogo >= 7 else COR["ambar"])
        caixa.add_widget(anel)
        caixa.add_widget(Widget())
        cartao.add_widget(caixa)
        Clock.schedule_once(lambda _dt: anel.mostrar(
            self.acertos_jogo / total if total else 0, f"{self.acertos_jogo}/{total}",
            "acertos"), 0.2)
        cartao.add_widget(Estrelas(estrelas(self.acertos_jogo, total)))
        cartao.add_widget(C.Texto(text=f"{self.pontos} pontos", estilo="titulo",
                                  halign="center"))
        if batido:
            cartao.add_widget(C.Aviso("Novo recorde pessoal!", tipo="sucesso"))
        elif recorde is not None:
            cartao.add_widget(C.Texto(text=f"Seu recorde: {recorde} pontos", estilo="apoio",
                                      halign="center"))
        if self.melhor_sequencia >= 2:
            cartao.add_widget(C.Texto(
                text=f"Melhor sequência: {self.melhor_sequencia} acertos seguidos",
                estilo="apoio", halign="center"))

        novo = C.Botao("Jogar de novo", variante="primario", icone="repetir")
        novo.bind(on_release=lambda *_: self.iniciar_faixas())
        cartao.add_widget(novo)
        voltar = C.Botao("Voltar aos jogos", variante="neutro")
        voltar.bind(on_release=lambda *_: self.trocar_modo("jogos"))
        cartao.add_widget(voltar)
        col.add_widget(cartao)
        itens = [cartao]

        errados = list(dict.fromkeys(self.errados))
        if errados:
            revisar = C.Cartao(spacing=dp(8))
            revisar.add_widget(C.Texto(text="PARA REVISAR", estilo="secao"))
            for sigla in errados:
                m = self._marcador(sigla)
                linha = C.LinhaToque(size_hint_y=None, height=max(dp(48), dpt(44)),
                                     padding=(dp(12), 0), spacing=dp(10),
                                     cor_fundo=COR["superficie_alt"], raio=dp(12))
                linha.descricao = f"Estudar {m['nome']}"
                linha.add_widget(C.rotulo(f"{m['nome']} ({sigla})", "14.5sp", COR["tinta"],
                                          encurtar=True))
                linha.add_widget(C.Icone("avancar", tamanho=dp(18), color=COR["tinta2"],
                                         pos_hint={"center_y": 0.5}))
                linha.bind(on_release=lambda *_, s=sigla: app.ir_para("detalhe", sigla=s))
                revisar.add_widget(linha)
            col.add_widget(revisar)
            itens.append(revisar)

        self.corpo.add_widget(scroll)
        C.aparecer(itens)

    # ════════════════════════════════════════════════════════════════
    # JOGO DA MEMÓRIA
    # ════════════════════════════════════════════════════════════════
    def iniciar_memoria(self):
        self.cartas = montar_memoria(self.app.marcadores)
        self.viradas = []
        self.encontradas = set()
        self.jogadas = 0
        self.travado = False
        self._mesa_memoria()

    def _mesa_memoria(self):
        self._parar_jogos()
        self._topo_visivel(False)
        self.corpo.clear_widgets()
        pares = len(self.cartas) // 2
        self.barra_memoria = self._barra_sessao(self._sair_do_jogo, 0, f"0/{pares}")
        self.corpo.add_widget(self.barra_memoria)

        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(4), dp(16), dp(28)), spacing=dp(12))
        self.scroll, self.col = scroll, col
        self.rotulo_jogadas = C.Texto(
            text="Toque em duas cartas: um marcador e o sistema que ele avalia.",
            estilo="apoio")
        col.add_widget(self.rotulo_jogadas)

        colunas = 3 if self.largura_util() < dp(520) else 4
        grade = GridLayout(cols=colunas, spacing=dp(10), size_hint_y=None)
        grade.bind(minimum_height=grade.setter("height"))
        self.widgets_cartas = []
        for i, carta in enumerate(self.cartas):
            w = CartaMemoria(i, carta)
            w.bind(on_release=lambda *_, idx=i: self.virar_carta(idx))
            grade.add_widget(w)
            self.widgets_cartas.append(w)
        col.add_widget(grade)

        self.area_par = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        self.area_par.bind(minimum_height=self.area_par.setter("height"))
        col.add_widget(self.area_par)

        self.corpo.add_widget(scroll)
        C.aparecer(self.widgets_cartas, atraso=0.02, passo=0.02)

    def virar_carta(self, indice):
        if self.travado or indice in self.encontradas or indice in self.viradas:
            return
        widget = self.widgets_cartas[indice]
        widget.virar(True)
        self.app.falar(widget.texto())
        self.viradas.append(indice)
        if len(self.viradas) < 2:
            return
        self.jogadas += 1
        self.rotulo_jogadas.text = f"Jogadas: {self.jogadas}"
        a, b = self.viradas
        if forma_par(self.cartas[a], self.cartas[b]):
            self.encontradas |= {a, b}
            self.viradas = []
            for i in (a, b):
                self.widgets_cartas[i].marcar_par()
            self._explicar_par(self.cartas[a])
            pares = len(self.cartas) // 2
            feitos = len(self.encontradas) // 2
            self.barra_memoria.progresso.animar(feitos / pares)
            self.barra_memoria.texto.text = f"{feitos}/{pares}"
            if feitos == pares:
                self.travado = True
                self._desvirar_evento = Clock.schedule_once(
                    lambda _dt: self._resultado_memoria(), 1.2)
        else:
            self.travado = True
            self._desvirar_evento = Clock.schedule_once(self._desvirar, 1.1)

    def _desvirar(self, _dt=None):
        self._desvirar_evento = None
        for i in self.viradas:
            self.widgets_cartas[i].virar(False)
        self.viradas = []
        self.travado = False

    def _explicar_par(self, carta):
        m = self._marcador(carta["par"])
        sistema = SISTEMAS.get(m["categoria"], m["categoria"])
        texto = f"{m['nome']} ({m['sigla']}) avalia: {sistema.lower()}."
        alta = m.get("interpretacao_alta", "").strip().rstrip(".")
        if alta:
            texto += f" Quando está alto: {alta[0].lower() + alta[1:]}."
        self.area_par.clear_widgets()
        aviso = C.Aviso(texto, tipo="sucesso", titulo="Par formado")
        self.area_par.add_widget(aviso)
        C.aparecer([aviso], atraso=0.0, passo=0.0)
        self.app.falar(texto)

    def _resultado_memoria(self):
        self._desvirar_evento = None
        app = self.app
        pares = len(self.cartas) // 2
        batido = app.progresso.registrar_partida("memoria", self.jogadas, menor_e_melhor=True)
        recorde = app.progresso.recorde("memoria")
        self.corpo.clear_widgets()

        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(24), dp(16), dp(24)), spacing=dp(14))
        cartao = C.Cartao(padding=dp(24), spacing=dp(12), raio=dp(24))
        selo = BoxLayout(size_hint_y=None, height=dp(64))
        selo.add_widget(Widget())
        selo.add_widget(C.SeloIcone("cartas", cor_fundo=COR["indigo_suave"],
                                    cor_icone=COR["indigo"], tamanho=dp(64)))
        selo.add_widget(Widget())
        cartao.add_widget(selo)
        cartao.add_widget(C.Texto(text="Todos os pares!", estilo="titulo", halign="center"))
        cartao.add_widget(C.Texto(text=f"{pares} pares em {self.jogadas} jogadas",
                                  estilo="apoio", halign="center"))
        cartao.add_widget(Estrelas(estrelas_memoria(self.jogadas, pares)))
        if batido:
            cartao.add_widget(C.Aviso("Novo recorde pessoal!", tipo="sucesso"))
        elif recorde is not None:
            cartao.add_widget(C.Texto(text=f"Seu recorde: {recorde} jogadas", estilo="apoio",
                                      halign="center"))

        resumo = C.Cartao(elevacao=0, cor_fundo=COR["superficie_alt"], spacing=dp(6))
        resumo.add_widget(C.Texto(text="OS PARES DESTA PARTIDA", estilo="secao"))
        for carta in self.cartas:
            if carta["tipo"] != "marcador":
                continue
            m = self._marcador(carta["par"])
            resumo.add_widget(C.Texto(
                text=f"{m['sigla']} · {m['nome']}: {SISTEMAS.get(m['categoria'], m['categoria'])}",
                estilo="apoio"))
        cartao.add_widget(resumo)

        novo = C.Botao("Jogar de novo", variante="primario", icone="repetir")
        novo.bind(on_release=lambda *_: self.iniciar_memoria())
        cartao.add_widget(novo)
        voltar = C.Botao("Voltar aos jogos", variante="neutro")
        voltar.bind(on_release=lambda *_: self.trocar_modo("jogos"))
        cartao.add_widget(voltar)
        col.add_widget(cartao)
        self.corpo.add_widget(scroll)
        C.aparecer([cartao])
