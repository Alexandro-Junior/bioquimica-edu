"""
BioquímicaEDU — Versão Enhanced com IA Integrada
Desktop (Tkinter) + Chat Local (Ollama) + Quiz Dinâmico

Todas as funcionalidades:
- 20 marcadores com filtros
- Chat inteligente sobre marcadores
- Quiz dinâmico gerado por IA
- Discussão de casos com feedback IA
- 100% privado (Ollama local)
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
import csv
import random
import threading
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Importa módulo de IA
try:
    from ollama_ia import ia
    IA_DISPONIVEL = ia.disponivel
except ImportError:
    print("⚠️ ollama_ia não encontrado. Chat será offline.")
    IA_DISPONIVEL = False

# ─────────────────────────────────────────────
# CORES (MESMO DO MAIN.PY)
# ─────────────────────────────────────────────
COR = {
    "fundo":           "#FAF6EE",
    "superficie":      "#FFFFFF",
    "topo":            "#FFFFFF",
    "trilha":          "#F1EBDC",
    "primaria":        "#16A34A",
    "primaria_dark":   "#15803D",
    "primaria_light":  "#DCFCE7",
    "sangue":          "#E11D48",
    "sangue_dark":     "#9F1239",
    "sangue_light":    "#FFE4E6",
    "bile":            "#F59E0B",
    "bile_dark":       "#B45309",
    "bile_light":      "#FEF3C7",
    "indicador":       "#7C3AED",
    "indicador_dark":  "#5B21B6",
    "indicador_light": "#EDE9FE",
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
        "Hepático":   "#F59E0B",
        "Renal":      "#06B6D4",
        "Glicêmico":  "#16A34A",
        "Lipídico":   "#8B5CF6",
        "Eletrólito": "#3B82F6",
        "Cardíaco":   "#E11D48",
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

# ─────────────────────────────────────────────
# WIDGET DE CHAT
# ─────────────────────────────────────────────
class PainelChat(tk.Frame):
    def __init__(self, parent, marcador=None, **kwargs):
        super().__init__(parent, bg=COR["superficie"], **kwargs)
        self.marcador = marcador
        self.mensagens = []

        # Cabeçalho
        cab = tk.Frame(self, bg=COR["cobalto"], height=40)
        cab.pack(fill=tk.X)
        cab.pack_propagate(False)
        tk.Label(cab, text="🤖  Tutor IA", font=FONTE["botao"],
                 fg=COR["branco"], bg=COR["cobalto"]).pack(side=tk.LEFT, padx=12)
        status = "Conectado" if IA_DISPONIVEL else "Offline (respostas básicas)"
        tk.Label(cab, text=status, font=FONTE["pequeno"],
                 fg=COR["cobalto_light"], bg=COR["cobalto"]).pack(side=tk.RIGHT, padx=12)

        # Área de mensagens
        scroll = tk.Frame(self)
        scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas_msgs = tk.Canvas(scroll, bg=COR["trilha"], highlightthickness=0)
        sb = tk.Scrollbar(scroll, orient="vertical", command=self.canvas_msgs.yview)
        self.msgs_interior = tk.Frame(self.canvas_msgs, bg=COR["trilha"])
        self.msgs_interior.bind(
            "<Configure>",
            lambda _: self.canvas_msgs.configure(scrollregion=self.canvas_msgs.bbox("all"))
        )
        self.canvas_msgs.create_window((0, 0), window=self.msgs_interior, anchor="nw")
        self.canvas_msgs.configure(yscrollcommand=sb.set)
        self.canvas_msgs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Input
        input_frame = tk.Frame(self, bg=COR["superficie"])
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.input_text = tk.Entry(input_frame, font=FONTE["corpo"],
                                   bg=COR["trilha"], fg=COR["texto"],
                                   insertbackground=COR["texto"],
                                   relief="flat", bd=0)
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.input_text.bind("<Return>", lambda _: self._enviar())

        btn_enviar = tk.Button(input_frame, text="Enviar", bg=COR["cobalto"],
                               fg=COR["branco"], relief="flat", bd=0,
                               command=self._enviar, font=FONTE["pequeno"],
                               padx=16, pady=8)
        btn_enviar.pack(side=tk.LEFT, padx=(8, 0))

        self._adicionar_msg_saudacao()

    def _adicionar_msg_saudacao(self):
        """Mensagem inicial"""
        marcador_nome = self.marcador.get("nome", "Tutor") if self.marcador else "Tutor"
        msg_frame = tk.Frame(self.msgs_interior, bg=COR["cobalto_light"])
        msg_frame.pack(fill=tk.X, padx=8, pady=4)

        tk.Label(msg_frame,
                 text=f"👋 Olá! Estou aqui para ajudar com dúvidas sobre {marcador_nome}.\n"
                       "Faça perguntas, pedir exemplos ou testes!",
                 font=FONTE["pequeno"], fg=COR["cobalto_dark"],
                 bg=COR["cobalto_light"], wraplength=280,
                 justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=8)

    def _enviar(self):
        """Envia pergunta à IA"""
        pergunta = self.input_text.get().strip()
        if not pergunta:
            return

        self.input_text.delete(0, tk.END)

        # Mostra pergunta do usuário
        self._adicionar_msg_usuario(pergunta)

        # Gera resposta em thread
        thread = threading.Thread(
            target=self._gerar_resposta,
            args=(pergunta,)
        )
        thread.daemon = True
        thread.start()

    def _adicionar_msg_usuario(self, texto):
        """Mostra mensagem do usuário"""
        msg_frame = tk.Frame(self.msgs_interior, bg=COR["primaria_light"])
        msg_frame.pack(fill=tk.X, padx=8, pady=4)

        tk.Label(msg_frame, text=f"👤 Você:\n{texto}",
                 font=FONTE["pequeno"], fg=COR["texto"],
                 bg=COR["primaria_light"], wraplength=280,
                 justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=6)

        self.canvas_msgs.yview_moveto(1.0)

    def _adicionar_msg_ia(self, texto):
        """Mostra mensagem da IA"""
        msg_frame = tk.Frame(self.msgs_interior, bg=COR["cobalto_light"])
        msg_frame.pack(fill=tk.X, padx=8, pady=4)

        tk.Label(msg_frame, text=f"🤖 IA:\n{texto}",
                 font=FONTE["pequeno"], fg=COR["texto"],
                 bg=COR["cobalto_light"], wraplength=280,
                 justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=6)

        self.canvas_msgs.yview_moveto(1.0)

    def _gerar_resposta(self, pergunta):
        """Chama IA e mostra resposta"""
        try:
            resposta = ia.chat_marcador(
                self.marcador.get("nome", "Marcador"),
                pergunta,
                callback=None
            )
            self._adicionar_msg_ia(resposta)
        except Exception as e:
            self._adicionar_msg_ia(f"❌ Erro: {e}\n\nTente novamente ou verifique se Ollama está rodando.")

# ─────────────────────────────────────────────
# TELA ESTUDO ENHANCEMENT
# ─────────────────────────────────────────────
class TelaEstudoEnhanced(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=COR["fundo"])
        self.controller = controller
        self.marcadores = carregar_marcadores()
        self.categorias = sorted({m["categoria"] for m in self.marcadores})
        self.cat_selecionada = tk.StringVar(value="Todas")
        self.busca_var = tk.StringVar()
        self.busca_var.trace("w", lambda *_: self._filtrar())
        self.marcador_atual = None
        self._construir()

    def _construir(self):
        # Nav
        nav = tk.Frame(self, bg=COR["topo"], height=55)
        nav.pack(fill=tk.X)
        nav.pack_propagate(False)
        tk.Button(nav, text="← Menu", bg=COR["topo"], fg=COR["texto2"],
                  relief="flat", command=lambda: self.controller.mostrar("inicio"),
                  font=FONTE["pequeno"], padx=15, pady=15).pack(side=tk.LEFT)
        tk.Label(nav, text="📚  Modo Estudo + IA", font=FONTE["medio"],
                 fg=COR["texto"], bg=COR["topo"]).pack(side=tk.LEFT, padx=10)

        # Filtros
        filtros = tk.Frame(self, bg=COR["fundo"], pady=12)
        filtros.pack(fill=tk.X, padx=20)

        tk.Label(filtros, text="Buscar:", font=FONTE["pequeno"],
                 fg=COR["texto2"], bg=COR["fundo"]).pack(side=tk.LEFT)
        entry = tk.Entry(filtros, textvariable=self.busca_var,
                         font=FONTE["corpo"], bg=COR["trilha"],
                         fg=COR["texto"], insertbackground=COR["texto"],
                         relief="flat", bd=0, width=20)
        entry.pack(side=tk.LEFT, padx=(5, 20), ipady=5)

        tk.Label(filtros, text="Categoria:", font=FONTE["pequeno"],
                 fg=COR["texto2"], bg=COR["fundo"]).pack(side=tk.LEFT)

        for cat in ["Todas"] + self.categorias:
            rb = tk.Radiobutton(
                filtros, text=cat, variable=self.cat_selecionada,
                value=cat, command=self._filtrar,
                bg=COR["fundo"], fg=COR["categoria"].get(cat, COR["texto"]),
                selectcolor=COR["trilha"], activebackground=COR["fundo"],
                font=FONTE["pequeno"], cursor="hand2"
            )
            rb.pack(side=tk.LEFT, padx=6)

        # Área com lista + detalhe + chat
        area = tk.Frame(self, bg=COR["fundo"])
        area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Lista (esquerda)
        esq = tk.Frame(area, bg=COR["superficie"], width=220)
        esq.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        esq.pack_propagate(False)

        tk.Label(esq, text="Marcadores", font=FONTE["medio"],
                 fg=COR["texto"], bg=COR["superficie"]).pack(pady=10)

        scroll_l = tk.Frame(esq, bg=COR["superficie"])
        scroll_l.pack(fill=tk.BOTH, expand=True)
        self.canvas_lista = tk.Canvas(scroll_l, bg=COR["superficie"], highlightthickness=0)
        sb = tk.Scrollbar(scroll_l, orient="vertical", command=self.canvas_lista.yview)
        self.lista_interior = tk.Frame(self.canvas_lista, bg=COR["superficie"])
        self.lista_interior.bind("<Configure>",
            lambda e: self.canvas_lista.configure(scrollregion=self.canvas_lista.bbox("all")))
        self.canvas_lista.create_window((0, 0), window=self.lista_interior, anchor="nw")
        self.canvas_lista.configure(yscrollcommand=sb.set)
        self.canvas_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Detalhe + Chat (direita)
        self.painel_detalhe = tk.Frame(area, bg=COR["fundo"])
        self.painel_detalhe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._placeholder()

        self._filtrar()

    def _filtrar(self):
        busca = self.busca_var.get().lower()
        cat = self.cat_selecionada.get()
        filtrados = [
            m for m in self.marcadores
            if (cat == "Todas" or m["categoria"] == cat)
            and (busca in m["nome"].lower() or busca in m["sigla"].lower())
        ]
        for w in self.lista_interior.winfo_children():
            w.destroy()
        for m in filtrados:
            self._item_lista(m)

    def _item_lista(self, m):
        cor_cat = COR["categoria"].get(m["categoria"], COR["primaria"])
        item = tk.Frame(self.lista_interior, bg=COR["superficie"], cursor="hand2")
        item.pack(fill=tk.X, pady=1)

        barra = tk.Frame(item, bg=cor_cat, width=4)
        barra.pack(side=tk.LEFT, fill=tk.Y)

        conteudo = tk.Frame(item, bg=COR["superficie"])
        conteudo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)

        tk.Label(conteudo, text=m["nome"], font=FONTE["pequeno"],
                 fg=COR["texto"], bg=COR["superficie"],
                 anchor=tk.W).pack(fill=tk.X)
        tk.Label(conteudo, text=f"{m['sigla']} · {m['categoria']}",
                 font=("Segoe UI", 9), fg=COR["texto2"],
                 bg=COR["superficie"], anchor=tk.W).pack(fill=tk.X)

        for w in [item, conteudo] + list(conteudo.winfo_children()):
            w.bind("<Button-1>", lambda _e, marc=m: self._detalhe(marc))
            w.bind("<Enter>", lambda _e, i=item: i.config(bg=COR["trilha"]))
            w.bind("<Leave>", lambda _e, i=item: i.config(bg=COR["superficie"]))

    def _placeholder(self):
        for w in self.painel_detalhe.winfo_children():
            w.destroy()
        tk.Label(self.painel_detalhe,
                 text="← Selecione um marcador",
                 font=FONTE["corpo"], fg=COR["texto2"],
                 bg=COR["fundo"]).pack(expand=True)

    def _detalhe(self, m):
        self.marcador_atual = m
        for w in self.painel_detalhe.winfo_children():
            w.destroy()

        cor_cat = COR["categoria"].get(m["categoria"], COR["primaria"])

        # Layout: esquerda (info) + direita (chat)
        layout = tk.Frame(self.painel_detalhe, bg=COR["fundo"])
        layout.pack(fill=tk.BOTH, expand=True)

        # ESQUERDA — Informações do marcador
        esq_info = tk.Frame(layout, bg=COR["fundo"], width=350)
        esq_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        esq_info.pack_propagate(False)

        canvas = tk.Canvas(esq_info, bg=COR["fundo"], highlightthickness=0)
        sb = tk.Scrollbar(esq_info, orient="vertical", command=canvas.yview)
        interior = tk.Frame(canvas, bg=COR["fundo"])
        interior.bind("<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=interior, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Cabeçalho
        cab = tk.Frame(interior, bg=cor_cat, pady=12)
        cab.pack(fill=tk.X)
        tk.Label(cab, text=m["nome"], font=("Segoe UI", 16, "bold"),
                 fg=COR["branco"], bg=cor_cat).pack(padx=16)
        tk.Label(cab, text=f"{m['sigla']} · {m['categoria']}",
                 font=FONTE["pequeno"], fg=COR["branco"], bg=cor_cat).pack(padx=16)

        # Valor ref
        card_ref = tk.Frame(interior, bg=COR["superficie"], relief="solid", bd=1)
        card_ref.pack(fill=tk.X, padx=12, pady=8)
        tk.Label(card_ref, text="Valor de Referência", font=FONTE["pequeno"],
                 fg=COR["texto3"], bg=COR["superficie"]).pack(anchor=tk.W, padx=12, pady=(8, 2))
        tk.Label(card_ref,
                 text=f"{m['valor_ref_min']} – {m['valor_ref_max']} {m['unidade']}",
                 font=("Segoe UI", 14, "bold"),
                 fg=cor_cat, bg=COR["superficie"]).pack(anchor=tk.W, padx=12, pady=(0, 8))

        # Interpretações
        for titulo, texto in [
            ("⬆ Quando ELEVADO", m["interpretacao_alta"]),
            ("⬇ Quando BAIXO", m["interpretacao_baixa"]),
        ]:
            c = tk.Frame(interior, bg=COR["superficie"], relief="solid", bd=1)
            c.pack(fill=tk.X, padx=12, pady=4)
            tk.Label(c, text=titulo, font=FONTE["pequeno"], fg=cor_cat,
                     bg=COR["superficie"]).pack(anchor=tk.W, padx=12, pady=(6, 2))
            tk.Label(c, text=texto, font=FONTE["corpo"], fg=COR["texto"],
                     bg=COR["superficie"], wraplength=300,
                     justify=tk.LEFT).pack(anchor=tk.W, padx=12, pady=(0, 8))

        # DIREITA — Chat com IA
        dir_chat = tk.Frame(layout, bg=COR["superficie"], relief="solid", bd=1, width=350)
        dir_chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dir_chat.pack_propagate(False)

        chat = PainelChat(dir_chat, marcador=m)
        chat.pack(fill=tk.BOTH, expand=True)

# ─────────────────────────────────────────────
# TELA QUIZ DINÂMICO (com IA)
# ─────────────────────────────────────────────
class TelaQuizDinamico(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=COR["fundo"])
        self.controller = controller
        self.marcadores = carregar_marcadores()
        self.perguntas_geradas = []
        self.indice = 0
        self.acertos = 0
        self.respondido = False
        self._construir()

    def _construir(self):
        nav = tk.Frame(self, bg=COR["topo"], height=55)
        nav.pack(fill=tk.X)
        nav.pack_propagate(False)
        tk.Button(nav, text="← Menu", bg=COR["topo"], fg=COR["texto2"],
                  relief="flat", command=lambda: self.controller.mostrar("inicio"),
                  font=FONTE["pequeno"], padx=15, pady=15).pack(side=tk.LEFT)
        tk.Label(nav, text="🧠  Quiz Dinâmico (IA)", font=FONTE["medio"],
                 fg=COR["texto"], bg=COR["topo"]).pack(side=tk.LEFT, padx=10)

        self.area = tk.Frame(self, bg=COR["fundo"])
        self.area.pack(fill=tk.BOTH, expand=True)
        self._tela_config()

    def _tela_config(self):
        for w in self.area.winfo_children():
            w.destroy()

        centro = tk.Frame(self.area, bg=COR["fundo"])
        centro.pack(expand=True)

        tk.Label(centro, text="🧠", font=("Segoe UI", 48),
                 fg=COR["cobalto"], bg=COR["fundo"]).pack(pady=20)
        tk.Label(centro, text="Quiz Dinâmico com IA",
                 font=FONTE["titulo"], fg=COR["texto"],
                 bg=COR["fundo"]).pack()
        tk.Label(centro,
                 text="Cada pergunta é gerada pela IA baseado nos marcadores",
                 font=FONTE["corpo"], fg=COR["texto2"],
                 bg=COR["fundo"]).pack(pady=8)

        card = tk.Frame(centro, bg=COR["superficie"], relief="solid", bd=1)
        card.pack(pady=20, padx=40, fill=tk.X)

        tk.Label(card, text="Quantas perguntas?",
                 font=FONTE["medio"], fg=COR["texto"],
                 bg=COR["superficie"]).pack(pady=12)

        self.num_perguntas = tk.IntVar(value=5)
        for n in [5, 8, 10]:
            tk.Radiobutton(card, text=str(n), variable=self.num_perguntas,
                           value=n, bg=COR["superficie"], fg=COR["texto"],
                           selectcolor=COR["fundo"], font=FONTE["corpo"]).pack()

        tk.Frame(card, height=8, bg=COR["superficie"]).pack()
        tk.Button(card, text="Iniciar", bg=COR["cobalto"], fg=COR["branco"],
                  relief="flat", font=FONTE["botao"],
                  command=self._iniciar, padx=30, pady=12).pack(pady=12)

    def _iniciar(self):
        n = self.num_perguntas.get()
        self.perguntas_geradas = []
        self.indice = 0
        self.acertos = 0
        self._gerar_proxima()

    def _gerar_proxima(self):
        if self.indice >= self.num_perguntas.get():
            self._resultado()
            return

        # Seleciona marcador aleatório
        m = random.choice(self.marcadores)

        # Gera pergunta com IA
        self.area.delete("all")
        self.area.pack_forget()
        self.area = tk.Frame(self, bg=COR["fundo"])
        self.area.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.area, text="Gerando pergunta...",
                 font=FONTE["corpo"], fg=COR["texto2"],
                 bg=COR["fundo"]).pack(expand=True)

        # Thread para gerar
        thread = threading.Thread(target=self._gerar_thread, args=(m,))
        thread.daemon = True
        thread.start()

    def _gerar_thread(self, m):
        try:
            pergunta = ia.quiz_dinamico(m)
            self._mostrar_pergunta(pergunta, m)
        except Exception as e:
            self._mostrar_erro(f"Erro ao gerar: {e}")

    def _mostrar_pergunta(self, p, m):
        self.area.delete("all")
        self.area.pack_forget()
        self.area = tk.Frame(self, bg=COR["fundo"])
        self.area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Progresso
        prog = tk.Frame(self.area, bg=COR["fundo"], pady=10)
        prog.pack(fill=tk.X)
        tk.Label(prog, text=f"{self.indice + 1}/{self.num_perguntas.get()}  ·  ✅ {self.acertos}",
                 font=FONTE["pequeno"], fg=COR["texto2"], bg=COR["fundo"]).pack()

        # Pergunta
        tk.Label(self.area, text=p.get("pergunta", "Pergunta?"),
                 font=FONTE["subtit"], fg=COR["texto"],
                 bg=COR["fundo"], wraplength=600, justify=tk.LEFT).pack(pady=20, anchor=tk.W)

        # Alternativas
        self.respondido = False
        self.escolha_correta = p.get("resposta_correta", 0)
        for i, alt in enumerate(p.get("alternativas", [])):
            btn = tk.Button(self.area, text=alt, bg=COR["trilha"],
                            fg=COR["texto"], relief="flat", anchor=tk.W,
                            font=FONTE["corpo"], padx=16, pady=12,
                            command=lambda i_=i: self._responder(i_, p))
            btn.pack(fill=tk.X, pady=4)
            btn.bind("<Enter>", lambda _e, b=btn: b.config(bg=COR["borda"]))
            btn.bind("<Leave>", lambda _e, b=btn: b.config(bg=COR["trilha"] if not self.respondido else b.cget("bg")))

    def _responder(self, indice, p):
        if self.respondido:
            return
        self.respondido = True
        correto = p.get("resposta_correta", 0) == indice

        if correto:
            self.acertos += 1

        # Feedback
        self.area.delete("all")
        self.area.pack_forget()
        self.area = tk.Frame(self, bg=COR["fundo"])
        self.area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        titulo = "✅ Correto!" if correto else "❌ Errado!"
        tk.Label(self.area, text=titulo,
                 font=FONTE["titulo"],
                 fg=COR["sucesso_dark"] if correto else COR["erro_dark"],
                 bg=COR["fundo"]).pack()

        tk.Label(self.area, text=p.get("explicacao", ""),
                 font=FONTE["corpo"], fg=COR["texto"],
                 bg=COR["fundo"], wraplength=600,
                 justify=tk.LEFT).pack(pady=20, anchor=tk.W)

        self.indice += 1
        tk.Button(self.area, text="Próxima" if self.indice < self.num_perguntas.get() else "Resultado",
                  bg=COR["primaria"], fg=COR["branco"],
                  relief="flat", font=FONTE["botao_g"],
                  command=self._gerar_proxima, padx=30, pady=12).pack()

    def _resultado(self):
        self.area.delete("all")
        self.area.pack_forget()
        self.area = tk.Frame(self, bg=COR["fundo"])
        self.area.pack(fill=tk.BOTH, expand=True)

        pct = (self.acertos / self.num_perguntas.get() * 100) if self.num_perguntas.get() else 0

        centro = tk.Frame(self.area, bg=COR["fundo"])
        centro.pack(expand=True)

        tk.Label(centro, text="🏆 Resultado",
                 font=FONTE["titulo"], fg=COR["texto"],
                 bg=COR["fundo"]).pack(pady=20)
        tk.Label(centro, text=f"{self.acertos}/{self.num_perguntas.get()} corretas",
                 font=FONTE["subtit"], fg=COR["texto2"],
                 bg=COR["fundo"]).pack()
        tk.Label(centro, text=f"{pct:.0f}%",
                 font=("Segoe UI", 48, "bold"),
                 fg=COR["primaria"], bg=COR["fundo"]).pack(pady=20)

        tk.Button(centro, text="Novo Quiz", bg=COR["primaria"],
                  fg=COR["branco"], relief="flat",
                  font=FONTE["botao_g"],
                  command=self._tela_config, padx=30, pady=12).pack(pady=10)
        tk.Button(centro, text="Voltar", bg=COR["trilha"],
                  fg=COR["texto"], relief="flat",
                  font=FONTE["botao_g"],
                  command=lambda: self.controller.mostrar("inicio"), padx=30, pady=12).pack()

    def _mostrar_erro(self, msg):
        self.area.delete("all")
        self.area.pack_forget()
        self.area = tk.Frame(self, bg=COR["fundo"])
        self.area.pack(fill=tk.BOTH, expand=True)
        centro = tk.Frame(self.area, bg=COR["fundo"])
        centro.pack(expand=True)
        tk.Label(centro, text="❌ " + msg,
                 font=FONTE["corpo"], fg=COR["erro"],
                 bg=COR["fundo"], wraplength=400).pack(pady=20)
        tk.Button(centro, text="Voltar", bg=COR["trilha"],
                  fg=COR["texto"], relief="flat", font=FONTE["botao_g"],
                  command=self._tela_config, padx=30, pady=12).pack()

# ─────────────────────────────────────────────
# TELA INICIAL MODIFICADA
# ─────────────────────────────────────────────
class TelaInicialEnhanced(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=COR["fundo"])
        self.controller = controller
        self._construir()

    def _construir(self):
        topo = tk.Frame(self, bg=COR["topo"], height=80)
        topo.pack(fill=tk.X)
        topo.pack_propagate(False)

        tk.Label(topo, text="⚗", font=("Segoe UI", 28),
                 fg=COR["primaria"], bg=COR["topo"]).pack(side=tk.LEFT, padx=20)
        tk.Label(topo, text="BioquímicaEDU + IA",
                 font=FONTE["titulo"], fg=COR["branco"],
                 bg=COR["topo"]).pack(side=tk.LEFT, padx=5)
        tk.Label(topo, text="com Chat Integrado & Quiz Dinâmico",
                 font=FONTE["pequeno"], fg=COR["texto2"],
                 bg=COR["topo"]).pack(side=tk.LEFT, padx=20)

        centro = tk.Frame(self, bg=COR["fundo"])
        centro.pack(expand=True, padx=40)

        grid = tk.Frame(centro, bg=COR["fundo"])
        grid.pack(pady=20)

        # Card 1: Estudo com Chat
        c1 = tk.Frame(grid, bg=COR["primaria_light"], width=220, height=180,
                      relief="solid", bd=1)
        c1.grid(row=0, column=0, padx=10, pady=10)
        c1.pack_propagate(False)
        tk.Label(c1, text="📚  Estudo + Chat",
                 font=FONTE["subtit"], fg=COR["primaria_dark"],
                 bg=COR["primaria_light"]).pack(pady=10)
        tk.Label(c1, text="Explore marcadores\nCom IA para tirar dúvidas",
                 font=FONTE["pequeno"], fg=COR["texto2"],
                 bg=COR["primaria_light"], justify=tk.CENTER).pack(pady=10)
        tk.Button(c1, text="Abrir", bg=COR["primaria"], fg=COR["branco"],
                  relief="flat", font=FONTE["botao"],
                  command=lambda: self.controller.mostrar("estudo_enhanced"),
                  padx=20, pady=8).pack()

        # Card 2: Quiz Dinâmico
        c2 = tk.Frame(grid, bg=COR["cobalto_light"], width=220, height=180,
                      relief="solid", bd=1)
        c2.grid(row=0, column=1, padx=10, pady=10)
        c2.pack_propagate(False)
        tk.Label(c2, text="🧠  Quiz Dinâmico",
                 font=FONTE["subtit"], fg=COR["cobalto_dark"],
                 bg=COR["cobalto_light"]).pack(pady=10)
        tk.Label(c2, text="Perguntas geradas\npela IA infinitamente",
                 font=FONTE["pequeno"], fg=COR["texto2"],
                 bg=COR["cobalto_light"], justify=tk.CENTER).pack(pady=10)
        tk.Button(c2, text="Abrir", bg=COR["cobalto"], fg=COR["branco"],
                  relief="flat", font=FONTE["botao"],
                  command=lambda: self.controller.mostrar("quiz_dinamico"),
                  padx=20, pady=8).pack()

        # Nota
        nota = tk.Frame(centro, bg=COR["indicador_light"], relief="solid", bd=1)
        nota.pack(fill=tk.X, pady=20)
        tk.Label(nota,
                 text=f"🤖 Status IA: {'✅ Ollama Conectado' if IA_DISPONIVEL else '⚠️ Ollama offline (modo básico)'}",
                 font=FONTE["corpo"], fg=COR["indicador_dark"],
                 bg=COR["indicador_light"]).pack(padx=16, pady=12)

# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────
class AppEnhanced(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BioquímicaEDU Enhanced — Estudo + IA")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(bg=COR["fundo"])

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
            ("inicio", TelaInicialEnhanced),
            ("estudo_enhanced", TelaEstudoEnhanced),
            ("quiz_dinamico", TelaQuizDinamico),
        ]:
            tela = Classe(self, self)
            tela.place(relwidth=1, relheight=1)
            self.telas[nome] = tela

    def mostrar(self, nome):
        if nome in ("estudo_enhanced", "quiz_dinamico"):
            if nome in self.telas:
                self.telas[nome].destroy()
            Classe = {"estudo_enhanced": TelaEstudoEnhanced,
                     "quiz_dinamico": TelaQuizDinamico}[nome]
            tela = Classe(self, self)
            tela.place(relwidth=1, relheight=1)
            self.telas[nome] = tela

        self.telas[nome].tkraise()

if __name__ == "__main__":
    print("BioquímicaEDU Enhanced — Iniciando...")
    print(f"Status IA: {'✅ Ollama disponível' if IA_DISPONIVEL else '⚠️ Ollama offline'}")
    app = AppEnhanced()
    app.mainloop()
