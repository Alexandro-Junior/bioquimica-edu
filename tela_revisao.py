"""
Sessão de revisão — o modo de estudo principal do BioquímicaEDU.

O ciclo de cada item é deliberado, e a ordem importa:

  1. Pergunta        recuperação ativa: você tenta lembrar antes de ver
  2. Confiança       você declara o quanto acha que sabe, ANTES da resposta
  3. Resposta        confere
  4. Autoavaliação   diz como foi, e isso reagenda o item

Por que perguntar a confiança antes de revelar: depois de ver a resposta
todo mundo acha que sabia. Capturar a estimativa antes é o que permite
medir calibração de forma honesta — e é justamente a lacuna que o
estudante não enxerga sozinho.

Por que a autoavaliação em quatro botões, e não só certo/errado: o SM-2
precisa de graduação para ajustar o intervalo. "Acertei com esforço" e
"acertei de imediato" levam a agendamentos diferentes, e essa diferença
é o que faz o intervalo convergir para a memória real de cada um.
"""

from __future__ import annotations

import tkinter as tk

from painel_inicio import COR, FONTE, BotaoAcao, cartao, titulo_secao, Animacao

# Autoavaliação -> qualidade do SM-2 (0 a 5)
AVALIACOES = [
    ("De novo",   0, COR["rubro"],  "Não lembrei"),
    ("Difícil",   3, COR["ambar"],  "Lembrei com esforço"),
    ("Bom",       4, COR["acento"], "Lembrei"),
    ("Fácil",     5, COR["indigo"], "Imediato"),
]

NIVEIS_CONFIANCA = [
    (1, "Nenhuma"),
    (2, "Pouca"),
    (3, "Média"),
    (4, "Boa"),
    (5, "Total"),
]


