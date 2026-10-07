"""Estudo: lista de marcadores com busca e filtro, e o detalhe de cada um.

O detalhe é uma tela cheia, e não um popup: no celular o conteúdo de um
marcador (interpretação, casos, imagens, fontes) é longo demais para uma
janela sobreposta, e a tela cheia ganha o gesto natural de voltar.
"""

import webbrowser

from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.utils import escape_markup

from mobile import componentes as C
from mobile.dados import IMG_DIR, formatar_numero
from mobile.tema import (COR, COR_ESTAGIO, ROTULO_ESTAGIO, cor_categoria,
                         cor_categoria_texto, dpt, texto_grande)
from mobile.telas.base import TelaBase


def suave(cor, alfa=0.13):
    return (*cor[:3], alfa)


def faixa_referencia(m):
    return f"{formatar_numero(m['valor_ref_min'])} – {formatar_numero(m['valor_ref_max'])}"


# ════════════════════════════════════════════════════════════════════
# LISTA
# ════════════════════════════════════════════════════════════════════
class TelaEstudo(TelaBase):

    def montar(self, **_):
        app = self.app
        self.marcadores = app.marcadores
        self.categoria = "Todos"
        categorias = []
        for m in self.marcadores:
            if m["categoria"] not in categorias:
                categorias.append(m["categoria"])

        raiz = BoxLayout(orientation="vertical")
        topo = BoxLayout(orientation="vertical", size_hint_y=None,
                         padding=(dp(16), dp(8), dp(16), dp(4)), spacing=dp(12))
        topo.bind(minimum_height=topo.setter("height"))

        cab = C.titulo_pagina("Estudo", " ")
        self.contagem = cab.subtitulo
        topo.add_widget(cab)

        self.busca = C.CampoTexto(dica="Buscar por nome ou sigla", lupa=True)
        self.busca.campo.bind(text=lambda *_: self._filtrar())
        topo.add_widget(self.busca)

        faixa, linha = C.faixa_rolavel(max(dp(46), C.dpt(40)), spacing=dp(8))
        self.chips = {}
        for categoria in ["Todos"] + categorias:
            chip = C.Chip(categoria, cor_ponto=None if categoria == "Todos"
                          else cor_categoria(categoria))
            chip.bind(on_release=lambda _c, cat=categoria: self._escolher(cat))
            linha.add_widget(chip)
            self.chips[categoria] = chip
        topo.add_widget(faixa)
        raiz.add_widget(topo)

        scroll, self.lista = C.coluna_rolavel(padding=(dp(16), dp(8), dp(16), dp(20)),
                                              spacing=dp(10))
        self.scroll = scroll
        raiz.add_widget(scroll)
        self.add_widget(raiz)
        self._escolher("Todos")

    def _escolher(self, categoria):
        self.categoria = categoria
        for nome, chip in self.chips.items():
            chip.selecionado = nome == categoria
        self._filtrar()

    def _filtrar(self):
        termo = self.busca.campo.text.strip().lower()
        visiveis = [m for m in self.marcadores
                    if (self.categoria == "Todos" or m["categoria"] == self.categoria)
                    and (not termo or termo in m["nome"].lower()
                         or termo in m["sigla"].lower())]
        self.lista.clear_widgets()
        total = len(self.marcadores)
        self.contagem.text = (f"{total} marcadores em 6 sistemas" if len(visiveis) == total
                              else f"{len(visiveis)} de {total} marcadores")
        linhas = [self._linha(m) for m in visiveis]
        for linha in linhas:
            self.lista.add_widget(linha)
        if not linhas:
            vazio = C.Cartao(elevacao=0, cor_fundo=COR["superficie_alt"], padding=dp(22))
            vazio.add_widget(C.Texto(text="Nenhum marcador encontrado", estilo="subtitulo",
                                     halign="center"))
            vazio.add_widget(C.Texto(text="Tente a sigla (ALT, K, TropI) ou outro sistema.",
                                     estilo="apoio", halign="center"))
            self.lista.add_widget(vazio)
            linhas = [vazio]
        C.aparecer(linhas[:8], atraso=0.0, passo=0.03)

    def _linha(self, m):
        sigla = m["sigla"]
        cor = cor_categoria(m["categoria"])
        progresso = self.app.progresso
        estagio = progresso.estagio(sigla)
        dominio = progresso.dominio(sigla)

        grande = texto_grande()
        linha = C.LinhaToque(size_hint_y=None, height=dpt(78), elevacao=1,
                             padding=(dp(12), dp(12), dp(12), dp(12)), spacing=dp(12),
                             auto_altura=grande)
        linha.descricao = f"{m['nome']}, {ROTULO_ESTAGIO[estagio]}"
        selo = C.Superficie(size_hint=(None, None), size=(dpt(54), dpt(54)), raio=dp(14),
                            cor_fundo=suave(cor), pos_hint={"center_y": 0.5})
        selo.add_widget(C.rotulo(sigla, "14.5sp" if len(sigla) <= 4 else "12sp",
                                 cor_categoria_texto(m["categoria"]),
                                 negrito=True, alinhar="center"))
        linha.add_widget(selo)

        if grande:
            # letra grande: o nome quebra em linhas em vez de ser cortado
            textos = BoxLayout(orientation="vertical", spacing=dp(2), size_hint_y=None,
                               pos_hint={"center_y": 0.5})
            textos.bind(minimum_height=textos.setter("height"))
            textos.add_widget(C.Texto(text=m["nome"], estilo="corpo", bold=True))
            # sem a coluna da direita, o nome ganha largura e não quebra no meio
            textos.add_widget(C.Texto(
                text=f"{dominio * 100:.0f}% de domínio · {ROTULO_ESTAGIO[estagio]} · "
                     f"{m['categoria']}", estilo="micro"))
        else:
            textos = BoxLayout(orientation="vertical", spacing=dp(2))
            textos.add_widget(C.rotulo(m["nome"], "15.5sp", COR["tinta"], negrito=True,
                                       vertical="bottom", encurtar=True))
            detalhe = BoxLayout(spacing=dp(6))
            detalhe.add_widget(C.Ponto(COR_ESTAGIO[estagio], tamanho=dp(7)))
            detalhe.add_widget(C.rotulo(f"{ROTULO_ESTAGIO[estagio]} · {m['categoria']}",
                                        "13sp", COR["tinta3"], vertical="middle",
                                        encurtar=True))
            textos.add_widget(detalhe)
        linha.add_widget(textos)

        if not grande:
            direita = BoxLayout(orientation="vertical", size_hint_x=None, width=dpt(42),
                                spacing=dp(6), padding=(0, dp(8)))
            direita.add_widget(C.rotulo(f"{dominio * 100:.0f}%", "13sp",
                                        COR["acento"] if dominio > 0 else COR["tinta3"],
                                        negrito=True, alinhar="right"))
            barra = C.BarraDominio(height=dp(5))
            barra.valor = dominio
            direita.add_widget(barra)
            linha.add_widget(direita)
        linha.add_widget(C.Icone("avancar", tamanho=dp(18), color=COR["tinta3"],
                                 pos_hint={"center_y": 0.5}))

        linha.bind(on_release=lambda *_: self.app.ir_para("detalhe", sigla=sigla))
        return linha


