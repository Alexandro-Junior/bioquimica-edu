"""
Tela inicial do BioquímicaEDU — o painel de estudo.

A pergunta que esta tela responde é uma só: "o que eu faço agora?".
Tudo aqui existe para respondê-la em poucos segundos, e só depois
oferecer contexto.

Por que não uma trilha de lições:
  Trilha linear pressupõe conteúdo que se ordena e se esgota. Marcadores
  bioquímicos não funcionam assim — são revisitados, esquecidos e
  reaprendidos. O que decide o dia não é "qual a próxima lição", e sim
  "o que está prestes a ser esquecido". Por isso a tela mostra o estado
  da memória, não um caminho.

Ordem das seções, por prioridade de decisão:
  1. Hoje         a decisão do dia, com uma única ação em destaque
  2. Memória      em que estágio está cada marcador
  3. Sistemas     domínio por área (hepático, renal, ...)
  4. Onde focar   os marcadores mais frágeis, com atalho
  5. Autoavaliação  o que você acha que sabe vs. o que acerta
  6. Constância   28 dias de atividade
  7. Marcos       conquistas ligadas a aprendizado
"""

from __future__ import annotations

import tkinter as tk

from painel_inicio import (
    COR, COR_ESTAGIO, ROTULO_ESTAGIO, FONTE,
    AnelDia, BarraEstagios, BarraDominio, ReguaCalibracao, Constancia,
    BotaoAcao, cartao, titulo_secao,
)