class TelaRevisao(tk.Frame):
    """`controller` precisa expor .progresso, .marcadores e .mostrar(nome)."""

    def __init__(self, master, controller):
        super().__init__(master, bg=COR["fundo"])
        self.controller = controller
        self.progresso = controller.progresso
        self.por_sigla = {m["sigla"]: m for m in controller.marcadores}

        siglas = [m["sigla"] for m in controller.marcadores]
        self.fila = self.progresso.fila_do_dia(siglas)
        self.posicao = 0
        self.confianca = None
        self.revelado = False
        self.acertos = 0

        self._cabecalho()
        self.palco = tk.Frame(self, bg=COR["fundo"])
        self.palco.pack(fill=tk.BOTH, expand=True, padx=26, pady=18)
        self._mostrar_item()

    # ── topo ────────────────────────────────────────────────────────
    def _cabecalho(self):
        topo = tk.Frame(self, bg=COR["superficie"], height=58)
        topo.pack(fill=tk.X)
        topo.pack_propagate(False)
        tk.Frame(self, bg=COR["borda"], height=1).pack(fill=tk.X)

        tk.Button(topo, text="< Sair", font=FONTE["corpo"], fg=COR["tinta2"],
                  bg=COR["superficie"], relief="flat", cursor="hand2",
                  activebackground=COR["superficie"],
                  command=lambda: self.controller.mostrar("inicio")
                  ).pack(side=tk.LEFT, padx=20)

        self.rotulo_passo = tk.Label(topo, text="", font=FONTE["forte"],
                                     fg=COR["tinta"], bg=COR["superficie"])
        self.rotulo_passo.pack(side=tk.LEFT, expand=True)

        self.trilho = tk.Canvas(topo, height=4, bg=COR["superficie"],
                                highlightthickness=0, width=200)
        self.trilho.pack(side=tk.RIGHT, padx=20)

    def _atualizar_trilho(self):
        total = len(self.fila) or 1
        fracao = self.posicao / total
        self.rotulo_passo.config(
            text=f"{min(self.posicao + 1, total)} de {total}")

        def passo(t):
            self.trilho.delete("all")
            largura = self.trilho.winfo_width() or 200
            self.trilho.create_rectangle(0, 0, largura, 4,
                                         fill=COR["borda"], outline="")
            w = largura * fracao * t
            if w > 0.5:
                self.trilho.create_rectangle(0, 0, w, 4,
                                             fill=COR["acento"], outline="")
        Animacao(self.trilho, passo, duracao_ms=400)

    # ── ciclo ───────────────────────────────────────────────────────
    def _limpar(self):
        for w in self.palco.winfo_children():
            w.destroy()

    def _mostrar_item(self):
        self._limpar()
        self.confianca = None
        self.revelado = False

        if not self.fila:
            self._sem_fila()
            return
        if self.posicao >= len(self.fila):
            self._encerrar()
            return

        self._atualizar_trilho()
        sigla = self.fila[self.posicao]
        marcador = self.por_sigla[sigla]

        c = cartao(self.palco, padding=26)
        c.pack(fill=tk.BOTH, expand=True)
        self.miolo = c.miolo

        tk.Label(self.miolo, text=marcador["categoria"].upper(),
                 font=FONTE["micro"], fg=COR["tinta3"],
                 bg=COR["superficie"]).pack(anchor=tk.W)
        tk.Label(self.miolo, text=marcador["nome"],
                 font=("Segoe UI", 22, "bold"), fg=COR["tinta"],
                 bg=COR["superficie"]).pack(anchor=tk.W, pady=(2, 0))
        tk.Label(self.miolo, text=f"Sigla: {sigla}", font=FONTE["mini"],
                 fg=COR["tinta2"], bg=COR["superficie"]).pack(anchor=tk.W)

        tk.Frame(self.miolo, bg=COR["borda"], height=1).pack(fill=tk.X, pady=16)

        tk.Label(self.miolo,
                 text="Qual a faixa de referência e o que significa estar alterado?",
                 font=("Segoe UI", 13), fg=COR["tinta"], bg=COR["superficie"],
                 wraplength=620, justify=tk.LEFT).pack(anchor=tk.W)

        # A resposta cresce conforme o conteúdo; as ações ficam logo
        # abaixo dela. Sem expand aqui, senão a área vazia empurra os
        # botões para fora da janela antes da revelação.
        self.area_resposta = tk.Frame(self.miolo, bg=COR["superficie"])
        self.area_resposta.pack(fill=tk.X, pady=(14, 0))

        self.area_acao = tk.Frame(self.miolo, bg=COR["superficie"])
        self.area_acao.pack(fill=tk.X, pady=(16, 0))

        self._perguntar_confianca()

    def _perguntar_confianca(self):
        """Passo 2: estimativa declarada antes de ver a resposta."""
        for w in self.area_acao.winfo_children():
            w.destroy()

        tk.Label(self.area_acao, text="Antes de ver: o quanto você acha que sabe?",
                 font=FONTE["corpo"], fg=COR["tinta2"],
                 bg=COR["superficie"]).pack(anchor=tk.W, pady=(0, 8))

        linha = tk.Frame(self.area_acao, bg=COR["superficie"])
        linha.pack(anchor=tk.W)

        self.botoes_confianca = []
        for valor, rotulo in NIVEIS_CONFIANCA:
            b = tk.Button(linha, text=rotulo, font=FONTE["mini"],
                          fg=COR["tinta2"], bg=COR["fundo"], relief="flat",
                          cursor="hand2", padx=14, pady=7,
                          activebackground=COR["acento_luz"],
                          command=lambda v=valor: self._definir_confianca(v))
            b.pack(side=tk.LEFT, padx=(0, 6))
            self.botoes_confianca.append((valor, b))

    def _definir_confianca(self, valor):
        self.confianca = valor
        for v, b in self.botoes_confianca:
            marcado = v == valor
            b.config(bg=COR["acento"] if marcado else COR["fundo"],
                     fg=COR["branco"] if marcado else COR["tinta2"])
        self._mostrar_revelar()

    def _mostrar_revelar(self):
        for w in list(self.area_acao.winfo_children())[2:]:
            w.destroy()
        BotaoAcao(self.area_acao, "Ver resposta", self._revelar,
                  largura=180).pack(anchor=tk.W, pady=(12, 0))

    def _revelar(self):
        """Passo 3: mostra o conteúdo e pede a autoavaliação."""
        if self.revelado:
            return
        self.revelado = True

        sigla = self.fila[self.posicao]
        m = self.por_sigla[sigla]

        for w in self.area_acao.winfo_children():
            w.destroy()

        faixa = tk.Frame(self.area_resposta, bg=COR["acento_luz"])
        faixa.pack(fill=tk.X)
        tk.Label(faixa,
                 text=f"{m['valor_ref_min']} a {m['valor_ref_max']} {m['unidade']}",
                 font=("Segoe UI", 17, "bold"), fg=COR["acento_alt"],
                 bg=COR["acento_luz"]).pack(anchor=tk.W, padx=14, pady=10)

        for titulo, chave, doencas, cor in (
            ("Quando está elevado", "interpretacao_alta",
             "doencas_associadas_alta", COR["rubro"]),
            ("Quando está baixo", "interpretacao_baixa",
             "doencas_associadas_baixa", COR["indigo"]),
        ):
            bloco = tk.Frame(self.area_resposta, bg=COR["superficie"])
            bloco.pack(fill=tk.X, pady=(12, 0))
            tk.Label(bloco, text=titulo, font=FONTE["secao"], fg=cor,
                     bg=COR["superficie"]).pack(anchor=tk.W)
            tk.Label(bloco, text=m.get(chave, "-"), font=FONTE["corpo"],
                     fg=COR["tinta"], bg=COR["superficie"], wraplength=620,
                     justify=tk.LEFT).pack(anchor=tk.W)
            associadas = m.get(doencas, "").strip()
            if associadas and associadas != "—":
                tk.Label(bloco, text=associadas, font=FONTE["mini"],
                         fg=COR["tinta2"], bg=COR["superficie"], wraplength=620,
                         justify=tk.LEFT).pack(anchor=tk.W, pady=(2, 0))

        self._pedir_autoavaliacao()

    def _pedir_autoavaliacao(self):
        """Passo 4: a nota do estudante reagenda o item."""
        tk.Label(self.area_acao, text="Como foi lembrar disso?",
                 font=FONTE["corpo"], fg=COR["tinta2"],
                 bg=COR["superficie"]).pack(anchor=tk.W, pady=(0, 8))

        linha = tk.Frame(self.area_acao, bg=COR["superficie"])
        linha.pack(anchor=tk.W)

        sigla = self.fila[self.posicao]
        for rotulo, qualidade, cor, dica in AVALIACOES:
            proximo = self._previsao(sigla, qualidade)
            b = tk.Frame(linha, bg=cor, cursor="hand2")
            b.pack(side=tk.LEFT, padx=(0, 8))
            interno = tk.Frame(b, bg=cor)
            interno.pack(padx=16, pady=8)
            tk.Label(interno, text=rotulo, font=FONTE["forte"],
                     fg=COR["branco"], bg=cor).pack()
            tk.Label(interno, text=proximo, font=FONTE["micro"],
                     fg=COR["branco"], bg=cor).pack()
            for w in (b, interno, *interno.winfo_children()):
                w.bind("<Button-1>",
                       lambda _e, q=qualidade: self._responder(q))

        tk.Label(self.area_acao,
                 text="A escolha define quando este marcador volta a aparecer.",
                 font=FONTE["micro"], fg=COR["tinta3"],
                 bg=COR["superficie"]).pack(anchor=tk.W, pady=(8, 0))

    def _previsao(self, sigla, qualidade):
        """Mostra no botão quando o item voltaria — torna o efeito visível."""
        from progresso import (INTERVALO_1, INTERVALO_2,
                               INTERVALO_FACIL_INICIAL)
        e = self.progresso.estado(sigla)
        if qualidade < 3:
            dias = INTERVALO_1
        elif e["repeticoes"] == 0:
            dias = INTERVALO_FACIL_INICIAL if qualidade == 5 else INTERVALO_1
        elif e["repeticoes"] == 1:
            dias = INTERVALO_2
        else:
            dias = max(1, round(e["intervalo"] * e["facilidade"]))
        if dias == 1:
            return "amanhã"
        if dias < 30:
            return f"em {dias} dias"
        return f"em {dias // 30} mês(es)"

    def _responder(self, qualidade):
        sigla = self.fila[self.posicao]
        self.progresso.registrar_resposta(sigla, qualidade,
                                          confianca=self.confianca)
        if qualidade >= 3:
            self.acertos += 1
        self.posicao += 1
        self._mostrar_item()

    # ── fim ─────────────────────────────────────────────────────────
    def _sem_fila(self):
        c = cartao(self.palco, padding=30)
        c.pack(fill=tk.X)
        tk.Label(c.miolo, text="Nada para revisar agora",
                 font=("Segoe UI", 19, "bold"), fg=COR["tinta"],
                 bg=COR["superficie"]).pack(anchor=tk.W)
        tk.Label(c.miolo,
                 text="Todos os marcadores estão em dia. Voltar antes da hora "
                      "reforça menos do que esperar o intervalo certo.",
                 font=FONTE["corpo"], fg=COR["tinta2"], bg=COR["superficie"],
                 wraplength=560, justify=tk.LEFT).pack(anchor=tk.W, pady=(6, 16))
        BotaoAcao(c.miolo, "Voltar ao início",
                  lambda: self.controller.mostrar("inicio")).pack(anchor=tk.W)

    def _encerrar(self):
        self._limpar()
        total = len(self.fila)

        c = cartao(self.palco, padding=30)
        c.pack(fill=tk.X)
        miolo = c.miolo

        tk.Label(miolo, text="Sessão concluída", font=("Segoe UI", 22, "bold"),
                 fg=COR["tinta"], bg=COR["superficie"]).pack(anchor=tk.W)
        tk.Label(miolo, text=f"{self.acertos} de {total} lembrados",
                 font=FONTE["corpo"], fg=COR["tinta2"],
                 bg=COR["superficie"]).pack(anchor=tk.W, pady=(4, 0))

        siglas = list(self.por_sigla)
        restante = self.progresso.fila_do_dia(siglas)
        if restante:
            recado = (f"Ainda há {len(restante)} item(ns) para hoje — "
                      "inclusive os que você marcou como 'de novo'.")
        else:
            recado = ("Sua fila de hoje acabou. Os itens voltam sozinhos "
                      "quando a memória começar a ceder.")
        tk.Label(miolo, text=recado, font=FONTE["corpo"], fg=COR["tinta2"],
                 bg=COR["superficie"], wraplength=560,
                 justify=tk.LEFT).pack(anchor=tk.W, pady=(14, 18))

        acoes = tk.Frame(miolo, bg=COR["superficie"])
        acoes.pack(anchor=tk.W)
        if restante:
            BotaoAcao(acoes, "Continuar revisando",
                      lambda: self.controller.mostrar("revisao"),
                      largura=190).pack(side=tk.LEFT, padx=(0, 10))
        BotaoAcao(acoes, "Voltar ao início",
                  lambda: self.controller.mostrar("inicio"),
                  cor=COR["tinta2"] if restante else COR["acento"],
                  largura=170).pack(side=tk.LEFT)
