"""
BioquímicaEDU — Versão Enhanced com IA Integrada
Desktop (Tkinter) + Chat Local (Ollama) + Quiz Dinâmico

Todas as funcionalidades:
- 20 marcadores com filtros
- Chat inteligente sobre marcadores
- Quiz dinâmico gerado por IA
- 100% privado (Ollama local)
"""

import tkinter as tk
import queue
import random
import threading

# Importa módulo de IA
try:
    from ollama_ia import ia
    IA_DISPONIVEL = ia.disponivel
except ImportError as e:
    # sem o módulo (ou sem o requests) não há nem o modo offline do tutor
    print(f"⚠️ Módulo de IA indisponível ({e}). Chat e quiz dinâmico desativados.")
    ia = None
    IA_DISPONIVEL = False

AVISO_SEM_MODULO_IA = ("O módulo de IA não pôde ser carregado. Instale as "
                       "dependências com:  pip install -r requirements.txt")


def em_segundo_plano(widget, tarefa, ao_terminar):
    """Roda `tarefa()` numa thread e entrega o resultado na thread do Tk.

    O Tkinter não é seguro entre threads: mexer em widgets fora da thread
    principal pode travar ou derrubar o app. A thread só calcula; quem
    desenha é `ao_terminar(resultado, erro)`, chamado pelo laço do Tk.
    Se a tela for fechada antes da resposta, o resultado é descartado.
    """
    fila = queue.Queue(maxsize=1)
    # O agendamento fica na janela principal: se ficasse no widget e a tela
    # fosse fechada antes da resposta, o Tk tentaria rodar um comando já
    # apagado junto com ela.
    raiz = widget.winfo_toplevel()

    def trabalhar():
        try:
            fila.put((tarefa(), None))
        except Exception as e:  # o erro vira mensagem na tela, não traceback
            fila.put((None, e))

    def conferir():
        if not widget.winfo_exists():
            return
        try:
            resultado, erro = fila.get_nowait()
        except queue.Empty:
            raiz.after(100, conferir)
            return
        ao_terminar(resultado, erro)

    threading.Thread(target=trabalhar, daemon=True).start()
    raiz.after(100, conferir)


# Telas completas reaproveitadas da versão desktop.
# Assim esta versão herda flashcards, diagnóstico, imagens e fontes sem
# duplicar código: o que se corrige em main.py vale aqui também.
from main import (
    COR,
    FONTE,
    carregar_marcadores,
    TelaEstudo as TelaEstudoCompleta,
    TelaFlashcards as TelaFlashcardsCompleta,
    TelaQuiz as TelaQuizCompleto,
    TelaDiagnostico as TelaDiagnosticoCompleto,
)

