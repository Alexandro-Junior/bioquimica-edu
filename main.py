"""
BioquímicaEDU — Software Educacional Interativo
Universidade Cidade de São Paulo — PIBIC
Aluno: Alexandro de Araujo Junior
Orientador: Francisco de Assis Cavallaro

Interface inspirada no Duolingo (botões 3D arredondados, nós de lição
circulares, tema claro) com paleta baseada em reagentes e marcadores da
bioquímica clínica: verde-enzima (Fehling/clorofila), vermelho-heme,
âmbar-bile, violeta-fenolftaleína, azul-biureto/cobalto.
"""

import tkinter as tk
from tkinter import messagebox
import json
import csv
import random
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# ─────────────────────────────────────────────
# PALETA — cores baseadas em reagentes da bioquímica
# ─────────────────────────────────────────────
COR = {
    "fundo":           "#FAF6EE",   # papel de filtro / bancada
    "superficie":      "#FFFFFF",
    "topo":            "#FFFFFF",
    "trilha":          "#F1EBDC",   # trilha clara entre lições

    # Primária — verde enzima (Fehling reduzido, clorofila, bromocresol verde)
    "primaria":        "#16A34A",
    "primaria_dark":   "#15803D",
    "primaria_light":  "#DCFCE7",

    # Heme / hemoglobina — vermelho sangue
    "sangue":          "#E11D48",
    "sangue_dark":     "#9F1239",
    "sangue_light":    "#FFE4E6",

    # Bilirrubina — âmbar bile
    "bile":            "#F59E0B",
    "bile_dark":       "#B45309",
    "bile_light":      "#FEF3C7",

    # Fenolftaleína em meio básico — violeta
    "indicador":       "#7C3AED",
    "indicador_dark":  "#5B21B6",
    "indicador_light": "#EDE9FE",

    # Reação de Biureto / íon cobalto — azul
    "cobalto":         "#1E88B0",
    "cobalto_dark":    "#0E5C7A",
    "cobalto_light":   "#CFFAFE",

    "texto":           "#1F2937",
    "texto2":          "#6B7280",
    "texto3":          "#9CA3AF",

    "borda":           "#E5E7EB",
    "borda_forte":     "#D1D5DB",

    "sucesso":         "#16A34A",
    "sucesso_dark":    "#15803D",
    "sucesso_light":   "#DCFCE7",
    "erro":            "#DC2626",
    "erro_dark":       "#991B1B",
    "erro_light":      "#FEE2E2",

    "branco":          "#FFFFFF",

    "categoria": {
        "Hepático":   "#F59E0B",  # bilirrubina âmbar
        "Renal":      "#06B6D4",  # diurese ciano
        "Glicêmico":  "#16A34A",  # Fehling verde
        "Lipídico":   "#8B5CF6",  # quilomícron lilás
        "Eletrólito": "#3B82F6",  # solução eletrolítica
        "Cardíaco":   "#E11D48",  # heme cardíaco
    },
}

FONTE = {
    "titulo":   ("Segoe UI Black", 26),
    "subtit":   ("Segoe UI", 18, "bold"),
    "medio":    ("Segoe UI", 14, "bold"),
    "corpo":    ("Segoe UI", 12),
    "pequeno":  ("Segoe UI", 10),
    "botao":    ("Segoe UI", 13, "bold"),
    "botao_g":  ("Segoe UI", 15, "bold"),
    "mono":     ("Consolas", 11),
}


# ─────────────────────────────────────────────
# UTILITÁRIOS DE COR & DESENHO
# ─────────────────────────────────────────────
def _hex_to_rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def escurecer(cor, f=0.20):
    r, g, b = _hex_to_rgb(cor)
    return "#%02x%02x%02x" % (
        max(0, int(r * (1 - f))),
        max(0, int(g * (1 - f))),
        max(0, int(b * (1 - f))),
    )


def clarear(cor, f=0.15):
    r, g, b = _hex_to_rgb(cor)
    return "#%02x%02x%02x" % (
        min(255, int(r + (255 - r) * f)),
        min(255, int(g + (255 - g) * f)),
        min(255, int(b + (255 - b) * f)),
    )


def _pts_round_rect(x1, y1, x2, y2, r):
    return [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2,
        x1 + r, y2, x1, y2, x1, y2 - r,
        x1, y1 + r, x1, y1,
    ]


# ─────────────────────────────────────────────
# BOTÃO ESTILO DUOLINGO — Canvas 3D com sombra inferior
# ─────────────────────────────────────────────
class BotaoDuo(tk.Canvas):
    def __init__(self, parent, texto, comando=None, *,
                 cor=None, cor_texto="#FFFFFF",
                 fonte=None, padx=22, pady=10,
                 radius=14, sombra=4, largura_min=0,
                 bg_parent=None):
        cor = cor or COR["primaria"]
        cor_sombra = escurecer(cor, 0.25)
        fonte = fonte or FONTE["botao"]
        bg_parent = bg_parent or parent.cget("bg")

        tmp = tk.Label(parent, text=texto.upper(), font=fonte)
        w_txt = tmp.winfo_reqwidth()
        h_txt = tmp.winfo_reqheight()
        tmp.destroy()

        w = max(w_txt + padx * 2, largura_min)
        h = h_txt + pady * 2

        super().__init__(parent, width=w, height=h + sombra,
                         bg=bg_parent, highlightthickness=0, bd=0)

        self.cor = cor
        self.cor_sombra = cor_sombra
        self.cor_texto = cor_texto
        self.w, self.h = w, h
        self.sombra = sombra
        self.radius = radius
        self.fonte = fonte
        self.texto = texto.upper()
        self.comando = comando
        self.pressed = False
        self.hovered = False
        self.enabled = True

        self._desenhar()
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _desenhar(self):
        self.delete("all")
        off = self.sombra if self.pressed else 0

        self.create_polygon(
            _pts_round_rect(0, self.sombra, self.w, self.h + self.sombra, self.radius),
            smooth=True, fill=self.cor_sombra, outline=""
        )
        cor_top = clarear(self.cor, 0.10) if self.hovered and not self.pressed else self.cor
        self.create_polygon(
            _pts_round_rect(0, off, self.w, self.h + off, self.radius),
            smooth=True, fill=cor_top, outline=""
        )
        self.create_text(self.w // 2, self.h // 2 + off,
                         text=self.texto, fill=self.cor_texto, font=self.fonte)

    def _on_press(self, _):
        if not self.enabled:
            return
        self.pressed = True
        self._desenhar()

    def _on_release(self, _):
        if not self.enabled:
            return
        was = self.pressed
        self.pressed = False
        self._desenhar()
        if was and self.comando:
            self.comando()

    def _on_enter(self, _):
        if not self.enabled:
            return
        self.hovered = True
        self.config(cursor="hand2")
        self._desenhar()

    def _on_leave(self, _):
        self.hovered = False
        self.pressed = False
        self._desenhar()

    def desabilitar(self):
        self.enabled = False
        self.config(cursor="")


# ─────────────────────────────────────────────
# CÍRCULO ESTILO DUOLINGO — nó de lição
# ─────────────────────────────────────────────
class CirculoDuo(tk.Canvas):
    def __init__(self, parent, icone, comando=None, *,
                 cor=None, tamanho=120, sombra=7, bg_parent=None):
        cor = cor or COR["primaria"]
        cor_sombra = escurecer(cor, 0.25)
        bg_parent = bg_parent or parent.cget("bg")
        super().__init__(parent, width=tamanho, height=tamanho + sombra,
                         bg=bg_parent, highlightthickness=0, bd=0)
        self.cor = cor
        self.cor_sombra = cor_sombra
        self.icone = icone
        self.tamanho = tamanho
        self.sombra = sombra
        self.comando = comando
        self.pressed = False
        self.hovered = False
        self._desenhar()
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _desenhar(self):
        self.delete("all")
        off = self.sombra if self.pressed else 0
        self.create_oval(0, self.sombra, self.tamanho, self.tamanho + self.sombra,
                         fill=self.cor_sombra, outline="")
        cor_top = clarear(self.cor, 0.10) if self.hovered and not self.pressed else self.cor
        self.create_oval(0, off, self.tamanho, self.tamanho + off,
                         fill=cor_top, outline="")
        self.create_text(self.tamanho // 2, self.tamanho // 2 + off,
                         text=self.icone, fill=COR["branco"],
                         font=("Segoe UI Emoji", int(self.tamanho * 0.42), "bold"))

    def _on_press(self, _):
        self.pressed = True
        self._desenhar()

    def _on_release(self, _):
        was = self.pressed
        self.pressed = False
        self._desenhar()
        if was and self.comando:
            self.comando()

    def _on_enter(self, _):
        self.hovered = True
        self.config(cursor="hand2")
        self._desenhar()

    def _on_leave(self, _):
        self.hovered = False
        self.pressed = False
        self._desenhar()


# ─────────────────────────────────────────────
# CARD branco com barra colorida superior (estilo Duo)
# ─────────────────────────────────────────────
def card(parent, *, cor_topo=None, espessura_topo=4):
    container = tk.Frame(parent, bg=parent.cget("bg"))
    borda = tk.Frame(container, bg=COR["borda"])
    borda.pack(fill=tk.BOTH, expand=True)
    if cor_topo:
        tk.Frame(borda, bg=cor_topo, height=espessura_topo).pack(fill=tk.X, side=tk.TOP)
    miolo = tk.Frame(borda, bg=COR["superficie"])
    miolo.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 2))
    container.miolo = miolo
    return container