# ════════════════════════════════════════════════════════════════════
# DETALHE
# ════════════════════════════════════════════════════════════════════
class TelaDetalhe(TelaBase):

    def montar(self, sigla=None, aba="geral", **_):
        app = self.app
        self.marcadores = app.marcadores
        m = next((x for x in self.marcadores if x["sigla"] == sigla), self.marcadores[0])
        self.m = m
        self.extras = app.extras.get(m["sigla"], {})
        self.imagens = app.imagens.get(m["sigla"], {}).get("imagens", [])

        raiz = BoxLayout(orientation="vertical")
        raiz.add_widget(C.Cabecalho(m["sigla"], ao_voltar=app.voltar,
                                    subtitulo=m["categoria"]))
        scroll, coluna = C.coluna_rolavel(padding=(dp(16), dp(2), dp(16), dp(28)),
                                          spacing=dp(14))
        self.scroll = scroll
        coluna.add_widget(self._resumo(m))

        self.abas = [("geral", "Visão geral")]
        if self.extras.get("exemplos"):
            self.abas.append(("casos", f"Casos ({len(self.extras['exemplos'])})"))
        if self.imagens:
            self.abas.append(("imagens", "Imagens"))
        if self.extras.get("referencias"):
            self.abas.append(("fontes", "Fontes"))
        if self.extras.get("videos"):
            self.abas.append(("videos", "Vídeos"))

        faixa, linha = C.faixa_rolavel(max(dp(46), dpt(40)), spacing=dp(8))
        self.chips = {}
        for chave, texto in self.abas:
            chip = C.Chip(texto)
            chip.bind(on_release=lambda _c, k=chave: self.mostrar_aba(k))
            linha.add_widget(chip)
            self.chips[chave] = chip
        coluna.add_widget(faixa)

        self.conteudo = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(12))
        self.conteudo.bind(minimum_height=self.conteudo.setter("height"))
        coluna.add_widget(self.conteudo)

        raiz.add_widget(scroll)
        self.add_widget(raiz)
        self.mostrar_aba(aba if aba in dict(self.abas) else "geral")

    def _resumo(self, m):
        cor = cor_categoria(m["categoria"])
        progresso = self.app.progresso
        estagio = progresso.estagio(m["sigla"])
        estado = progresso.estado(m["sigla"])

        cartao = C.Cartao(padding=dp(20), spacing=dp(8), raio=dp(22))
        cartao.add_widget(C.Texto(text=m["nome"], estilo="titulo"))
        etiquetas = BoxLayout(size_hint_y=None, height=dpt(26), spacing=dp(6))
        etiquetas.add_widget(C.Etiqueta(m["categoria"], suave(cor, 0.14),
                                        cor_categoria_texto(m["categoria"])))
        etiquetas.add_widget(C.Etiqueta(ROTULO_ESTAGIO[estagio],
                                        suave(COR_ESTAGIO[estagio], 0.22),
                                        COR["tinta"]))
        etiquetas.add_widget(Widget())
        cartao.add_widget(etiquetas)
        cartao.add_widget(C.espacador(dp(4)))

        faixa = C.Superficie(orientation="vertical", size_hint_y=None, height=dpt(86),
                             cor_fundo=COR["acento_suave"], raio=dp(14),
                             padding=(dp(16), dp(12)))
        faixa.add_widget(C.rotulo("FAIXA DE REFERÊNCIA", "12sp", COR["acento_escuro"],
                                  negrito=True, vertical="bottom"))
        faixa.add_widget(C.rotulo(
            f"[b]{escape_markup(faixa_referencia(m))}[/b]  "
            f"[size={int(sp(15))}]{escape_markup(m['unidade'])}[/size]",
            "28sp", COR["acento_escuro"], vertical="top", markup=True))
        cartao.add_widget(faixa)

        if estado["tentativas"]:
            quando = estado["proxima_revisao"] or ""
            if quando:
                ano, mes, dia = quando.split("-")
                quando = f"próxima revisão em {dia}/{mes}"
            cartao.add_widget(C.Texto(
                text=f"{progresso.dominio(m['sigla']) * 100:.0f}% de domínio · {quando}",
                estilo="micro"))
        return cartao

    def mostrar_aba(self, chave):
        for k, chip in self.chips.items():
            chip.selecionado = k == chave
        self.aba = chave
        self.conteudo.clear_widgets()
        construtor = {"geral": self._geral, "casos": self._casos,
                      "imagens": self._imagens, "fontes": self._fontes,
                      "videos": self._videos}[chave]
        blocos = construtor()
        for bloco in blocos:
            self.conteudo.add_widget(bloco)
        C.aparecer(blocos, atraso=0.0, passo=0.05)

    # ── abas ────────────────────────────────────────────────────────
    def _interpretacao(self, icone, titulo, texto, doencas, cor, fundo):
        cartao = C.Cartao(spacing=dp(10))
        cab = BoxLayout(size_hint_y=None, height=dpt(34), spacing=dp(10))
        cab.add_widget(C.SeloIcone(icone, cor_fundo=fundo, cor_icone=cor, tamanho=dp(34),
                                   pos_hint={"center_y": 0.5}))
        cab.add_widget(C.rotulo(titulo, "16sp", COR["tinta"], negrito=True))
        cartao.add_widget(cab)
        cartao.add_widget(C.Texto(text=texto or "—", estilo="corpo"))
        itens = [d.strip() for d in (doencas or "").split(",")
                 if d.strip() and d.strip() != "—"]
        if itens:
            cartao.add_widget(C.Texto(text="Associado a", estilo="micro"))
            pilha = StackLayout(size_hint_y=None, spacing=dp(6), orientation="lr-tb")
            pilha.bind(minimum_height=pilha.setter("height"))
            for item in itens:
                pilha.add_widget(C.Etiqueta(item, COR["superficie_alt"], COR["tinta"],
                                            height=dpt(28), pos_hint={}))
            cartao.add_widget(pilha)
        return cartao

    def texto_para_leitura(self):
        """O conteúdo da visão geral em frases, para voz e para Libras."""
        m = self.m

        def associadas(chave):
            texto = (m.get(chave) or "").strip()
            return "" if not texto or texto == "—" else f" Associado a: {texto}."

        faixa = faixa_referencia(m).replace(" – ", " a ")
        return (f"{m['nome']}. Faixa de referência: {faixa} {m['unidade']}. "
                f"Quando está elevado: {m.get('interpretacao_alta', '')}."
                f"{associadas('doencas_associadas_alta')} "
                f"Quando está baixo: {m.get('interpretacao_baixa', '')}."
                f"{associadas('doencas_associadas_baixa')}")

    def _geral(self):
        m = self.m
        libras = None
        if self.app.prefs["atalho_libras"]:
            libras = C.Botao("Libras", variante="neutro", icone="libras", height=dp(44),
                             tamanho_fonte="14sp", size_hint_x=None, width=dpt(112))
            libras.bind(on_release=lambda *_: self.app.abrir_libras(self.texto_para_leitura()))
        acoes = C.linha_acoes(C.botao_ouvir(self.app, self.texto_para_leitura), libras)
        blocos = [acoes] if acoes is not None else []
        return blocos + [
            self._interpretacao("sobe", "Quando está elevado", m.get("interpretacao_alta"),
                                m.get("doencas_associadas_alta"),
                                COR["rubro"], COR["rubro_suave"]),
            self._interpretacao("desce", "Quando está baixo", m.get("interpretacao_baixa"),
                                m.get("doencas_associadas_baixa"),
                                COR["indigo"], COR["indigo_suave"]),
        ]

    def _casos(self):
        blocos = []
        for i, ex in enumerate(self.extras.get("exemplos", []), 1):
            cartao = C.Cartao(spacing=dp(10))
            topo = BoxLayout(size_hint_y=None, height=dpt(24))
            topo.add_widget(C.Etiqueta(f"Caso {i}", COR["acento_suave"], COR["acento_escuro"]))
            topo.add_widget(Widget())
            cartao.add_widget(topo)
            cartao.add_widget(C.Texto(text=ex["titulo"], estilo="subtitulo"))
            cartao.add_widget(C.Texto(text=ex["descricao"], estilo="corpo"))

            valores = C.Superficie(orientation="vertical", size_hint_y=None,
                                   cor_fundo=COR["superficie_alt"], raio=dp(14),
                                   padding=dp(12), spacing=dp(4))
            valores.bind(minimum_height=valores.setter("height"))
            valores.add_widget(C.Texto(text="VALORES", estilo="micro", bold=True))
            valores.add_widget(C.Texto(text=ex["valores"].replace(" | ", "\n"),
                                       estilo="apoio", color=COR["tinta"]))
            cartao.add_widget(valores)

            cartao.add_widget(C.Texto(text="Conduta", estilo="secao", color=COR["acento_escuro"]))
            cartao.add_widget(C.Texto(text=ex["conducao"], estilo="corpo"))
            blocos.append(cartao)
        return blocos

    def _imagens(self):
        blocos = []
        for img in self.imagens:
            cartao = C.Cartao(spacing=dp(10))
            cartao.add_widget(C.Texto(text=img["titulo"], estilo="subtitulo"))
            cartao.add_widget(C.Texto(text=img["descricao"], estilo="apoio"))
            caminho = IMG_DIR / img["arquivo"]
            if caminho.exists():
                cartao.add_widget(Image(source=str(caminho), size_hint_y=None,
                                        height=dp(220), fit_mode="contain"))
            else:
                cartao.add_widget(C.Texto(
                    text=f"Imagem ausente: {img['arquivo']}. "
                         "Gere com: python criar_imagens.py",
                    estilo="micro", color=COR["ambar"]))
            blocos.append(cartao)
        return blocos

    def _fontes(self):
        blocos = []
        for ref in self.extras.get("referencias", []):
            cartao = C.Cartao(spacing=dp(8))
            cartao.add_widget(C.Texto(text=ref["titulo"], estilo="subtitulo"))
            cartao.add_widget(C.Texto(text=ref["fonte"], estilo="micro"))
            if ref.get("nota"):
                cartao.add_widget(C.Texto(text=ref["nota"], estilo="apoio"))
            botao = C.Botao("Abrir referência", variante="secundario", icone="link",
                            height=dp(46), tamanho_fonte="14sp")
            botao.bind(on_release=lambda *_, u=ref["url"]: abrir_link(u))
            cartao.add_widget(botao)
            blocos.append(cartao)
        return blocos

    def _videos(self):
        blocos = []
        for video in self.extras.get("videos", []):
            cartao = C.Cartao(spacing=dp(8))
            cartao.add_widget(C.Texto(text=video["titulo"], estilo="subtitulo"))
            detalhe = " · ".join(x for x in (video.get("canal"), video.get("duracao")) if x)
            if detalhe:
                cartao.add_widget(C.Texto(text=detalhe, estilo="micro"))
            botao = C.Botao("Assistir", variante="neutro", icone="play",
                            height=dp(46), tamanho_fonte="14sp")
            botao.bind(on_release=lambda *_, u=video["url"]: abrir_link(
                u.replace("/embed/", "/watch?v=")))
            cartao.add_widget(botao)
            blocos.append(cartao)
        return blocos


def abrir_link(url):
    """Abre só endereços https: os links vêm dos dados do app, mas um arquivo
    de dados alterado não deve conseguir disparar outro tipo de esquema."""
    if not str(url).lower().startswith("https://"):
        print(f"[link] endereço recusado (não é https): {url!r}")
        return
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[link] não foi possível abrir: {e}")