class PainelInicio(tk.Frame):
    """`controller` precisa expor: .progresso, .marcadores e .mostrar(nome)."""

    def __init__(self, master, controller):
        super().__init__(master, bg=COR["fundo"])
        self.controller = controller
        self.marcadores = controller.marcadores
        self.siglas = [m["sigla"] for m in self.marcadores]
        self.categorias = {m["sigla"]: m["categoria"] for m in self.marcadores}
        self.nome = {m["sigla"]: m["nome"] for m in self.marcadores}
        self.resumo = controller.progresso.resumo(self.siglas, self.categorias)
        self._construir()

    # ── estrutura ───────────────────────────────────────────────────
    def _construir(self):
        self._cabecalho()

        corpo = tk.Frame(self, bg=COR["fundo"])
        corpo.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(corpo, bg=COR["fundo"], highlightthickness=0)
        barra = tk.Scrollbar(corpo, orient="vertical", command=canvas.yview)
        interior = tk.Frame(canvas, bg=COR["fundo"])

        janela = canvas.create_window((0, 0), window=interior, anchor="nw")
        interior.bind("<Configure>",
                      lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(janela, width=e.width))
        canvas.configure(yscrollcommand=barra.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barra.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas = canvas
        canvas.bind("<Enter>", lambda _: canvas.bind_all("<MouseWheel>", self._rolar))
        canvas.bind("<Leave>", lambda _: canvas.unbind_all("<MouseWheel>"))

        area = tk.Frame(interior, bg=COR["fundo"])
        area.pack(fill=tk.BOTH, expand=True, padx=26, pady=(18, 26))

        self._cartao_hoje(area)

        colunas = tk.Frame(area, bg=COR["fundo"])
        colunas.pack(fill=tk.BOTH, expand=True, pady=(14, 0))
        colunas.columnconfigure(0, weight=3, uniform="c")
        colunas.columnconfigure(1, weight=2, uniform="c")

        esquerda = tk.Frame(colunas, bg=COR["fundo"])
        esquerda.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        direita = tk.Frame(colunas, bg=COR["fundo"])
        direita.grid(row=0, column=1, sticky="nsew", padx=(7, 0))

        self._cartao_memoria(esquerda)
        self._cartao_sistemas(esquerda)
        self._cartao_focar(direita)
        self._cartao_calibracao(direita)
        self._cartao_constancia(direita)
        self._cartao_marcos(area)
        self._barra_modos(area)

    def _rolar(self, evento):
        self._canvas.yview_scroll(int(-evento.delta / 120), "units")

    def _cabecalho(self):
        topo = tk.Frame(self, bg=COR["superficie"], height=64)
        topo.pack(fill=tk.X)
        topo.pack_propagate(False)
        tk.Frame(self, bg=COR["borda"], height=1).pack(fill=tk.X)

        esq = tk.Frame(topo, bg=COR["superficie"])
        esq.pack(side=tk.LEFT, padx=26)
        tk.Label(esq, text="BioquímicaEDU", font=FONTE["titulo"],
                 fg=COR["tinta"], bg=COR["superficie"]).pack(anchor=tk.W, pady=(11, 0))
        tk.Label(esq, text="Marcadores bioquímicos no diagnóstico clínico",
                 font=FONTE["micro"], fg=COR["tinta3"],
                 bg=COR["superficie"]).pack(anchor=tk.W)

        dir_ = tk.Frame(topo, bg=COR["superficie"])
        dir_.pack(side=tk.RIGHT, padx=26)
        dias = self.resumo["sequencia"]
        texto = "primeiro dia" if dias <= 1 else f"{dias} dias seguidos"
        tk.Label(dir_, text=texto, font=FONTE["forte"], fg=COR["tinta2"],
                 bg=COR["superficie"]).pack(anchor=tk.E, pady=(16, 0))
        tk.Label(dir_, text=f"{self.resumo['revisados_hoje']} revisões hoje",
                 font=FONTE["micro"], fg=COR["tinta3"],
                 bg=COR["superficie"]).pack(anchor=tk.E)

    # ── 1. hoje ─────────────────────────────────────────────────────
    def _cartao_hoje(self, parent):
        c = cartao(parent, padding=20)
        c.pack(fill=tk.X)
        miolo = c.miolo

        fila = self.resumo["fila"]
        vencidos = self.resumo["vencidos"]
        reforco = self.resumo["reforco"]
        novos = self.resumo["novos"]
        feitos = self.resumo["revisados_hoje"]

        linha = tk.Frame(miolo, bg=COR["superficie"])
        linha.pack(fill=tk.X)

        anel = AnelDia(linha)
        anel.pack(side=tk.LEFT, padx=(0, 22))
        cor_anel = COR["ambar"] if vencidos else COR["acento"]
        anel.definir(feitos, feitos + len(fila), cor_anel)

        texto = tk.Frame(linha, bg=COR["superficie"])
        texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        primeiro_uso = novos == len(self.siglas)
        rotulo_acao = "Começar revisão de hoje"

        if primeiro_uso:
            titulo = "Comece por aqui"
            detalhe = (f"São {len(self.siglas)} marcadores. Você não precisa ver "
                       "todos hoje: o app apresenta poucos por vez e traz cada um "
                       "de volta pouco antes de você esquecer.")
            rotulo_acao = "Estudar os primeiros"
        elif reforco:
            titulo = "Corrija o que errou hoje"
            detalhe = (f"{reforco} marcador(es) que você errou nesta sessão. "
                       "Rever agora, com o erro fresco, é o que fixa a correção.")
            rotulo_acao = "Retomar os que errei"
        elif vencidos:
            titulo = "Sua revisão de hoje está pronta"
            detalhe = (f"{vencidos} marcador(es) chegaram ao ponto de revisão — "
                       "no limite entre lembrar e esquecer, que é onde rever rende mais.")
        elif fila:
            titulo = "Revisões em dia"
            detalhe = ("Nada vencido hoje. Você pode avançar em "
                       f"{min(len(fila), novos)} marcador(es) ainda não estudados.")
            rotulo_acao = "Aprender algo novo"
        else:
            titulo = "Tudo revisado"
            detalhe = ("Você já estudou todos os marcadores e nenhum venceu hoje. "
                       "O app chama de volta quando a memória precisar.")

        tk.Label(texto, text=titulo, font=("Segoe UI", 17, "bold"),
                 fg=COR["tinta"], bg=COR["superficie"]).pack(anchor=tk.W, pady=(6, 4))
        tk.Label(texto, text=detalhe, font=FONTE["corpo"], fg=COR["tinta2"],
                 bg=COR["superficie"], wraplength=470, justify=tk.LEFT
                 ).pack(anchor=tk.W)

        if fila:
            minutos = self.resumo["minutos_estimados"]
            previa = ", ".join(fila[:4]) + ("..." if len(fila) > 4 else "")
            tk.Label(texto,
                     text=f"{len(fila)} itens · cerca de {minutos} min · {previa}",
                     font=FONTE["mini"], fg=COR["tinta3"],
                     bg=COR["superficie"]).pack(anchor=tk.W, pady=(8, 0))

        acoes = tk.Frame(texto, bg=COR["superficie"])
        acoes.pack(anchor=tk.W, pady=(14, 2))

        if fila:
            BotaoAcao(acoes, rotulo_acao,
                      lambda: self.controller.mostrar("revisao"),
                      cor=cor_anel, largura=232).pack(side=tk.LEFT)
        else:
            BotaoAcao(acoes, "Praticar mesmo assim",
                      lambda: self.controller.mostrar("quiz"),
                      largura=190).pack(side=tk.LEFT)

        tk.Button(acoes, text="Explorar marcadores", font=FONTE["corpo"],
                  fg=COR["tinta2"], bg=COR["superficie"], relief="flat",
                  cursor="hand2", activebackground=COR["superficie"],
                  command=lambda: self.controller.mostrar("estudo")
                  ).pack(side=tk.LEFT, padx=14)

    # ── 2. memória ──────────────────────────────────────────────────
    def _cartao_memoria(self, parent):
        c = cartao(parent)
        c.pack(fill=tk.X, pady=(0, 14))
        miolo = c.miolo

        dominio = self.resumo["dominio_geral"]
        titulo_secao(miolo, "Estado da memória", f"{dominio * 100:.0f}% de domínio")

        barra = BarraEstagios(miolo)
        barra.pack(fill=tk.X, pady=(12, 10))
        barra.definir(self.resumo["estagios"])

        legenda = tk.Frame(miolo, bg=COR["superficie"])
        legenda.pack(fill=tk.X)
        for chave in ("consolidado", "firmando", "aprendendo", "novo"):
            item = tk.Frame(legenda, bg=COR["superficie"])
            item.pack(side=tk.LEFT, padx=(0, 14))
            ponto = tk.Canvas(item, width=9, height=9, bg=COR["superficie"],
                              highlightthickness=0)
            ponto.create_oval(1, 1, 8, 8, fill=COR_ESTAGIO[chave], outline="")
            ponto.pack(side=tk.LEFT, pady=(1, 0))
            tk.Label(item, text=f" {ROTULO_ESTAGIO[chave]}", font=FONTE["mini"],
                     fg=COR["tinta2"], bg=COR["superficie"]).pack(side=tk.LEFT)

        tk.Label(miolo,
                 text="Um marcador vira consolidado quando você acerta com "
                      "intervalos cada vez maiores entre as revisões.",
                 font=FONTE["mini"], fg=COR["tinta3"], bg=COR["superficie"],
                 wraplength=430, justify=tk.LEFT).pack(anchor=tk.W, pady=(12, 0))

    # ── 3. sistemas ─────────────────────────────────────────────────
    def _cartao_sistemas(self, parent):
        c = cartao(parent)
        c.pack(fill=tk.X)
        miolo = c.miolo
        titulo_secao(miolo, "Por sistema")

        grade = tk.Frame(miolo, bg=COR["superficie"])
        grade.pack(fill=tk.X, pady=(12, 0))
        grade.columnconfigure(1, weight=1)

        ordenado = sorted(self.resumo["dominio_categoria"].items(),
                          key=lambda kv: -kv[1])
        for i, (categoria, valor) in enumerate(ordenado):
            tk.Label(grade, text=categoria, font=FONTE["corpo"], fg=COR["tinta"],
                     bg=COR["superficie"], width=11, anchor=tk.W
                     ).grid(row=i, column=0, sticky="w", pady=4)
            b = BarraDominio(grade)
            b.grid(row=i, column=1, sticky="ew", padx=10, pady=4)
            b.definir(valor, atraso_ms=200 + i * 55)
            tk.Label(grade, text=f"{valor * 100:.0f}%", font=FONTE["mini"],
                     fg=COR["tinta2"], bg=COR["superficie"], width=4, anchor=tk.E
                     ).grid(row=i, column=2, sticky="e", pady=4)

    # ── 4. onde focar ───────────────────────────────────────────────
    def _cartao_focar(self, parent):
        fracos = self.resumo["pontos_fracos"]
        if not fracos:
            return
        c = cartao(parent)
        c.pack(fill=tk.X, pady=(0, 14))
        miolo = c.miolo
        titulo_secao(miolo, "Onde focar")

        tk.Label(miolo, text="Seus marcadores mais frágeis agora",
                 font=FONTE["mini"], fg=COR["tinta3"], bg=COR["superficie"]
                 ).pack(anchor=tk.W, pady=(2, 8))

        for sigla, dominio in fracos:
            linha = tk.Frame(miolo, bg=COR["superficie"], cursor="hand2")
            linha.pack(fill=tk.X, pady=3)

            cor_faixa = COR["rubro"] if dominio < 0.3 else COR["ambar"]
            faixa = tk.Frame(linha, bg=cor_faixa, width=3, height=34)
            faixa.pack(side=tk.LEFT, fill=tk.Y)
            faixa.pack_propagate(False)

            info = tk.Frame(linha, bg=COR["superficie"])
            info.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(9, 0))
            tk.Label(info, text=f"{sigla} · {self.nome.get(sigla, '')[:26]}",
                     font=FONTE["forte"], fg=COR["tinta"], bg=COR["superficie"]
                     ).pack(anchor=tk.W)
            tk.Label(info, text=f"{dominio * 100:.0f}% de domínio",
                     font=FONTE["micro"], fg=COR["tinta2"], bg=COR["superficie"]
                     ).pack(anchor=tk.W)

            for w in (linha, info, *info.winfo_children()):
                w.bind("<Button-1>",
                       lambda _e, s=sigla: self.controller.mostrar("estudo", foco=s))

    # ── 5. autoavaliação ────────────────────────────────────────────
    def _cartao_calibracao(self, parent):
        cal = self.resumo["calibracao"]
        c = cartao(parent)
        c.pack(fill=tk.X, pady=(0, 14))
        miolo = c.miolo
        titulo_secao(miolo, "Autoavaliação")

        if not cal or not cal.get("suficiente"):
            faltam = max(1, 10 - (cal or {}).get("amostra", 0))
            tk.Label(miolo,
                     text=f"Responda mais {faltam} questões dizendo o quanto tem "
                          "certeza. Depois comparamos sua confiança com seus acertos.",
                     font=FONTE["mini"], fg=COR["tinta3"], bg=COR["superficie"],
                     wraplength=250, justify=tk.LEFT).pack(anchor=tk.W, pady=(6, 2))
            return

        regua = ReguaCalibracao(miolo)
        regua.pack(fill=tk.X, pady=(10, 2))
        regua.definir(cal["confianca"], cal["acerto"])

        tk.Label(miolo, text=cal["leitura"], font=FONTE["mini"],
                 fg=COR["tinta"], bg=COR["superficie"],
                 wraplength=250, justify=tk.LEFT).pack(anchor=tk.W, pady=(6, 0))
        tk.Label(miolo, text=f"com base nas últimas {cal['amostra']} respostas",
                 font=FONTE["micro"], fg=COR["tinta3"], bg=COR["superficie"]
                 ).pack(anchor=tk.W, pady=(2, 0))

    # ── 6. constância ───────────────────────────────────────────────
    def _cartao_constancia(self, parent):
        c = cartao(parent)
        c.pack(fill=tk.X, pady=(0, 14))
        miolo = c.miolo
        titulo_secao(miolo, "Constância", "28 dias")

        grafico = Constancia(miolo)
        grafico.pack(fill=tk.X, pady=(10, 0))
        grafico.definir(self.resumo["atividade"])

        ativos = sum(1 for _, v in self.resumo["atividade"] if v)
        tk.Label(miolo, text=f"{ativos} dias com estudo nas últimas 4 semanas",
                 font=FONTE["micro"], fg=COR["tinta3"], bg=COR["superficie"]
                 ).pack(anchor=tk.W, pady=(4, 0))

    # ── 7. marcos ───────────────────────────────────────────────────
    def _cartao_marcos(self, parent):
        conquistas = self.resumo["conquistas"]
        c = cartao(parent)
        c.pack(fill=tk.X, pady=(14, 0))
        miolo = c.miolo

        obtidas = sum(1 for x in conquistas if x["alcancada"])
        titulo_secao(miolo, "Marcos", f"{obtidas} de {len(conquistas)}")

        faixa = tk.Frame(miolo, bg=COR["superficie"])
        faixa.pack(fill=tk.X, pady=(12, 0))

        for marco in conquistas:
            feito = marco["alcancada"]
            fundo = COR["acento_luz"] if feito else COR["fundo"]
            selo = tk.Frame(faixa, bg=fundo)
            selo.pack(side=tk.LEFT, padx=(0, 8))
            interno = tk.Frame(selo, bg=fundo)
            interno.pack(padx=11, pady=8)
            tk.Label(interno, text=marco["titulo"], font=FONTE["mini"],
                     fg=COR["acento_alt"] if feito else COR["tinta3"],
                     bg=fundo).pack()
            tk.Label(interno, text=marco["descricao"], font=FONTE["micro"],
                     fg=COR["tinta2"] if feito else COR["tinta3"],
                     bg=fundo, wraplength=125, justify=tk.CENTER).pack()

    # ── acesso aos modos ────────────────────────────────────────────
    def _barra_modos(self, parent):
        faixa = tk.Frame(parent, bg=COR["fundo"])
        faixa.pack(fill=tk.X, pady=(16, 0))

        modos = [
            ("Estudo",      "Consultar marcadores", "estudo"),
            ("Flashcards",  "Recuperação rápida",   "flashcards"),
            ("Quiz",        "Testar conhecimento",  "quiz"),
            ("Diagnóstico", "Interpretar casos",    "diagnostico"),
        ]
        for i, (titulo, descricao, destino) in enumerate(modos):
            faixa.columnconfigure(i, weight=1, uniform="m")
            c = cartao(faixa, padding=13)
            c.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0))
            miolo = c.miolo
            tk.Label(miolo, text=titulo, font=FONTE["forte"], fg=COR["tinta"],
                     bg=COR["superficie"]).pack(anchor=tk.W)
            tk.Label(miolo, text=descricao, font=FONTE["micro"], fg=COR["tinta3"],
                     bg=COR["superficie"]).pack(anchor=tk.W)

            for w in (c, miolo, *miolo.winfo_children()):
                w.configure(cursor="hand2")
                w.bind("<Button-1>",
                       lambda _e, d=destino: self.controller.mostrar(d))
