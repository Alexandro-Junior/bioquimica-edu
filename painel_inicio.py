"""
Tela inicial do BioquímicaEDU — painel de estudo.

A ideia que organiza esta tela: quando o estudante abre o app, ele tem
uma pergunta só — "o que eu faço agora?". Tudo aqui existe para responder
isso em menos de dois segundos, e só depois oferecer contexto.

Por que não uma trilha de lições:
  Trilha linear pressupõe conteúdo que se ordena e se esgota. Marcadores
  bioquímicos não funcionam assim — eles são revisitados, esquecidos e
  reaprendidos. O que decide o dia não é "qual a próxima lição", é "o que
  está prestes a ser esquecido". Por isso a tela é um painel de estado da
  memória, não um caminho.

Hierarquia, de cima para baixo:
  1. Hoje          decisão do dia, com uma única ação em destaque
  2. Memória       em que estágio está cada marcador
  3. Calibração    o que você acha que sabe vs. o que acerta
  4. Onde focar    os marcadores mais frágeis, com atalho
  5. Sistemas      domínio por área (hepático, renal, ...)
  6. Constância    28 dias de atividade
  7. Marcos        conquistas ligadas a aprendizado

As animações são todas informativas: o anel preenche até a fração real
do dia, as barras crescem até o domínio real. Nada anima só para enfeitar
— movimento sem dado por trás vira ruído e cansa em uso diário.
"""

from __future__ import annotations

import tkinter as tk
from datetime import date

# ── Paleta ──────────────────────────────────────────────────────────
# Fundo de papel quente com acentos de reagente. Superfícies claras e
# uma cor forte só na ação principal, para o olho saber onde ir.
COR = {
    "fundo":       "#F7F5F1",
    "superficie":  "#FFFFFF",
    "borda":       "#E7E3DC",
    "tinta":       "#16211C",
    "tinta2":      "#5C6560",
    "tinta3":      "#9AA29D",

    "acento":      "#0E7C5A",   # verde de laboratório, ação principal
    "acento_alt":  "#0A5F45",
    "acento_luz":  "#E3F2EB",

    "ambar":       "#C77A16",   # atenção: revisões atrasadas
    "ambar_luz":   "#FBF0DC",
    "rubro":       "#B3352F",   # fragilidade
    "rubro_luz":   "#FBE9E7",
    "indigo":      "#3D5A98",   # metacognição
    "indigo_luz":  "#E8EDF7",
    "branco":      "#FFFFFF",
}

# Cor por estágio de memória — progressão fria para quente conforme fixa
COR_ESTAGIO = {
    "novo":        "#C8CFCA",
    "aprendendo":  "#E0A458",
    "firmando":    "#5B9BD5",
    "consolidado": "#0E7C5A",
}

ROTULO_ESTAGIO = {
    "novo":        "Não estudados",
    "aprendendo":  "Aprendendo",
    "firmando":    "Firmando",
    "consolidado": "Consolidados",
}

FONTE = {
    "gigante": ("Segoe UI", 40, "bold"),
    "titulo":  ("Segoe UI", 19, "bold"),
    "secao":   ("Segoe UI", 11, "bold"),
    "corpo":   ("Segoe UI", 10),
    "forte":   ("Segoe UI", 10, "bold"),
    "mini":    ("Segoe UI", 9),
    "micro":   ("Segoe UI", 8),
}


def suavizar(t: float) -> float:
    """Desaceleração cúbica: rápido no início, calmo no fim.

    Movimento linear parece mecânico; este perfil imita algo chegando ao
    repouso, que o olho lê como natural sem prestar atenção nele.
    """
    return 1 - pow(1 - t, 3)


class Animacao:
    """Interpola de 0 a 1 chamando `passo` a cada quadro."""

    def __init__(self, widget, passo, duracao_ms=650, atraso_ms=0):
        self.widget = widget
        self.passo = passo
        self.duracao = duracao_ms
        self.quadro = 0
        self.intervalo = 16  # ~60 fps
        self.cancelado = False
        widget.after(atraso_ms, self._tique)

    def _tique(self):
        if self.cancelado or not self.widget.winfo_exists():
            return
        decorrido = self.quadro * self.intervalo
        t = min(1.0, decorrido / self.duracao)
        try:
            self.passo(suavizar(t))
        except tk.TclError:
            return  # widget destruído no meio da animação
        if t < 1.0:
            self.quadro += 1
            self.widget.after(self.intervalo, self._tique)