# ─────────────────────────────────────────────
# BARRA DE PROGRESSO arredondada
# ─────────────────────────────────────────────
class BarraProgresso(tk.Canvas):
    def __init__(self, parent, *, largura=400, altura=16,
                 cor=None, bg_parent=None):
        bg_parent = bg_parent or parent.cget("bg")
        super().__init__(parent, width=largura, height=altura,
                         bg=bg_parent, highlightthickness=0, bd=0)
        self.largura = largura
        self.altura = altura
        self.cor = cor or COR["primaria"]
        self.pct = 0.0
        self._desenhar()

    def set(self, pct):
        self.pct = max(0.0, min(1.0, pct))
        self._desenhar()

    def _desenhar(self):
        self.delete("all")
        r = self.altura // 2
        self.create_polygon(
            _pts_round_rect(0, 0, self.largura, self.altura, r),
            smooth=True, fill=COR["borda"], outline=""
        )
        if self.pct > 0:
            fill_w = max(int(self.largura * self.pct), self.altura)
            self.create_polygon(
                _pts_round_rect(0, 0, fill_w, self.altura, r),
                smooth=True, fill=self.cor, outline=""
            )
            # Reflexo (highlight branco superior, como no Duo)
            self.create_polygon(
                _pts_round_rect(4, 3, fill_w - 4, self.altura // 2, r // 2),
                smooth=True, fill=clarear(self.cor, 0.35), outline=""
            )


# ─────────────────────────────────────────────
# LABEL helpers
# ─────────────────────────────────────────────
def rotulo(parent, texto, *, fonte=None, cor=None, wrap=0, ancora=tk.W):
    return tk.Label(
        parent, text=texto,
        font=fonte or FONTE["corpo"],
        fg=cor or COR["texto"],
        bg=parent.cget("bg"),
        anchor=ancora, justify=tk.LEFT,
        wraplength=wrap,
    )


# ─────────────────────────────────────────────
# CARREGAMENTO DE DADOS
# ─────────────────────────────────────────────
def carregar_marcadores():
    marcadores = []
    try:
        with open(DATA_DIR / "marcadores.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                row["valor_ref_min"] = float(row["valor_ref_min"])
                row["valor_ref_max"] = float(row["valor_ref_max"])
                marcadores.append(row)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar marcadores: {e}")
    return marcadores


def carregar_casos():
    try:
        with open(DATA_DIR / "casos_clinicos.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar casos: {e}")
        return []


def carregar_quiz():
    try:
        with open(DATA_DIR / "quiz_perguntas.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar quiz: {e}")
        return []


def carregar_flashcards():
    try:
        with open(DATA_DIR / "flashcards.json", encoding="utf-8") as f:
            dados = json.load(f)
            return dados.get("flashcards", [])
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar flashcards: {e}")
        return []


def carregar_marcadores_extras():
    """Carrega vídeos e exemplos clínicos para cada marcador"""
    try:
        with open(DATA_DIR / "marcadores_extras.json", encoding="utf-8") as f:
            dados = json.load(f)
            # Converte em dicionário por sigla para acesso rápido
            extras = {}
            for m in dados.get("marcadores_extras", []):
                extras[m["sigla"]] = m
            return extras
    except Exception as e:
        print(f"Aviso: Extras não disponíveis: {e}")
        return {}


def carregar_marcadores_imagens():
    """Carrega os diagramas de cada marcador (aba Imagens)"""
    try:
        with open(DATA_DIR / "marcadores_imagens.json", encoding="utf-8") as f:
            dados = json.load(f)
            return {m["sigla"]: m for m in dados.get("marcadores_imagens", [])}
    except Exception as e:
        print(f"Aviso: Imagens não disponíveis: {e}")
        return {}


# ─────────────────────────────────────────────
# BARRA SUPERIOR comum (com indicadores XP/sequência)
# ─────────────────────────────────────────────
def barra_topo(parent, controller, *, titulo, voltar=True, cor_titulo=None):
    topo = tk.Frame(parent, bg=COR["topo"], height=60)
    topo.pack(fill=tk.X, side=tk.TOP)
    topo.pack_propagate(False)
    tk.Frame(parent, bg=COR["borda"], height=1).pack(fill=tk.X)

    if voltar:
        seta = tk.Label(topo, text="✕", font=("Segoe UI", 18, "bold"),
                        fg=COR["texto3"], bg=COR["topo"], cursor="hand2",
                        padx=18)
        seta.pack(side=tk.LEFT)
        seta.bind("<Button-1>", lambda _: controller.mostrar("inicio"))
        seta.bind("<Enter>", lambda _: seta.config(fg=COR["texto"]))
        seta.bind("<Leave>", lambda _: seta.config(fg=COR["texto3"]))

    tk.Label(topo, text=titulo,
             font=FONTE["medio"],
             fg=cor_titulo or COR["texto"],
             bg=COR["topo"]).pack(side=tk.LEFT, padx=4)

    # Indicadores de gamificação
    ind = tk.Frame(topo, bg=COR["topo"])
    ind.pack(side=tk.RIGHT, padx=20)
    tk.Label(ind, text=f"🔥 {controller.streak}",
             font=FONTE["botao"], fg=COR["bile_dark"],
             bg=COR["topo"]).pack(side=tk.LEFT, padx=8)
    tk.Label(ind, text=f"⚡ {controller.xp} XP",
             font=FONTE["botao"], fg=COR["indicador_dark"],
             bg=COR["topo"]).pack(side=tk.LEFT, padx=8)


# ─────────────────────────────────────────────
# MODO FLASHCARDS (Estudo Rápido)
# ─────────────────────────────────────────────
class TelaFlashcards(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=COR["fundo"])
        self.controller = controller
        self.flashcards = carregar_flashcards()
        self.indice = 0
        self.virado = False
        self._construir()

    def _construir(self):
        nav = tk.Frame(self, bg=COR["topo"], height=55)
        nav.pack(fill=tk.X)
        nav.pack_propagate(False)
        tk.Button(nav, text="← Menu", bg=COR["topo"], fg=COR["texto2"],
                  relief="flat", command=lambda: self.controller.mostrar("inicio"),
                  font=FONTE["pequeno"], padx=15, pady=15).pack(side=tk.LEFT)
        tk.Label(nav, text="🎴  Flashcards — Estudo Rápido", font=FONTE["medio"],
                 fg=COR["texto"], bg=COR["topo"]).pack(side=tk.LEFT, padx=10)

        area = tk.Frame(self, bg=COR["fundo"])
        area.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        prog = tk.Frame(area, bg=COR["fundo"], pady=10)
        prog.pack(fill=tk.X)
        tk.Label(prog, text=f"{self.indice + 1}/{len(self.flashcards)}",
                 font=FONTE["subtit"], fg=COR["texto"],
                 bg=COR["fundo"]).pack()

        barra_bg = tk.Frame(area, bg=COR["borda"], height=6)
        barra_bg.pack(fill=tk.X, pady=8)
        pct = (self.indice / len(self.flashcards)) if self.flashcards else 0
        barra_fill = tk.Frame(barra_bg, bg=COR["primaria"], height=6)
        barra_fill.place(relwidth=pct, relheight=1)

        card_container = tk.Frame(area, bg=COR["fundo"])
        card_container.pack(expand=True, fill=tk.BOTH, pady=20)

        self.card_canvas = tk.Canvas(card_container, bg=COR["fundo"],
                                      highlightthickness=0, height=300)
        self.card_canvas.pack(fill=tk.BOTH, expand=True)
        self.card_canvas.bind("<Button-1>", lambda _: self._virar_card())

        self._desenhar_card()

        botoes = tk.Frame(area, bg=COR["fundo"])
        botoes.pack(fill=tk.X, pady=10)

        tk.Button(botoes, text="← Anterior", bg=COR["trilha"],
                  fg=COR["texto"], relief="flat", font=FONTE["botao"],
                  command=self._anterior, padx=24, pady=10).pack(side=tk.LEFT, padx=10)

        tk.Label(botoes, text="Clique no card para virar", font=FONTE["pequeno"],
                 fg=COR["texto2"], bg=COR["fundo"]).pack(side=tk.LEFT, expand=True)

        tk.Button(botoes, text="Próximo →", bg=COR["primaria"],
                  fg=COR["branco"], relief="flat", font=FONTE["botao"],
                  command=self._proximo, padx=24, pady=10).pack(side=tk.RIGHT, padx=10)

    def _desenhar_card(self):
        self.card_canvas.delete("all")
        w = self.card_canvas.winfo_width()
        h = self.card_canvas.winfo_height()

        if w < 50 or h < 50:
            w, h = 600, 300

        self.card_canvas.create_polygon(
            _pts_round_rect(10, 10, w - 10, h - 10, 20),
            smooth=True, fill=escurecer(COR["primaria"], 0.3), outline=""
        )

        if self.virado:
            cor_fundo = COR["primaria_light"]
            cor_texto = COR["texto"]
        else:
            cor_fundo = COR["primaria"]
            cor_texto = COR["branco"]

        self.card_canvas.create_polygon(
            _pts_round_rect(5, 5, w - 5, h - 5, 20),
            smooth=True, fill=cor_fundo, outline=COR["borda_forte"], width=2
        )

        if self.flashcards:
            card = self.flashcards[self.indice]
            if not self.virado:
                texto = f"❓\n\n{card['pergunta']}"
            else:
                texto = f"✅\n\n{card['resposta']}"

            self.card_canvas.create_text(
                w // 2, h // 2,
                text=texto,
                font=FONTE["subtit"],
                fill=cor_texto,
                width=int(w * 0.8)
            )

            if not self.virado:
                self.card_canvas.create_text(
                    w // 2, h - 30,
                    text="Clique para revelar resposta",
                    font=FONTE["pequeno"],
                    fill=clarear(COR["primaria"], 0.6)
                )

    def _virar_card(self):
        self.virado = not self.virado
        self._desenhar_card()

    def _anterior(self):
        if self.indice > 0:
            self.indice -= 1
            self.virado = False
            self._atualizar()

    def _proximo(self):
        if self.indice < len(self.flashcards) - 1:
            self.indice += 1
            self.virado = False
            self._atualizar()
        else:
            messagebox.showinfo("Flashcards", "Você chegou ao fim! Parabéns! 🎉")
            self.controller.mostrar("inicio")

    def _atualizar(self):
        self._desenhar_card()


# ─────────────────────────────────────────────
# TELA INICIAL — caminho de "lições" estilo Duolingo
# ─────────────────────────────────────────────
class TelaInicial(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=COR["fundo"])
        self.controller = controller
        self._construir()

    def _construir(self):
        # Cabeçalho
        topo = tk.Frame(self, bg=COR["topo"], height=80)
        topo.pack(fill=tk.X)
        topo.pack_propagate(False)
        tk.Frame(self, bg=COR["borda"], height=1).pack(fill=tk.X)

        marca = tk.Frame(topo, bg=COR["topo"])
        marca.pack(side=tk.LEFT, padx=22, pady=10)
        tk.Label(marca, text="⚗", font=("Segoe UI Emoji", 30),
                 fg=COR["primaria"], bg=COR["topo"]).pack(side=tk.LEFT)
        bloco = tk.Frame(marca, bg=COR["topo"])
        bloco.pack(side=tk.LEFT, padx=8)
        tk.Label(bloco, text="BioquímicaEDU",
                 font=("Segoe UI Black", 20),
                 fg=COR["texto"], bg=COR["topo"]).pack(anchor=tk.W)
        tk.Label(bloco, text="Aprenda bioquímica clínica em jornada",
                 font=FONTE["pequeno"], fg=COR["texto2"],
                 bg=COR["topo"]).pack(anchor=tk.W)

        ind = tk.Frame(topo, bg=COR["topo"])
        ind.pack(side=tk.RIGHT, padx=22)
        self._chip(ind, "🔥", str(self.controller.streak), COR["bile_dark"])
        self._chip(ind, "⚡", f"{self.controller.xp} XP", COR["indicador_dark"])

        # Faixa de unidade (estilo "Unit 1")
        faixa = tk.Frame(self, bg=COR["primaria"], height=70)
        faixa.pack(fill=tk.X)
        faixa.pack_propagate(False)
        wrap = tk.Frame(faixa, bg=COR["primaria"])
        wrap.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        tk.Label(wrap, text="UNIDADE 1",
                 font=FONTE["pequeno"], fg=clarear(COR["primaria"], 0.6),
                 bg=COR["primaria"]).pack()
        tk.Label(wrap, text="Marcadores bioquímicos clínicos",
                 font=("Segoe UI Black", 16), fg=COR["branco"],
                 bg=COR["primaria"]).pack()

        # Caminho de lições (zigue-zague)
        caminho = tk.Frame(self, bg=COR["fundo"])
        caminho.pack(expand=True, fill=tk.BOTH)

        canvas = tk.Canvas(caminho, bg=COR["fundo"], highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        # Posições em zigue-zague (relativas)
        nos = [
            ("📚", "Modo Estudo",
             "Explore 20 marcadores e suas\ninterpretações clínicas",
             COR["primaria"], "estudo", 0),
            ("🎴", "Flashcards",
             "Estude rápido com 50 cards\nque viram ao clicar",
             COR["bile"], "flashcards", 1),
            ("🧠", "Quiz Rápido",
             "Teste seus conhecimentos\ncom perguntas embaralhadas",
             COR["cobalto"], "quiz", -1),
            ("🩺", "Casos Clínicos",
             "Analise exames e chegue\nao diagnóstico correto",
             COR["indicador"], "diagnostico", 1),
        ]
        canvas.bind("<Configure>",
                    lambda e: self._desenhar_caminho(e, canvas, nos))

        # Rodapé
        rodape = tk.Frame(self, bg=COR["topo"], height=42)
        rodape.pack(fill=tk.X, side=tk.BOTTOM)
        rodape.pack_propagate(False)
        tk.Frame(self, bg=COR["borda"], height=1).pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(rodape,
                 text="Universidade Cidade de São Paulo — UNICID · PIBIC/CNPq",
                 font=FONTE["pequeno"], fg=COR["texto2"],
                 bg=COR["topo"]).pack(pady=12)

    def _chip(self, parent, icone, valor, cor):
        chip = tk.Frame(parent, bg=COR["trilha"])
        chip.pack(side=tk.LEFT, padx=6)
        tk.Label(chip, text=icone, font=("Segoe UI Emoji", 14),
                 bg=COR["trilha"]).pack(side=tk.LEFT, padx=(10, 4), pady=6)
        tk.Label(chip, text=valor, font=FONTE["botao"],
                 fg=cor, bg=COR["trilha"]).pack(side=tk.LEFT, padx=(0, 12))

    def _desenhar_caminho(self, _evt, canvas, nos):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 50 or h < 50:
            return

        cx = w // 2
        passo_y = max(160, h // (len(nos) + 1))
        offset = 90

        # Conectores pontilhados
        for i in range(len(nos) - 1):
            x1 = cx + nos[i][5] * offset
            y1 = passo_y * (i + 1)
            x2 = cx + nos[i + 1][5] * offset
            y2 = passo_y * (i + 2)
            n = 14
            for k in range(1, n):
                t = k / n
                # curva quadrática suave
                mx = (x1 + x2) // 2
                my = (y1 + y2) // 2
                px = int((1 - t) * (1 - t) * x1 + 2 * (1 - t) * t * mx + t * t * x2)
                py = int((1 - t) * (1 - t) * y1 + 2 * (1 - t) * t * my + t * t * y2)
                r = 4
                canvas.create_oval(px - r, py - r, px + r, py + r,
                                    fill=COR["borda_forte"], outline="")

        # Nós (círculos + label)
        for i, (icone, titulo, desc, cor, alvo, off_dir) in enumerate(nos):
            x = cx + off_dir * offset
            y = passo_y * (i + 1)
            self._criar_no(canvas, x, y, icone, titulo, desc, cor, alvo)

    def _criar_no(self, canvas, x, y, icone, titulo, desc, cor, alvo):
        tamanho = 110
        circ = CirculoDuo(canvas, icone,
                          comando=lambda: self.controller.mostrar(alvo),
                          cor=cor, tamanho=tamanho, bg_parent=COR["fundo"])
        canvas.create_window(x, y, window=circ)

        # Cartão flutuante com título e botão "iniciar"
        cartao = tk.Frame(canvas, bg=COR["superficie"],
                          highlightbackground=COR["borda"],
                          highlightthickness=1)
        tk.Label(cartao, text=titulo,
                 font=("Segoe UI Black", 13),
                 fg=COR["texto"], bg=COR["superficie"]).pack(padx=14, pady=(10, 2))
        tk.Label(cartao, text=desc,
                 font=FONTE["pequeno"], fg=COR["texto2"],
                 bg=COR["superficie"], justify=tk.CENTER).pack(padx=14)
        BotaoDuo(cartao, "Iniciar +10 XP",
                 comando=lambda: self.controller.mostrar(alvo),
                 cor=cor, padx=14, pady=7,
                 fonte=FONTE["pequeno"],
                 bg_parent=COR["superficie"]).pack(pady=10, padx=14)

        canvas.create_window(x, y + 130, window=cartao)


# ─────────────────────────────────────────────
# MODO ESTUDO
# ─────────────────────────────────────────────
class TelaEstudo(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=COR["fundo"])
        self.controller = controller
        self.marcadores = carregar_marcadores()
        self.categorias = sorted({m["categoria"] for m in self.marcadores})
        self.cat_selecionada = tk.StringVar(value="Todas")
        self.busca_var = tk.StringVar()
        self.busca_var.trace("w", lambda *_: self._filtrar())
        self.extras = carregar_marcadores_extras()   # Vídeos + exemplos
        self.imagens = carregar_marcadores_imagens()  # Diagramas
        self._refs_imagens = []  # evita coleta das PhotoImage pelo GC
        self._construir()

    def _construir(self):
        barra_topo(self, self.controller,
                   titulo="📚  Modo Estudo · Marcadores")

        # Filtros (chips de categoria + busca)
        filtros = tk.Frame(self, bg=COR["fundo"], pady=14)
        filtros.pack(fill=tk.X, padx=24)

        wrap_busca = tk.Frame(filtros, bg=COR["trilha"])
        wrap_busca.pack(side=tk.LEFT, padx=(0, 18))
        tk.Label(wrap_busca, text="🔍", font=("Segoe UI Emoji", 12),
                 bg=COR["trilha"]).pack(side=tk.LEFT, padx=(10, 4), pady=6)
        entry = tk.Entry(wrap_busca, textvariable=self.busca_var,
                         font=FONTE["corpo"], bg=COR["trilha"],
                         fg=COR["texto"], insertbackground=COR["texto"],
                         relief="flat", bd=0, width=20)
        entry.pack(side=tk.LEFT, padx=(0, 12), pady=6)

        for cat in ["Todas"] + self.categorias:
            cor = COR["categoria"].get(cat, COR["texto2"])
            self._chip_categoria(filtros, cat, cor)

        # Área dividida
        area = tk.Frame(self, bg=COR["fundo"])
        area.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 16))

        # Esquerda — lista
        esq = tk.Frame(area, bg=COR["superficie"],
                       highlightbackground=COR["borda"], highlightthickness=1,
                       width=270)
        esq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))
        esq.pack_propagate(False)
        tk.Label(esq, text="MARCADORES",
                 font=("Segoe UI", 10, "bold"),
                 fg=COR["texto3"], bg=COR["superficie"]).pack(anchor=tk.W,
                                                              padx=14, pady=(14, 6))

        wrap = tk.Frame(esq, bg=COR["superficie"])
        wrap.pack(fill=tk.BOTH, expand=True)
        self.canvas_lista = tk.Canvas(wrap, bg=COR["superficie"], highlightthickness=0)
        sb = tk.Scrollbar(wrap, orient="vertical", command=self.canvas_lista.yview)
        self.lista_interior = tk.Frame(self.canvas_lista, bg=COR["superficie"])
        self.lista_interior.bind(
            "<Configure>",
            lambda _: self.canvas_lista.configure(
                scrollregion=self.canvas_lista.bbox("all"))
        )
        self.canvas_lista.create_window((0, 0), window=self.lista_interior, anchor="nw")
        self.canvas_lista.configure(yscrollcommand=sb.set)
        self.canvas_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Direita — detalhe
        self.dir = tk.Frame(area, bg=COR["fundo"])
        self.dir.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._placeholder()
        self._filtrar()

    def _chip_categoria(self, parent, cat, cor):
        var = self.cat_selecionada
        wrap = tk.Frame(parent, bg=COR["fundo"])
        wrap.pack(side=tk.LEFT, padx=4)

        def atualizar(_=None):
            ativo = (var.get() == cat)
            chip.config(bg=cor if ativo else COR["trilha"])
            lbl.config(bg=cor if ativo else COR["trilha"],
                       fg=COR["branco"] if ativo else cor)

        chip = tk.Frame(wrap, bg=COR["trilha"], cursor="hand2")
        chip.pack()
        lbl = tk.Label(chip, text=cat, font=FONTE["pequeno"],
                       fg=cor, bg=COR["trilha"], padx=12, pady=6)
        lbl.pack()
        chip.bind("<Button-1>", lambda _: (var.set(cat), self._filtrar(), atualizar()))
        lbl.bind("<Button-1>", lambda _: (var.set(cat), self._filtrar(), atualizar()))
        var.trace("w", lambda *_: atualizar())
        atualizar()

    def _filtrar(self):
        busca = self.busca_var.get().lower()
        cat = self.cat_selecionada.get()
        filtrados = [
            m for m in self.marcadores
            if (cat == "Todas" or m["categoria"] == cat)
            and (busca in m["nome"].lower() or busca in m["sigla"].lower())
        ]
        self._popular(filtrados)

    def _popular(self, marcadores):
        for w in self.lista_interior.winfo_children():
            w.destroy()
        for m in marcadores:
            self._item_lista(m)

    def _item_lista(self, m):
        cor = COR["categoria"].get(m["categoria"], COR["primaria"])
        item = tk.Frame(self.lista_interior, bg=COR["superficie"], cursor="hand2")
        item.pack(fill=tk.X, padx=8, pady=3)

        # Bolinha colorida (categoria)
        bolinha_canvas = tk.Canvas(item, width=14, height=14,
                                    bg=COR["superficie"], highlightthickness=0)
        bolinha_canvas.create_oval(1, 1, 13, 13, fill=cor, outline="")
        bolinha_canvas.pack(side=tk.LEFT, padx=(8, 10))

        info = tk.Frame(item, bg=COR["superficie"])
        info.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)
        tk.Label(info, text=m["nome"], font=("Segoe UI", 11, "bold"),
                 fg=COR["texto"], bg=COR["superficie"],
                 anchor=tk.W).pack(fill=tk.X)
        tk.Label(info, text=f"{m['sigla']}  ·  {m['categoria']}",
                 font=FONTE["pequeno"], fg=COR["texto2"],
                 bg=COR["superficie"], anchor=tk.W).pack(fill=tk.X)

        def hover(_): item.config(bg=COR["trilha"]); info.config(bg=COR["trilha"]); \
            bolinha_canvas.config(bg=COR["trilha"]); \
            [c.config(bg=COR["trilha"]) for c in info.winfo_children()]
        def unhover(_): item.config(bg=COR["superficie"]); info.config(bg=COR["superficie"]); \
            bolinha_canvas.config(bg=COR["superficie"]); \
            [c.config(bg=COR["superficie"]) for c in info.winfo_children()]
        for w in [item, info, bolinha_canvas] + list(info.winfo_children()):
            w.bind("<Button-1>", lambda _e, marc=m: self._detalhe(marc))
            w.bind("<Enter>", hover)
            w.bind("<Leave>", unhover)

    def _placeholder(self):
        for w in self.dir.winfo_children():
            w.destroy()
        wrap = tk.Frame(self.dir, bg=COR["fundo"])
        wrap.pack(expand=True)
        tk.Label(wrap, text="🧪", font=("Segoe UI Emoji", 56),
                 fg=COR["borda_forte"], bg=COR["fundo"]).pack(pady=(10, 6))
        tk.Label(wrap, text="Selecione um marcador",
                 font=FONTE["medio"], fg=COR["texto2"],
                 bg=COR["fundo"]).pack()
        tk.Label(wrap, text="Veja valores de referência, interpretação clínica\n"
                            "e doenças associadas",
                 font=FONTE["pequeno"], fg=COR["texto3"],
                 bg=COR["fundo"], justify=tk.CENTER).pack(pady=8)

    def _detalhe(self, m):
        for w in self.dir.winfo_children():
            w.destroy()
        cor_cat = COR["categoria"].get(m["categoria"], COR["primaria"])

        # Container com abas
        self.aba_atual = tk.StringVar(value="info")

        # Barra de abas
        abas_frame = tk.Frame(self.dir, bg=COR["trilha"], height=45)
        abas_frame.pack(fill=tk.X)
        abas_frame.pack_propagate(False)

        extras_m = self.extras.get(m["sigla"], {})
        disponivel = {
            "info": True,
            "fontes": bool(extras_m.get("referencias")),
            "videos": bool(extras_m.get("videos")),
            "exemplos": bool(extras_m.get("exemplos")),
            "imagens": bool(self.imagens.get(m["sigla"], {}).get("imagens")),
        }

        for aba, icone, label in [("info", "ℹ️", "Info"),
                                   ("fontes", "📚", "Fontes"),
                                   ("videos", "🎥", "Vídeos"),
                                   ("exemplos", "📋", "Exemplos"),
                                   ("imagens", "📊", "Imagens")]:
            if disponivel[aba]:
                def sel_aba(a=aba):
                    self.aba_atual.set(a)
                    self._atualizar_detalhe(m)

                btn = tk.Button(abas_frame, text=f"{icone} {label}",
                               bg=COR["trilha"], fg=COR["texto"],
                               relief="flat", font=FONTE["pequeno"],
                               command=sel_aba, padx=16, pady=8)
                btn.pack(side=tk.LEFT, padx=4)

                # Highlight da aba ativa
                def refresh_btn(btn_=btn, a=aba):
                    if self.aba_atual.get() == a:
                        btn_.config(bg=COR["primaria"], fg=COR["branco"])
                    else:
                        btn_.config(bg=COR["trilha"], fg=COR["texto"])
                self.aba_atual.trace("w", lambda *_: refresh_btn())
                refresh_btn()

        canvas = tk.Canvas(self.dir, bg=COR["fundo"], highlightthickness=0)
        sb = tk.Scrollbar(self.dir, orient="vertical", command=canvas.yview)
        interior = tk.Frame(canvas, bg=COR["fundo"])
        interior.bind("<Configure>",
                      lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=interior, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.detalhe_interior = interior
        self.detalhe_canvas = canvas
        self._atualizar_detalhe(m)

    def _atualizar_detalhe(self, m):
        """Atualiza conteúdo da aba selecionada"""
        for w in self.detalhe_interior.winfo_children():
            w.destroy()

        cor_cat = COR["categoria"].get(m["categoria"], COR["primaria"])
        aba = self.aba_atual.get()

        if aba == "info":
            self._detalhe_info(m, cor_cat)
        elif aba == "videos":
            self._detalhe_videos(m, cor_cat)
        elif aba == "exemplos":
            self._detalhe_exemplos(m, cor_cat)
        elif aba == "imagens":
            self._detalhe_imagens(m, cor_cat)
        elif aba == "fontes":
            self._detalhe_fontes(m, cor_cat)

    def _detalhe_info(self, m, cor_cat):
        """Aba Info - valores e interpretações"""
        interior = self.detalhe_interior

        # Cabeçalho colorido com selo da categoria
        cab = tk.Frame(interior, bg=cor_cat, pady=18)
        cab.pack(fill=tk.X)
        bloco = tk.Frame(cab, bg=cor_cat)
        bloco.pack(padx=22, anchor=tk.W)
        tk.Label(bloco, text=m["categoria"].upper(),
                 font=("Segoe UI", 9, "bold"),
                 fg=clarear(cor_cat, 0.5), bg=cor_cat).pack(anchor=tk.W)
        tk.Label(bloco, text=m["nome"],
                 font=("Segoe UI Black", 20),
                 fg=COR["branco"], bg=cor_cat).pack(anchor=tk.W)
        tk.Label(bloco, text=f"Sigla {m['sigla']}",
                 font=FONTE["pequeno"], fg=clarear(cor_cat, 0.6),
                 bg=cor_cat).pack(anchor=tk.W, pady=(2, 0))

        # Referência
        c_ref = card(interior, cor_topo=cor_cat)
        c_ref.pack(fill=tk.X, padx=18, pady=12)
        tk.Label(c_ref.miolo, text="VALOR DE REFERÊNCIA",
                 font=("Segoe UI", 9, "bold"),
                 fg=COR["texto3"], bg=COR["superficie"]).pack(anchor=tk.W,
                                                              padx=18, pady=(14, 2))
        tk.Label(c_ref.miolo,
                 text=f"{m['valor_ref_min']} – {m['valor_ref_max']} {m['unidade']}",
                 font=("Segoe UI Black", 22),
                 fg=cor_cat, bg=COR["superficie"]).pack(anchor=tk.W, padx=18)
        self._barra_referencia(c_ref.miolo, m, cor_cat)

        # Interpretações
        for titulo, texto, cor, icone in [
            ("QUANDO ELEVADO", m["interpretacao_alta"], COR["erro"], "⬆"),
            ("QUANDO BAIXO", m["interpretacao_baixa"], COR["cobalto"], "⬇"),
        ]:
            c = card(interior, cor_topo=cor)
            c.pack(fill=tk.X, padx=18, pady=6)
            cab2 = tk.Frame(c.miolo, bg=COR["superficie"])
            cab2.pack(anchor=tk.W, padx=18, pady=(12, 4))
            tk.Label(cab2, text=icone, font=("Segoe UI Emoji", 14),
                     fg=cor, bg=COR["superficie"]).pack(side=tk.LEFT, padx=(0, 6))
            tk.Label(cab2, text=titulo, font=("Segoe UI", 10, "bold"),
                     fg=cor, bg=COR["superficie"]).pack(side=tk.LEFT)
            tk.Label(c.miolo, text=texto, font=FONTE["corpo"],
                     fg=COR["texto"], bg=COR["superficie"],
                     wraplength=520, justify=tk.LEFT).pack(anchor=tk.W,
                                                            padx=18, pady=(0, 14))

        # Doenças associadas
        for titulo, texto, cor in [
            ("Doenças associadas — valor ALTO",
             m["doencas_associadas_alta"], COR["erro"]),
            ("Doenças associadas — valor BAIXO",
             m["doencas_associadas_baixa"], COR["cobalto"]),
        ]:
            if texto and texto != "—":
                c = card(interior, cor_topo=cor)
                c.pack(fill=tk.X, padx=18, pady=6)
                tk.Label(c.miolo, text=titulo,
                         font=("Segoe UI", 10, "bold"),
                         fg=COR["texto2"], bg=COR["superficie"]).pack(
                    anchor=tk.W, padx=18, pady=(12, 6))
                for doenca in texto.split(","):
                    d = doenca.strip()
                    if d and d != "—":
                        linha = tk.Frame(c.miolo, bg=COR["superficie"])
                        linha.pack(fill=tk.X, padx=18, pady=2)
                        tag = tk.Frame(linha, bg=clarear(cor, 0.85))
                        tag.pack(side=tk.LEFT)
                        tk.Label(tag, text=d, font=FONTE["pequeno"],
                                 fg=cor, bg=clarear(cor, 0.85),
                                 padx=10, pady=4).pack()

    def _detalhe_videos(self, m, cor_cat):
        """Aba Vídeos - links do YouTube"""
        interior = self.detalhe_interior

        if m["sigla"] not in self.extras:
            tk.Label(interior, text="Sem vídeos disponíveis para este marcador",
                    font=FONTE["corpo"], fg=COR["texto2"],
                    bg=COR["fundo"]).pack(pady=20)
            return

        extras = self.extras[m["sigla"]]
        videos = extras.get("videos", [])

        if not videos:
            tk.Label(interior, text="Sem vídeos disponíveis",
                    font=FONTE["corpo"], fg=COR["texto2"],
                    bg=COR["fundo"]).pack(pady=20)
            return

        tk.Label(interior, text=f"🎥 {len(videos)} vídeos disponíveis",
                font=FONTE["subtit"], fg=COR["texto"],
                bg=COR["fundo"]).pack(pady=(12, 8), padx=18, anchor=tk.W)

        for vid in videos:
            c = card(interior, cor_topo=cor_cat)
            c.pack(fill=tk.X, padx=18, pady=8)

            cab = tk.Frame(c.miolo, bg=COR["superficie"])
            cab.pack(fill=tk.X, padx=18, pady=(10, 4))
            tk.Label(cab, text=vid["titulo"],
                    font=FONTE["medio"], fg=COR["texto"],
                    bg=COR["superficie"]).pack(anchor=tk.W)
            tk.Label(cab, text=f"⏱ {vid.get('duracao', '?')}",
                    font=FONTE["pequeno"], fg=COR["texto2"],
                    bg=COR["superficie"]).pack(anchor=tk.W)

            # Botão para abrir vídeo
            def abrir_video(url=vid["url"]):
                import webbrowser
                webbrowser.open(url.replace("/embed/", "/watch?v="))

            tk.Button(c.miolo, text="▶ Assistir no YouTube",
                     bg=COR["sangue"], fg=COR["branco"],
                     relief="flat", font=FONTE["botao"],
                     command=abrir_video, padx=16, pady=8).pack(pady=10)

    def _detalhe_exemplos(self, m, cor_cat):
        """Aba Exemplos - casos clínicos"""
        interior = self.detalhe_interior

        if m["sigla"] not in self.extras:
            tk.Label(interior, text="Sem exemplos disponíveis para este marcador",
                    font=FONTE["corpo"], fg=COR["texto2"],
                    bg=COR["fundo"]).pack(pady=20)
            return

        extras = self.extras[m["sigla"]]
        exemplos = extras.get("exemplos", [])

        if not exemplos:
            tk.Label(interior, text="Sem exemplos disponíveis",
                    font=FONTE["corpo"], fg=COR["texto2"],
                    bg=COR["fundo"]).pack(pady=20)
            return

        tk.Label(interior, text=f"📋 {len(exemplos)} casos clínicos",
                font=FONTE["subtit"], fg=COR["texto"],
                bg=COR["fundo"]).pack(pady=(12, 8), padx=18, anchor=tk.W)

        for i, ex in enumerate(exemplos, 1):
            c = card(interior, cor_topo=cor_cat)
            c.pack(fill=tk.X, padx=18, pady=8)

            # Título do caso
            tk.Label(c.miolo, text=f"Caso {i}: {ex['titulo']}",
                    font=FONTE["medio"], fg=COR["texto"],
                    bg=COR["superficie"]).pack(anchor=tk.W, padx=18, pady=(10, 4))

            # Descrição
            tk.Label(c.miolo, text=ex['descricao'],
                    font=FONTE["corpo"], fg=COR["texto"],
                    bg=COR["superficie"], wraplength=480,
                    justify=tk.LEFT).pack(anchor=tk.W, padx=18, pady=(0, 8))

            # Valores em destaque
            valores_frame = tk.Frame(c.miolo, bg=clarear(cor_cat, 0.85))
            valores_frame.pack(fill=tk.X, padx=18, pady=8)
            tk.Label(valores_frame, text=ex['valores'],
                    font=("Consolas", 9, "bold"), fg=cor_cat,
                    bg=clarear(cor_cat, 0.85)).pack(padx=10, pady=6)

            # Conduta
            tk.Label(c.miolo, text="💊 Conduta:",
                    font=("Segoe UI", 9, "bold"), fg=COR["texto2"],
                    bg=COR["superficie"]).pack(anchor=tk.W, padx=18, pady=(4, 2))
            tk.Label(c.miolo, text=ex['conducao'],
                    font=FONTE["corpo"], fg=COR["texto"],
                    bg=COR["superficie"], wraplength=480,
                    justify=tk.LEFT).pack(anchor=tk.W, padx=18, pady=(0, 10))

        # Cabeçalho colorido com selo da categoria
        cab = tk.Frame(interior, bg=cor_cat, pady=18)
        cab.pack(fill=tk.X)
        bloco = tk.Frame(cab, bg=cor_cat)
        bloco.pack(padx=22, anchor=tk.W)
        tk.Label(bloco, text=m["categoria"].upper(),
                 font=("Segoe UI", 9, "bold"),
                 fg=clarear(cor_cat, 0.5), bg=cor_cat).pack(anchor=tk.W)
        tk.Label(bloco, text=m["nome"],
                 font=("Segoe UI Black", 20),
                 fg=COR["branco"], bg=cor_cat).pack(anchor=tk.W)
        tk.Label(bloco, text=f"Sigla {m['sigla']}",
                 font=FONTE["pequeno"], fg=clarear(cor_cat, 0.6),
                 bg=cor_cat).pack(anchor=tk.W, pady=(2, 0))

        # Referência
        c_ref = card(interior, cor_topo=cor_cat)
        c_ref.pack(fill=tk.X, padx=18, pady=12)
        tk.Label(c_ref.miolo, text="VALOR DE REFERÊNCIA",
                 font=("Segoe UI", 9, "bold"),
                 fg=COR["texto3"], bg=COR["superficie"]).pack(anchor=tk.W,
                                                              padx=18, pady=(14, 2))
        tk.Label(c_ref.miolo,
                 text=f"{m['valor_ref_min']} – {m['valor_ref_max']} {m['unidade']}",
                 font=("Segoe UI Black", 22),
                 fg=cor_cat, bg=COR["superficie"]).pack(anchor=tk.W, padx=18)
        self._barra_referencia(c_ref.miolo, m, cor_cat)

        # Interpretações
        for titulo, texto, cor, icone in [
            ("QUANDO ELEVADO", m["interpretacao_alta"], COR["erro"], "⬆"),
            ("QUANDO BAIXO", m["interpretacao_baixa"], COR["cobalto"], "⬇"),
        ]:
            c = card(interior, cor_topo=cor)
            c.pack(fill=tk.X, padx=18, pady=6)
            cab2 = tk.Frame(c.miolo, bg=COR["superficie"])
            cab2.pack(anchor=tk.W, padx=18, pady=(12, 4))
            tk.Label(cab2, text=icone, font=("Segoe UI Emoji", 14),
                     fg=cor, bg=COR["superficie"]).pack(side=tk.LEFT, padx=(0, 6))
            tk.Label(cab2, text=titulo, font=("Segoe UI", 10, "bold"),
                     fg=cor, bg=COR["superficie"]).pack(side=tk.LEFT)
            tk.Label(c.miolo, text=texto, font=FONTE["corpo"],
                     fg=COR["texto"], bg=COR["superficie"],
                     wraplength=520, justify=tk.LEFT).pack(anchor=tk.W,
                                                            padx=18, pady=(0, 14))

        # Doenças associadas
        for titulo, texto, cor in [
            ("Doenças associadas — valor ALTO",
             m["doencas_associadas_alta"], COR["erro"]),
            ("Doenças associadas — valor BAIXO",
             m["doencas_associadas_baixa"], COR["cobalto"]),
        ]:
            if texto and texto != "—":
                c = card(interior, cor_topo=cor)
                c.pack(fill=tk.X, padx=18, pady=6)
                tk.Label(c.miolo, text=titulo,
                         font=("Segoe UI", 10, "bold"),
                         fg=COR["texto2"], bg=COR["superficie"]).pack(
                    anchor=tk.W, padx=18, pady=(12, 6))
                for doenca in texto.split(","):
                    d = doenca.strip()
                    if d and d != "—":
                        linha = tk.Frame(c.miolo, bg=COR["superficie"])
                        linha.pack(fill=tk.X, padx=18, pady=2)
                        tag = tk.Frame(linha, bg=clarear(cor, 0.85))
                        tag.pack(side=tk.LEFT)
                        tk.Label(tag, text=d, font=FONTE["pequeno"],
                                 fg=cor, bg=clarear(cor, 0.85),
                                 padx=10, pady=4).pack()
                tk.Frame(c.miolo, bg=COR["superficie"], height=10).pack()

    def _detalhe_fontes(self, m, cor_cat):
        """Aba Fontes - bibliografia academica verificada"""
        import webbrowser
        interior = self.detalhe_interior
        referencias = self.extras.get(m["sigla"], {}).get("referencias", [])

        if not referencias:
            tk.Label(interior, text="Sem referencias cadastradas para este marcador",
                     font=FONTE["corpo"], fg=COR["texto2"],
                     bg=COR["fundo"]).pack(pady=20)
            return

        tk.Label(interior, text=f"📚 {len(referencias)} referencias revisadas por pares",
                 font=FONTE["subtit"], fg=COR["texto"],
                 bg=COR["fundo"]).pack(pady=(12, 8), padx=18, anchor=tk.W)

        for ref in referencias:
            c = card(interior, cor_topo=cor_cat)
            c.pack(fill=tk.X, padx=18, pady=8)

            tk.Label(c.miolo, text=ref["titulo"],
                     font=FONTE["medio"], fg=COR["texto"],
                     bg=COR["superficie"], wraplength=480, justify=tk.LEFT
                     ).pack(anchor=tk.W, padx=18, pady=(10, 2))

            tk.Label(c.miolo, text=ref["fonte"],
                     font=FONTE["pequeno"], fg=COR["texto2"],
                     bg=COR["superficie"]).pack(anchor=tk.W, padx=18)

            if ref.get("nota"):
                tk.Label(c.miolo, text=ref["nota"],
                         font=FONTE["corpo"], fg=COR["texto"],
                         bg=COR["superficie"], wraplength=480, justify=tk.LEFT
                         ).pack(anchor=tk.W, padx=18, pady=(6, 0))

            def abrir(url=ref["url"]):
                webbrowser.open(url)

            tk.Button(c.miolo, text="Abrir referencia",
                      bg=COR["cobalto"], fg=COR["branco"],
                      relief="flat", font=FONTE["botao"],
                      command=abrir, padx=14, pady=6
                      ).pack(anchor=tk.W, padx=18, pady=10)

    def _detalhe_imagens(self, m, cor_cat):
        """Aba Imagens - diagramas do marcador"""
        interior = self.detalhe_interior
        imagens = self.imagens.get(m["sigla"], {}).get("imagens", [])

        if not imagens:
            tk.Label(interior, text="Sem imagens disponíveis para este marcador",
                     font=FONTE["corpo"], fg=COR["texto2"],
                     bg=COR["fundo"]).pack(pady=20)
            return

        tk.Label(interior, text=f"📊 {len(imagens)} diagramas",
                 font=FONTE["subtit"], fg=COR["texto"],
                 bg=COR["fundo"]).pack(pady=(12, 8), padx=18, anchor=tk.W)

        self._refs_imagens.clear()

        for img in imagens:
            c = card(interior, cor_topo=cor_cat)
            c.pack(fill=tk.X, padx=18, pady=8)

            tk.Label(c.miolo, text=img["titulo"],
                     font=FONTE["medio"], fg=COR["texto"],
                     bg=COR["superficie"]).pack(anchor=tk.W, padx=18, pady=(10, 4))

            tk.Label(c.miolo, text=img["descricao"],
                     font=FONTE["corpo"], fg=COR["texto"],
                     bg=COR["superficie"], wraplength=480,
                     justify=tk.LEFT).pack(anchor=tk.W, padx=18, pady=(0, 8))

            self._montar_imagem(c.miolo, img["arquivo"])

    def _montar_imagem(self, parent, arquivo):
        """Exibe o PNG redimensionado, ou uma mensagem se nao for possivel."""
        caminho = DATA_DIR / "images" / arquivo

        if not caminho.exists():
            tk.Label(parent,
                     text=f"Imagem nao encontrada: {arquivo}\n"
                          f"Gere os diagramas com: python criar_imagens.py",
                     font=FONTE["pequeno"], fg=COR["bile"],
                     bg=COR["superficie"], justify=tk.LEFT
                     ).pack(anchor=tk.W, padx=18, pady=(0, 12))
            return

        try:
            from PIL import Image, ImageTk
        except ImportError:
            tk.Label(parent,
                     text="Instale o Pillow para ver os diagramas:  pip install pillow",
                     font=FONTE["pequeno"], fg=COR["texto2"],
                     bg=COR["superficie"]).pack(anchor=tk.W, padx=18, pady=(0, 12))
            return

        try:
            imagem = Image.open(caminho)
            largura_max = 520
            if imagem.width > largura_max:
                proporcao = largura_max / imagem.width
                imagem = imagem.resize(
                    (largura_max, int(imagem.height * proporcao)),
                    Image.LANCZOS)
            foto = ImageTk.PhotoImage(imagem)
            self._refs_imagens.append(foto)  # sem isso o Tk descarta a imagem
            tk.Label(parent, image=foto, bg=COR["superficie"]
                     ).pack(padx=18, pady=(0, 12))
        except Exception as e:
            tk.Label(parent, text=f"Nao foi possivel abrir {arquivo}: {e}",
                     font=FONTE["pequeno"], fg=COR["erro"],
                     bg=COR["superficie"], wraplength=480, justify=tk.LEFT
                     ).pack(anchor=tk.W, padx=18, pady=(0, 12))

    def _barra_referencia(self, parent, m, cor):
        frame = tk.Frame(parent, bg=COR["superficie"], pady=10)
        frame.pack(fill=tk.X, padx=18)
        tk.Label(frame, text="Zona normal",
                 font=FONTE["pequeno"], fg=COR["texto3"],
                 bg=COR["superficie"]).pack(anchor=tk.W)
        c = tk.Canvas(frame, width=460, height=14,
                       bg=COR["superficie"], highlightthickness=0)
        c.pack(anchor=tk.W, pady=4)
        c.create_polygon(_pts_round_rect(0, 0, 460, 14, 7),
                          smooth=True, fill=COR["borda"], outline="")
        c.create_polygon(_pts_round_rect(150, 0, 310, 14, 7),
                          smooth=True, fill=cor, outline="")
        c.create_polygon(_pts_round_rect(152, 2, 308, 7, 3),
                          smooth=True, fill=clarear(cor, 0.4), outline="")
        legenda = tk.Frame(frame, bg=COR["superficie"])
        legenda.pack(fill=tk.X)
        tk.Label(legenda, text=f"↙ Baixo", font=FONTE["pequeno"],
                 fg=COR["cobalto"], bg=COR["superficie"]).pack(side=tk.LEFT)
        tk.Label(legenda,
                 text=f"{m['valor_ref_min']}  ──  {m['valor_ref_max']}  {m['unidade']}",
                 font=("Consolas", 9, "bold"), fg=cor,
                 bg=COR["superficie"]).pack(side=tk.LEFT, padx=18)
        tk.Label(legenda, text="Alto ↘", font=FONTE["pequeno"],
                 fg=COR["erro"], bg=COR["superficie"]).pack(side=tk.RIGHT)


# ─────────────────────────────────────────────
# MODO QUIZ
# ─────────────────────────────────────────────
class TelaQuiz(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=COR["fundo"])
        self.controller = controller
        self.perguntas = carregar_quiz()
        self.perguntas_embaralhadas = []
        self.indice = 0
        self.acertos = 0
        self.respondido = False
        self.escolha = None
        self.total = 0
        self.barra_prog = None
        self._construir()

    def _construir(self):
        barra_topo(self, self.controller, titulo="🧠  Quiz")
        self.area = tk.Frame(self, bg=COR["fundo"])
        self.area.pack(fill=tk.BOTH, expand=True)
        self._configurar()

    def _configurar(self):
        for w in self.area.winfo_children():
            w.destroy()

        centro = tk.Frame(self.area, bg=COR["fundo"])
        centro.pack(expand=True)

        CirculoDuo(centro, "🧠", cor=COR["cobalto"], tamanho=110,
                   bg_parent=COR["fundo"]).pack(pady=(20, 14))

        tk.Label(centro, text="Pronto para o quiz?",
                 font=("Segoe UI Black", 22),
                 fg=COR["texto"], bg=COR["fundo"]).pack()
        tk.Label(centro,
                 text=f"Banco com {len(self.perguntas)} perguntas embaralhadas",
                 font=FONTE["corpo"], fg=COR["texto2"],
                 bg=COR["fundo"]).pack(pady=(4, 22))

        c = card(centro)
        c.pack(padx=40, pady=10, fill=tk.X)
        tk.Label(c.miolo, text="Quantas perguntas?",
                 font=FONTE["medio"], fg=COR["texto"],
                 bg=COR["superficie"]).pack(pady=(16, 10))

        self.num_perguntas = tk.IntVar(value=min(10, len(self.perguntas)))
        opcoes = [5, 8, 10, 12] if len(self.perguntas) >= 12 else \
                 list(range(3, len(self.perguntas) + 1))

        bloco = tk.Frame(c.miolo, bg=COR["superficie"])
        bloco.pack(pady=4)
        self._chips_num = {}
        for n in opcoes:
            chip = self._chip_num(bloco, n)
            self._chips_num[n] = chip
            chip.pack(side=tk.LEFT, padx=6)
        self._atualizar_chips_num()

        tk.Frame(c.miolo, bg=COR["superficie"], height=10).pack()
        BotaoDuo(c.miolo, "Iniciar Quiz",
                 comando=self._iniciar,
                 cor=COR["primaria"], fonte=FONTE["botao_g"],
                 padx=40, pady=14,
                 bg_parent=COR["superficie"]).pack(pady=18)

    def _chip_num(self, parent, n):
        var = self.num_perguntas
        wrap = tk.Frame(parent, bg=COR["superficie"], cursor="hand2")
        lbl = tk.Label(wrap, text=str(n),
                       font=("Segoe UI Black", 16),
                       fg=COR["cobalto"], bg=clarear(COR["cobalto"], 0.85),
                       padx=18, pady=8)
        lbl.pack()

        def sel(_=None):
            var.set(n)
            self._atualizar_chips_num()
        wrap.bind("<Button-1>", sel)
        lbl.bind("<Button-1>", sel)
        wrap.lbl = lbl
        return wrap

    def _atualizar_chips_num(self):
        if not hasattr(self, "_chips_num"):
            return
        sel = self.num_perguntas.get()
        for n, chip in self._chips_num.items():
            ativo = (n == sel)
            chip.lbl.config(bg=COR["cobalto"] if ativo else clarear(COR["cobalto"], 0.85),
                            fg=COR["branco"] if ativo else COR["cobalto"])

    def _iniciar(self):
        n = self.num_perguntas.get()
        self.perguntas_embaralhadas = random.sample(
            self.perguntas, min(n, len(self.perguntas)))
        self.total = len(self.perguntas_embaralhadas)
        self.indice = 0
        self.acertos = 0
        self._pergunta()

    def _pergunta(self):
        for w in self.area.winfo_children():
            w.destroy()

        if self.indice >= self.total:
            self._resultado()
            return

        self.respondido = False
        self.escolha = None
        p = self.perguntas_embaralhadas[self.indice]
        cor_cat = COR["categoria"].get(p.get("categoria", ""), COR["cobalto"])

        # Barra de progresso superior
        prog = tk.Frame(self.area, bg=COR["fundo"], pady=12)
        prog.pack(fill=tk.X, padx=40)
        self.barra_prog = BarraProgresso(prog, largura=600, altura=14,
                                          cor=COR["primaria"], bg_parent=COR["fundo"])
        self.barra_prog.set(self.indice / self.total)
        self.barra_prog.pack(side=tk.LEFT, padx=(0, 14))
        tk.Label(prog, text=f"{self.indice + 1}/{self.total}",
                 font=FONTE["botao"], fg=COR["texto2"],
                 bg=COR["fundo"]).pack(side=tk.LEFT)

        # Etiqueta de categoria
        chip_cat = tk.Frame(self.area, bg=COR["fundo"])
        chip_cat.pack(padx=40, pady=(0, 8), anchor=tk.W)
        tk.Label(chip_cat,
                 text=f"  {p.get('categoria', '—').upper()}  ",
                 font=("Segoe UI", 9, "bold"),
                 fg=COR["branco"], bg=cor_cat,
                 pady=4).pack()

        # Pergunta
        tk.Label(self.area, text=p["pergunta"],
                 font=("Segoe UI Black", 17),
                 fg=COR["texto"], bg=COR["fundo"],
                 wraplength=720, justify=tk.LEFT).pack(
            padx=40, pady=(4, 18), anchor=tk.W)

        # Alternativas (rolagem se precisar)
        scroll = tk.Canvas(self.area, bg=COR["fundo"], highlightthickness=0)
        sb = tk.Scrollbar(self.area, orient="vertical", command=scroll.yview)
        interior = tk.Frame(scroll, bg=COR["fundo"])
        interior.bind("<Configure>",
                      lambda _: scroll.configure(scrollregion=scroll.bbox("all")))
        scroll.create_window((0, 0), window=interior, anchor="nw",
                              width=820)
        scroll.configure(yscrollcommand=sb.set)
        scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=40)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._alternativas = []
        for i, texto in enumerate(p["alternativas"]):
            alt = self._cartao_alternativa(interior, i, texto)
            alt.pack(fill=tk.X, pady=5)
            self._alternativas.append(alt)

        # Rodapé de ação
        self._rodape_acao = tk.Frame(self.area, bg=COR["fundo"], pady=12)
        self._rodape_acao.pack(fill=tk.X, side=tk.BOTTOM)
        self._btn_verificar = BotaoDuo(self._rodape_acao, "Verificar",
                                       comando=lambda: self._verificar(p),
                                       cor=COR["borda_forte"],
                                       cor_texto=COR["texto3"],
                                       fonte=FONTE["botao_g"],
                                       padx=60, pady=14,
                                       bg_parent=COR["fundo"])
        self._btn_verificar.pack()

    def _cartao_alternativa(self, parent, indice, texto):
        wrap = tk.Frame(parent, bg=COR["fundo"], cursor="hand2")
        borda_externa = tk.Frame(wrap, bg=COR["borda"])
        borda_externa.pack(fill=tk.X)
        inner = tk.Frame(borda_externa, bg=COR["superficie"])
        inner.pack(fill=tk.X, padx=2, pady=(0, 2))

        letra = tk.Label(inner, text=chr(65 + indice),
                          font=("Segoe UI Black", 14),
                          fg=COR["texto2"], bg=COR["trilha"],
                          padx=14, pady=10, width=2)
        letra.pack(side=tk.LEFT, padx=10, pady=8)
        msg = tk.Label(inner, text=texto, font=FONTE["corpo"],
                        fg=COR["texto"], bg=COR["superficie"],
                        wraplength=680, justify=tk.LEFT, anchor=tk.W)
        msg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 14), pady=10)

        wrap.borda = borda_externa
        wrap.inner = inner
        wrap.letra = letra
        wrap.msg = msg
        wrap.indice = indice
        wrap.estado = "neutro"

        def selecionar(_=None):
            if self.respondido:
                return
            self.escolha = indice
            self._refresh_alternativas()

        for w in [wrap, borda_externa, inner, letra, msg]:
            w.bind("<Button-1>", selecionar)
        return wrap

    def _refresh_alternativas(self):
        for alt in self._alternativas:
            if alt.estado != "neutro":
                continue
            if alt.indice == self.escolha:
                alt.borda.config(bg=COR["cobalto"])
                alt.letra.config(bg=COR["cobalto"], fg=COR["branco"])
            else:
                alt.borda.config(bg=COR["borda"])
                alt.letra.config(bg=COR["trilha"], fg=COR["texto2"])
        # ativa botão Verificar
        if self.escolha is not None and not self.respondido:
            self._btn_verificar.cor = COR["primaria"]
            self._btn_verificar.cor_sombra = escurecer(COR["primaria"], 0.25)
            self._btn_verificar.cor_texto = COR["branco"]
            self._btn_verificar._desenhar()

    def _verificar(self, p):
        if self.escolha is None or self.respondido:
            return
        self._responder(self.escolha, p)

    def _responder(self, indice_resp, p):
        if self.respondido:
            return
        self.respondido = True
        self.escolha = indice_resp
        correto = p["resposta_correta"]
        acertou = (indice_resp == correto)

        for alt in self._alternativas:
            if alt.indice == correto:
                alt.estado = "correto"
                alt.borda.config(bg=COR["sucesso"])
                alt.inner.config(bg=COR["sucesso_light"])
                alt.letra.config(bg=COR["sucesso"], fg=COR["branco"])
                alt.msg.config(bg=COR["sucesso_light"])
            elif alt.indice == indice_resp:
                alt.estado = "errado"
                alt.borda.config(bg=COR["erro"])
                alt.inner.config(bg=COR["erro_light"])
                alt.letra.config(bg=COR["erro"], fg=COR["branco"])
                alt.msg.config(bg=COR["erro_light"])

        if acertou:
            self.acertos += 1
            self.controller.xp += 10
            self.controller.streak += 1
        else:
            self.controller.streak = 0

        self._feedback(p, acertou)

    def _feedback(self, p, acertou):
        # Substitui rodapé por painel grande tipo Duo
        for w in self._rodape_acao.winfo_children():
            w.destroy()
        self._rodape_acao.config(
            bg=COR["sucesso_light"] if acertou else COR["erro_light"])

        cor = COR["sucesso_dark"] if acertou else COR["erro_dark"]
        titulo = "Excelente!  +10 XP" if acertou else "Não foi dessa vez"
        icone = "✅" if acertou else "❌"

        cab = tk.Frame(self._rodape_acao,
                       bg=COR["sucesso_light"] if acertou else COR["erro_light"])
        cab.pack(fill=tk.X, padx=40, pady=(12, 4))
        tk.Label(cab, text=icone, font=("Segoe UI Emoji", 22),
                 bg=cab.cget("bg"), fg=cor).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(cab, text=titulo, font=("Segoe UI Black", 16),
                 bg=cab.cget("bg"), fg=cor).pack(side=tk.LEFT)

        tk.Label(self._rodape_acao, text=p["explicacao"],
                 font=FONTE["corpo"], fg=COR["texto"],
                 bg=self._rodape_acao.cget("bg"),
                 wraplength=720, justify=tk.LEFT).pack(
            padx=40, pady=(0, 12), anchor=tk.W)

        self.indice += 1
        label_btn = "Continuar" if self.indice < self.total else "Ver Resultado"
        BotaoDuo(self._rodape_acao, label_btn,
                 comando=self._pergunta,
                 cor=COR["sucesso"] if acertou else COR["erro"],
                 fonte=FONTE["botao_g"], padx=60, pady=14,
                 bg_parent=self._rodape_acao.cget("bg")).pack(pady=(0, 14))

    def _resultado(self):
        for w in self.area.winfo_children():
            w.destroy()
        pct = (self.acertos / self.total * 100) if self.total else 0
        if pct >= 80:
            emoji, cor, msg = "🏆", COR["primaria"], "Excelente! Você domina o conteúdo."
        elif pct >= 60:
            emoji, cor, msg = "👍", COR["bile"], "Bom resultado — revise os erros."
        else:
            emoji, cor, msg = "📖", COR["sangue"], "Continue estudando os marcadores."

        centro = tk.Frame(self.area, bg=COR["fundo"])
        centro.pack(expand=True)

        CirculoDuo(centro, emoji, cor=cor, tamanho=120,
                   bg_parent=COR["fundo"]).pack(pady=(24, 14))
        tk.Label(centro, text="Lição concluída!",
                 font=("Segoe UI Black", 24),
                 fg=COR["texto"], bg=COR["fundo"]).pack()
        tk.Label(centro, text=f"{self.acertos} de {self.total} corretas",
                 font=FONTE["subtit"], fg=COR["texto2"],
                 bg=COR["fundo"]).pack(pady=4)

        c = card(centro, cor_topo=cor)
        c.pack(pady=20, padx=60)
        tk.Label(c.miolo, text=f"{pct:.0f}%",
                 font=("Segoe UI Black", 48),
                 fg=cor, bg=COR["superficie"]).pack(padx=44, pady=(14, 4))
        tk.Label(c.miolo, text=msg, font=FONTE["corpo"],
                 fg=COR["texto2"], bg=COR["superficie"]).pack(padx=24, pady=(0, 18))

        btns = tk.Frame(centro, bg=COR["fundo"])
        btns.pack(pady=18)
        BotaoDuo(btns, "Nova Lição", comando=self._configurar,
                 cor=COR["primaria"], fonte=FONTE["botao_g"],
                 padx=30, pady=12, bg_parent=COR["fundo"]).pack(side=tk.LEFT, padx=8)
        BotaoDuo(btns, "Voltar ao Menu",
                 comando=lambda: self.controller.mostrar("inicio"),
                 cor=COR["trilha"], cor_texto=COR["texto"],
                 fonte=FONTE["botao_g"], padx=30, pady=12,
                 bg_parent=COR["fundo"]).pack(side=tk.LEFT, padx=8)