# ─────────────────────────────────────────────
# WIDGET DE CHAT
# ─────────────────────────────────────────────
class PainelChat(tk.Frame):
    def __init__(self, parent, marcador=None, **kwargs):
        super().__init__(parent, bg=COR["superficie"], **kwargs)
        self.marcador = marcador

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

        if ia is None:
            self._adicionar_msg_ia(AVISO_SEM_MODULO_IA)
            return

        def mostrar(resposta, erro):
            if erro is not None:
                resposta = (f"❌ Erro: {erro}\n\nTente novamente ou verifique "
                            "se o Ollama está rodando.")
            self._adicionar_msg_ia(resposta)

        em_segundo_plano(self, lambda: self._gerar_resposta(pergunta), mostrar)

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
        """Consulta a IA. Roda fora da thread do Tk: não toca em widgets."""
        nome = self.marcador.get("nome", "Marcador") if self.marcador else "Marcador"
        return ia.chat_marcador(nome, pergunta, callback=None)

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
        self.busca_var.trace_add("write", lambda *_: self._filtrar())
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

    def _nova_area(self, **pack):
        """Troca a área de conteúdo por uma vazia.

        A área anterior é destruída (e não só escondida), senão cada
        pergunta deixaria um frame órfão acumulando na memória.
        """
        self.area.destroy()
        self.area = tk.Frame(self, bg=COR["fundo"])
        self.area.pack(fill=tk.BOTH, expand=True, **pack)
        return self.area

    def _iniciar(self):
        self.perguntas_geradas = []
        self.indice = 0
        self.acertos = 0
        self._gerar_proxima()

    def _gerar_proxima(self):
        if self.indice >= self.num_perguntas.get():
            self._resultado()
            return

        if ia is None:
            self._mostrar_erro(AVISO_SEM_MODULO_IA)
            return
        if not self.marcadores:
            self._mostrar_erro("Nenhum marcador carregado de data/marcadores.csv")
            return

        # Seleciona marcador aleatório
        m = random.choice(self.marcadores)

        # Gera pergunta com IA
        self._nova_area()
        tk.Label(self.area, text="Gerando pergunta...",
                 font=FONTE["corpo"], fg=COR["texto2"],
                 bg=COR["fundo"]).pack(expand=True)

        def mostrar(pergunta, erro):
            if erro is not None:
                self._mostrar_erro(f"Erro ao gerar: {erro}")
            else:
                self._mostrar_pergunta(pergunta, m)

        em_segundo_plano(self, lambda: ia.quiz_dinamico(m), mostrar)

    def _mostrar_pergunta(self, p, m):
        self._nova_area(padx=20, pady=10)

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
        self._nova_area(padx=20, pady=20)

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
        self._nova_area()

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
        self._nova_area()
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
        topo = tk.Frame(self, bg=COR["topo"], height=84)
        topo.pack(fill=tk.X)
        topo.pack_propagate(False)

        tk.Label(topo, text="⚗", font=("Segoe UI", 28),
                 fg=COR["primaria"], bg=COR["topo"]).pack(side=tk.LEFT, padx=20)
        titulos = tk.Frame(topo, bg=COR["topo"])
        titulos.pack(side=tk.LEFT)
        tk.Label(titulos, text="BioquimicaEDU + IA",
                 font=FONTE["titulo"], fg=COR["texto"],
                 bg=COR["topo"]).pack(anchor=tk.W)
        tk.Label(titulos, text="Todos os modos de estudo, com tutor local opcional",
                 font=FONTE["pequeno"], fg=COR["texto2"],
                 bg=COR["topo"]).pack(anchor=tk.W)

        centro = tk.Frame(self, bg=COR["fundo"])
        centro.pack(expand=True, padx=40)

        grid = tk.Frame(centro, bg=COR["fundo"])
        grid.pack(pady=10)

        modos = [
            ("📚  Estudo", "20 marcadores com fontes,\nexemplos e imagens",
             "primaria", "estudo"),
            ("🎴  Flashcards", "Cards de revisao rapida",
             "bile", "flashcards"),
            ("🧠  Quiz", "Perguntas com explicacao",
             "cobalto", "quiz"),
            ("🩺  Diagnostico", "Casos clinicos para interpretar",
             "indicador", "diagnostico"),
            ("💬  Estudo + Chat", "Tire duvidas com o tutor\nlocal (Ollama)",
             "primaria", "estudo_enhanced"),
            ("✨  Quiz Dinamico", "Perguntas geradas pela IA",
             "sangue", "quiz_dinamico"),
        ]

        for i, (titulo, descricao, cor, destino) in enumerate(modos):
            cartao = tk.Frame(grid, bg=COR[f"{cor}_light"], width=250, height=168,
                              relief="solid", bd=1)
            cartao.grid(row=i // 3, column=i % 3, padx=9, pady=9)
            cartao.pack_propagate(False)

            tk.Label(cartao, text=titulo, font=FONTE["subtit"],
                     fg=COR[f"{cor}_dark"], bg=COR[f"{cor}_light"]).pack(pady=(16, 6))
            tk.Label(cartao, text=descricao, font=FONTE["pequeno"],
                     fg=COR["texto2"], bg=COR[f"{cor}_light"],
                     justify=tk.CENTER).pack(pady=(0, 10))
            tk.Button(cartao, text="Abrir", bg=COR[cor], fg=COR["branco"],
                      relief="flat", font=FONTE["botao"],
                      command=lambda d=destino: self.controller.mostrar(d),
                      padx=22, pady=7).pack()

        estado = ("Ollama conectado: chat e quiz dinamico ativos"
                  if IA_DISPONIVEL else
                  "Ollama offline: os dois modos com IA respondem pela base local")
        nota = tk.Frame(centro, bg=COR["indicador_light"], relief="solid", bd=1)
        nota.pack(fill=tk.X, pady=(14, 4))
        tk.Label(nota, text=estado, font=FONTE["corpo"],
                 fg=COR["indicador_dark"], bg=COR["indicador_light"]
                 ).pack(padx=16, pady=10)


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

        # As telas reaproveitadas do main.py leem estes contadores.
        self.xp = 0
        self.streak = 0

        self.telas = {}
        self._criar_telas()

    # Telas recriadas a cada visita, para refletir XP/sequência e sortear
    # novas perguntas e casos.
    CLASSES = {
        "inicio":          TelaInicialEnhanced,
        "estudo_enhanced": TelaEstudoEnhanced,
        "quiz_dinamico":   TelaQuizDinamico,
        "estudo":          TelaEstudoCompleta,
        "flashcards":      TelaFlashcardsCompleta,
        "quiz":            TelaQuizCompleto,
        "diagnostico":     TelaDiagnosticoCompleto,
    }

    def _criar_telas(self):
        self.mostrar("inicio")

    def mostrar(self, nome):
        Classe = self.CLASSES.get(nome)
        if Classe is None:
            print(f"[navegacao] tela desconhecida: {nome}")
            return
        anterior = self.telas.pop(nome, None)
        if anterior is not None:
            anterior.destroy()
        tela = Classe(self, self)
        tela.place(relwidth=1, relheight=1)
        self.telas[nome] = tela
        tela.tkraise()

if __name__ == "__main__":
    print("BioquímicaEDU Enhanced — Iniciando...")
    print(f"Status IA: {'✅ Ollama disponível' if IA_DISPONIVEL else '⚠️ Ollama offline'}")
    app = AppEnhanced()
    app.mainloop()