class AnelDia(tk.Canvas):
    """Anel de progresso do dia.

    Mostra a fração da fila já revisada hoje. O número no centro é o que
    falta, porque é isso que o estudante precisa decidir — não o total.
    """

    def __init__(self, parent, tamanho=132, **kw):
        super().__init__(parent, width=tamanho, height=tamanho,
                         bg=COR["superficie"], highlightthickness=0, **kw)
        self.tamanho = tamanho
        self.fracao_alvo = 0.0
        self.texto_centro = ""
        self.rotulo_centro = ""
        self.cor = COR["acento"]

    def definir(self, feitos: int, total: int, cor: str | None = None):
        self.cor = cor or COR["acento"]
        self.fracao_alvo = (feitos / total) if total else 1.0
        restante = max(0, total - feitos)
        self.texto_centro = str(restante) if total else "0"
        self.rotulo_centro = "a revisar" if restante else "em dia"
        Animacao(self, self._desenhar, duracao_ms=800, atraso_ms=80)

    def _desenhar(self, t: float):
        self.delete("all")
        m, s = 12, self.tamanho
        largura = 11

        self.create_oval(m, m, s - m, s - m, outline=COR["borda"], width=largura)

        extensao = 359.999 * self.fracao_alvo * t
        if extensao > 0.6:
            self.create_arc(m, m, s - m, s - m, start=90, extent=-extensao,
                            outline=self.cor, width=largura, style=tk.ARC)

        self.create_text(s / 2, s / 2 - 9, text=self.texto_centro,
                         font=("Segoe UI", 27, "bold"), fill=COR["tinta"])
        self.create_text(s / 2, s / 2 + 17, text=self.rotulo_centro,
                         font=FONTE["micro"], fill=COR["tinta2"])


class BarraEstagios(tk.Canvas):
    """Uma barra única dividida pelos quatro estágios de memória.

    Barra empilhada em vez de quatro barras separadas: o que importa é a
    proporção entre estágios, e proporção se lê melhor num todo dividido.
    """

    def __init__(self, parent, altura=22, **kw):
        super().__init__(parent, height=altura, bg=COR["superficie"],
                         highlightthickness=0, **kw)
        self.altura = altura
        self.contagem = {}
        self.bind("<Configure>", lambda _: self._redesenhar(1.0))

    def definir(self, contagem: dict[str, int]):
        self.contagem = contagem
        Animacao(self, self._redesenhar, duracao_ms=750, atraso_ms=180)

    def _redesenhar(self, t: float):
        self.delete("all")
        largura = self.winfo_width()
        if largura <= 1 or not self.contagem:
            return
        total = sum(self.contagem.values()) or 1
        x = 0.0
        for chave in ("consolidado", "firmando", "aprendendo", "novo"):
            n = self.contagem.get(chave, 0)
            if not n:
                continue
            w = (n / total) * largura * t
            if w < 0.5:
                continue
            self.create_rectangle(x, 0, x + w, self.altura,
                                  fill=COR_ESTAGIO[chave], outline="")
            if w > 26:
                self.create_text(x + w / 2, self.altura / 2, text=str(n),
                                 font=FONTE["micro"], fill=COR["branco"])
            x += w


class BarraDominio(tk.Canvas):
    """Barra fina de domínio, usada por categoria."""

    def __init__(self, parent, altura=8, cor=None, **kw):
        super().__init__(parent, height=altura, bg=COR["superficie"],
                         highlightthickness=0, **kw)
        self.altura = altura
        self.cor = cor or COR["acento"]
        self.valor = 0.0
        self.bind("<Configure>", lambda _: self._redesenhar(1.0))

    def definir(self, valor: float, atraso_ms=0):
        self.valor = max(0.0, min(1.0, valor))
        Animacao(self, self._redesenhar, duracao_ms=700, atraso_ms=atraso_ms)

    def _redesenhar(self, t: float):
        self.delete("all")
        largura = self.winfo_width()
        if largura <= 1:
            return
        r = self.altura / 2
        self.create_rectangle(0, 0, largura, self.altura,
                              fill=COR["borda"], outline="")
        w = largura * self.valor * t
        if w > 1:
            self.create_rectangle(0, 0, w, self.altura, fill=self.cor, outline="")


class ReguaCalibracao(tk.Canvas):
    """Duas marcas numa régua: o que você acha que sabe e o que acerta.

    A distância entre elas é a informação. Estudantes costumam
    superestimar o próprio preparo, e essa é justamente a lacuna que
    ninguém percebe sozinho.
    """

    def __init__(self, parent, altura=64, **kw):
        super().__init__(parent, height=altura, bg=COR["superficie"],
                         highlightthickness=0, **kw)
        self.altura = altura
        self.confianca = 0.0
        self.acerto = 0.0
        self.bind("<Configure>", lambda _: self._redesenhar(1.0))

    def definir(self, confianca: float, acerto: float):
        self.confianca, self.acerto = confianca, acerto
        Animacao(self, self._redesenhar, duracao_ms=800, atraso_ms=260)

    def _redesenhar(self, t: float):
        self.delete("all")
        largura = self.winfo_width()
        if largura <= 1:
            return
        m = 10
        util = largura - 2 * m
        y = self.altura / 2

        self.create_line(m, y, m + util, y, fill=COR["borda"], width=5)

        cx = m + util * self.confianca * t
        ax = m + util * self.acerto * t

        # faixa entre as duas marcas: a lacuna que se quer enxergar
        if abs(cx - ax) > 2:
            self.create_line(min(cx, ax), y, max(cx, ax), y,
                             fill=COR["ambar"], width=5)

        self.create_oval(ax - 7, y - 7, ax + 7, y + 7,
                         fill=COR["acento"], outline=COR["branco"], width=2)
        self.create_text(ax, y + 20, text="acerto", font=FONTE["micro"],
                         fill=COR["acento"])

        self.create_oval(cx - 7, y - 7, cx + 7, y + 7,
                         fill=COR["indigo"], outline=COR["branco"], width=2)
        self.create_text(cx, y - 20, text="confiança", font=FONTE["micro"],
                         fill=COR["indigo"])