# ─────────────────────────────────────────────
# MODO DIAGNÓSTICO SIMULADO
# ─────────────────────────────────────────────
class TelaDiagnostico(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=COR["fundo"])
        self.controller = controller
        self.casos = carregar_casos()
        self.caso_atual = None
        self.respondido = False
        self._construir()

    def _construir(self):
        barra_topo(self, self.controller,
                   titulo="🩺  Diagnóstico Simulado")
        self.area = tk.Frame(self, bg=COR["fundo"])
        self.area.pack(fill=tk.BOTH, expand=True)
        self._selecao()

    def _selecao(self):
        for w in self.area.winfo_children():
            w.destroy()

        canvas = tk.Canvas(self.area, bg=COR["fundo"], highlightthickness=0)
        sb = tk.Scrollbar(self.area, orient="vertical", command=canvas.yview)
        interior = tk.Frame(canvas, bg=COR["fundo"])
        interior.bind("<Configure>",
                      lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=interior, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(interior, text="Casos Clínicos",
                 font=("Segoe UI Black", 22),
                 fg=COR["texto"], bg=COR["fundo"]).pack(
            pady=(20, 4), padx=40, anchor=tk.W)
        tk.Label(interior, text="Escolha um caso, analise os exames e dê o diagnóstico",
                 font=FONTE["corpo"], fg=COR["texto2"],
                 bg=COR["fundo"]).pack(pady=(0, 18), padx=40, anchor=tk.W)

        for i, caso in enumerate(self.casos):
            self._card_caso(interior, caso, i + 1)

    def _card_caso(self, parent, caso, n):
        c = card(parent, cor_topo=COR["indicador"])
        c.pack(fill=tk.X, padx=40, pady=8)

        cab = tk.Frame(c.miolo, bg=COR["superficie"])
        cab.pack(fill=tk.X, padx=18, pady=(14, 6))

        # Circulinho com número
        num = tk.Canvas(cab, width=34, height=34,
                        bg=COR["superficie"], highlightthickness=0)
        num.create_oval(2, 2, 32, 32, fill=COR["indicador_light"], outline="")
        num.create_text(17, 17, text=str(n),
                         font=("Segoe UI Black", 14), fill=COR["indicador_dark"])
        num.pack(side=tk.LEFT, padx=(0, 12))

        tk.Label(cab, text=caso["titulo"],
                 font=("Segoe UI Black", 14),
                 fg=COR["texto"], bg=COR["superficie"]).pack(side=tk.LEFT)

        prev = caso["historia"][:130] + "..."
        tk.Label(c.miolo, text=prev,
                 font=FONTE["pequeno"], fg=COR["texto2"],
                 bg=COR["superficie"], wraplength=720,
                 justify=tk.LEFT).pack(padx=18, anchor=tk.W)

        # Mini exames
        exames_txt = "  ·  ".join([
            f"{k} {v['valor']} {v['unidade']}"
            for k, v in list(caso["exames"].items())[:3]
        ]) + "  ..."
        tk.Label(c.miolo, text=f"🔬  {exames_txt}",
                 font=("Consolas", 9), fg=COR["cobalto_dark"],
                 bg=COR["superficie"]).pack(padx=18, pady=(8, 0), anchor=tk.W)

        BotaoDuo(c.miolo, "Analisar caso",
                 comando=lambda c_=caso: self._abrir(c_),
                 cor=COR["indicador"], padx=22, pady=9,
                 bg_parent=COR["superficie"]).pack(
            anchor=tk.W, padx=18, pady=14)

    def _abrir(self, caso):
        self.caso_atual = caso
        self.respondido = False
        for w in self.area.winfo_children():
            w.destroy()

        canvas = tk.Canvas(self.area, bg=COR["fundo"], highlightthickness=0)
        sb = tk.Scrollbar(self.area, orient="vertical", command=canvas.yview)
        interior = tk.Frame(canvas, bg=COR["fundo"])
        interior.bind("<Configure>",
                      lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=interior, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_caso = canvas

        # Cabeçalho violeta (indicador)
        cab = tk.Frame(interior, bg=COR["indicador"], pady=22)
        cab.pack(fill=tk.X)
        tk.Label(cab, text="CASO CLÍNICO",
                 font=("Segoe UI", 9, "bold"),
                 fg=clarear(COR["indicador"], 0.6),
                 bg=COR["indicador"]).pack(padx=24, anchor=tk.W)
        tk.Label(cab, text=caso["titulo"],
                 font=("Segoe UI Black", 18),
                 fg=COR["branco"], bg=COR["indicador"]).pack(padx=24, anchor=tk.W)

        # História
        c_hist = card(interior, cor_topo=COR["indicador"])
        c_hist.pack(fill=tk.X, padx=24, pady=12)
        tk.Label(c_hist.miolo, text="📋  HISTÓRIA CLÍNICA",
                 font=("Segoe UI", 10, "bold"),
                 fg=COR["texto3"], bg=COR["superficie"]).pack(
            anchor=tk.W, padx=18, pady=(14, 4))
        tk.Label(c_hist.miolo, text=caso["historia"],
                 font=FONTE["corpo"], fg=COR["texto"],
                 bg=COR["superficie"], wraplength=720,
                 justify=tk.LEFT).pack(anchor=tk.W, padx=18, pady=(0, 14))

        # Exames
        tk.Label(interior, text="🔬  Exames laboratoriais",
                 font=("Segoe UI Black", 14),
                 fg=COR["texto"], bg=COR["fundo"]).pack(
            anchor=tk.W, padx=24, pady=(8, 6))

        for nome_ex, dados in caso["exames"].items():
            self._linha_exame(interior, nome_ex, dados)

        # Pergunta
        tk.Label(interior, text="🩺  Qual o diagnóstico mais provável?",
                 font=("Segoe UI Black", 16),
                 fg=COR["texto"], bg=COR["fundo"]).pack(
            anchor=tk.W, padx=24, pady=(22, 10))

        self.frame_diag = tk.Frame(interior, bg=COR["fundo"])
        self.frame_diag.pack(fill=tk.X, padx=24)

        alts = caso["alternativas"][:]
        random.shuffle(alts)
        self.btns_diag = []
        for alt in alts:
            cartao = self._cartao_diag(self.frame_diag, alt, caso)
            cartao.pack(fill=tk.X, pady=5)
            self.btns_diag.append(cartao)

        self.frame_exp = tk.Frame(interior, bg=COR["fundo"])
        self.frame_exp.pack(fill=tk.X, padx=24, pady=12)

        BotaoDuo(interior, "Voltar aos casos",
                 comando=self._selecao,
                 cor=COR["trilha"], cor_texto=COR["texto"],
                 padx=22, pady=9,
                 bg_parent=COR["fundo"]).pack(anchor=tk.W, padx=24, pady=18)

    def _linha_exame(self, parent, nome, dados):
        val = dados["valor"]
        ref_min = dados["ref_min"]
        ref_max = dados["ref_max"]
        if val > ref_max:
            status, cor, seta = "ALTO", COR["erro"], "⬆"
        elif val < ref_min:
            status, cor, seta = "BAIXO", COR["cobalto"], "⬇"
        else:
            status, cor, seta = "NORMAL", COR["sucesso"], "✓"

        c = card(parent, cor_topo=cor, espessura_topo=3)
        c.pack(fill=tk.X, padx=24, pady=3)

        linha = tk.Frame(c.miolo, bg=COR["superficie"])
        linha.pack(fill=tk.X, padx=18, pady=10)
        tk.Label(linha, text=nome,
                 font=("Segoe UI", 12, "bold"),
                 fg=COR["texto"], bg=COR["superficie"]).pack(side=tk.LEFT)

        direita = tk.Frame(linha, bg=COR["superficie"])
        direita.pack(side=tk.RIGHT)
        tk.Label(direita,
                 text=f"Ref. {ref_min}–{ref_max} {dados['unidade']}",
                 font=FONTE["pequeno"], fg=COR["texto3"],
                 bg=COR["superficie"]).pack(side=tk.LEFT, padx=12)
        tk.Label(direita,
                 text=f"{seta} {val} {dados['unidade']}",
                 font=("Segoe UI Black", 14),
                 fg=cor, bg=COR["superficie"]).pack(side=tk.LEFT, padx=6)
        tag = tk.Frame(direita, bg=clarear(cor, 0.85))
        tag.pack(side=tk.LEFT, padx=10)
        tk.Label(tag, text=status,
                 font=("Segoe UI", 9, "bold"),
                 fg=cor, bg=clarear(cor, 0.85),
                 padx=10, pady=3).pack()

    def _cartao_diag(self, parent, alt, caso):
        wrap = tk.Frame(parent, bg=COR["fundo"], cursor="hand2")
        borda = tk.Frame(wrap, bg=COR["borda"])
        borda.pack(fill=tk.X)
        inner = tk.Frame(borda, bg=COR["superficie"])
        inner.pack(fill=tk.X, padx=2, pady=(0, 2))
        msg = tk.Label(inner, text=alt, font=FONTE["corpo"],
                        fg=COR["texto"], bg=COR["superficie"],
                        wraplength=700, justify=tk.LEFT, anchor=tk.W)
        msg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=18, pady=12)

        wrap.borda = borda
        wrap.inner = inner
        wrap.msg = msg
        wrap.alt = alt

        def clicar(_=None):
            self._verificar_diag(alt, caso)
        for w in [wrap, borda, inner, msg]:
            w.bind("<Button-1>", clicar)
        return wrap

    def _verificar_diag(self, escolha, caso):
        if self.respondido:
            return
        self.respondido = True
        correto = caso["resposta_correta"]
        acertou = (escolha == correto)

        for c in self.btns_diag:
            if c.alt == correto:
                c.borda.config(bg=COR["sucesso"])
                c.inner.config(bg=COR["sucesso_light"])
                c.msg.config(bg=COR["sucesso_light"])
            elif c.alt == escolha:
                c.borda.config(bg=COR["erro"])
                c.inner.config(bg=COR["erro_light"])
                c.msg.config(bg=COR["erro_light"])

        if acertou:
            self.controller.xp += 25
            self.controller.streak += 1
        else:
            self.controller.streak = 0

        # Painel de feedback
        cor = COR["sucesso_dark"] if acertou else COR["erro_dark"]
        bg = COR["sucesso_light"] if acertou else COR["erro_light"]
        titulo = "Diagnóstico correto!  +25 XP" if acertou else "Diagnóstico incorreto"
        icone = "✅" if acertou else "❌"

        panel = tk.Frame(self.frame_exp, bg=bg)
        panel.pack(fill=tk.X)

        cab = tk.Frame(panel, bg=bg)
        cab.pack(fill=tk.X, padx=14, pady=(12, 4))
        tk.Label(cab, text=icone, font=("Segoe UI Emoji", 20),
                 bg=bg, fg=cor).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(cab, text=titulo, font=("Segoe UI Black", 14),
                 bg=bg, fg=cor).pack(side=tk.LEFT)

        if not acertou:
            tk.Label(panel,
                     text=f"Resposta correta: {correto}",
                     font=FONTE["medio"], fg=COR["sucesso_dark"],
                     bg=bg).pack(anchor=tk.W, padx=14, pady=(0, 6))

        tk.Label(panel, text="📖 Explicação",
                 font=("Segoe UI", 10, "bold"),
                 fg=COR["texto2"], bg=bg).pack(anchor=tk.W, padx=14)
        tk.Label(panel, text=caso["explicacao"],
                 font=FONTE["corpo"], fg=COR["texto"],
                 bg=bg, wraplength=720, justify=tk.LEFT).pack(
            anchor=tk.W, padx=14, pady=(4, 14))

        self.canvas_caso.after(120, lambda: self.canvas_caso.yview_moveto(1.0))


# ─────────────────────────────────────────────
# CONTROLADOR PRINCIPAL
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BioquímicaEDU — Software Educacional Interativo")
        self.geometry("1100x720")
        self.minsize(960, 640)
        self.configure(bg=COR["fundo"])

        # Estado de gamificação (em sessão)
        self.xp = 0
        self.streak = 0

        # Centralizar
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

        self.telas = {}
        self._criar_telas()
        self.mostrar("inicio")

    def _criar_telas(self):
        for nome, Classe in [
            ("inicio",      TelaInicial),
            ("estudo",      TelaEstudo),
            ("flashcards",  TelaFlashcards),
            ("quiz",        TelaQuiz),
            ("diagnostico", TelaDiagnostico),
        ]:
            tela = Classe(self, self)
            tela.place(relwidth=1, relheight=1)
            self.telas[nome] = tela

    def mostrar(self, nome):
        # Recriar telas com estado para refletir XP/streak atualizados
        if nome in self.telas:
            self.telas[nome].destroy()
        Classe = {"inicio": TelaInicial, "estudo": TelaEstudo,
                  "flashcards": TelaFlashcards,
                  "quiz": TelaQuiz, "diagnostico": TelaDiagnostico}[nome]
        tela = Classe(self, self)
        tela.place(relwidth=1, relheight=1)
        self.telas[nome] = tela
        self.telas[nome].tkraise()


# ─────────────────────────────────────────────
if __name__ == "__main__":
    App().mainloop()