class Constancia(tk.Canvas):
    """28 dias de atividade, um traço por dia.

    Sem número de "ofensiva" em destaque: sequência longa vira dívida, e
    quebrar depois de semanas desanima mais do que motiva. Aqui a leitura
    é do padrão, não de um placar a defender.
    """

    def __init__(self, parent, altura=42, **kw):
        super().__init__(parent, height=altura, bg=COR["superficie"],
                         highlightthickness=0, **kw)
        self.altura = altura
        self.dados = []
        self.bind("<Configure>", lambda _: self._redesenhar(1.0))

    def definir(self, dados: list[tuple[str, int]]):
        self.dados = dados
        Animacao(self, self._redesenhar, duracao_ms=700, atraso_ms=320)

    def _redesenhar(self, t: float):
        self.delete("all")
        largura = self.winfo_width()
        if largura <= 1 or not self.dados:
            return
        n = len(self.dados)
        passo = largura / n
        pico = max((v for _, v in self.dados), default=0) or 1
        base = self.altura - 12
        hoje = date.today().isoformat()

        for i, (dia, valor) in enumerate(self.dados):
            x = i * passo + passo / 2
            if valor:
                h = (base - 4) * min(1.0, valor / pico) * t
                cor = COR["acento"] if dia != hoje else COR["ambar"]
                self.create_line(x, base, x, base - h, fill=cor,
                                 width=max(2, passo * 0.5), capstyle=tk.ROUND)
            else:
                self.create_line(x, base, x, base - 2, fill=COR["borda"],
                                 width=max(2, passo * 0.5), capstyle=tk.ROUND)

        self.create_text(passo / 2, self.altura - 3, text="há 4 semanas",
                         font=FONTE["micro"], fill=COR["tinta3"], anchor="w")
        self.create_text(largura - 2, self.altura - 3, text="hoje",
                         font=FONTE["micro"], fill=COR["tinta3"], anchor="e")


def cartao(parent, padding=16):
    """Superfície branca com borda fina — a unidade visual da tela."""
    fora = tk.Frame(parent, bg=COR["borda"])
    dentro = tk.Frame(fora, bg=COR["superficie"])
    dentro.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
    miolo = tk.Frame(dentro, bg=COR["superficie"])
    miolo.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
    fora.miolo = miolo
    return fora


def titulo_secao(parent, texto, complemento=""):
    linha = tk.Frame(parent, bg=COR["superficie"])
    linha.pack(fill=tk.X, anchor=tk.W)
    tk.Label(linha, text=texto.upper(), font=FONTE["secao"],
             fg=COR["tinta2"], bg=COR["superficie"]).pack(side=tk.LEFT)
    if complemento:
        tk.Label(linha, text=complemento, font=FONTE["mini"],
                 fg=COR["tinta3"], bg=COR["superficie"]).pack(side=tk.RIGHT)
    return linha


class BotaoAcao(tk.Canvas):
    """Botão da ação principal, com resposta visual ao toque."""

    def __init__(self, parent, texto, comando, cor=None, largura=250, altura=46):
        super().__init__(parent, width=largura, height=altura,
                         bg=COR["superficie"], highlightthickness=0,
                         cursor="hand2")
        self.texto = texto
        self.comando = comando
        self.cor_base = cor or COR["acento"]
        self.cor_atual = self.cor_base
        self.larg, self.alt = largura, altura
        self._desenhar()
        self.bind("<Button-1>", self._pressionar)
        self.bind("<ButtonRelease-1>", self._soltar)
        self.bind("<Enter>", lambda _: self._pintar(COR["acento_alt"]))
        self.bind("<Leave>", lambda _: self._pintar(self.cor_base))

    def _desenhar(self, deslocamento=0):
        self.delete("all")
        r = 10
        x1, y1, x2, y2 = 1, 1 + deslocamento, self.larg - 1, self.alt - 3 + deslocamento
        self.create_polygon(
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
            smooth=True, fill=self.cor_atual, outline="")
        self.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=self.texto,
                         font=FONTE["forte"], fill=COR["branco"])

    def _pintar(self, cor):
        self.cor_atual = cor
        self._desenhar()

    def _pressionar(self, _):
        self._desenhar(deslocamento=2)

    def _soltar(self, _):
        self._desenhar()
        if callable(self.comando):
            self.comando()
