#!/usr/bin/env python3
"""
Gera as figuras e as métricas do relatório final.

- arquitetura.png      camadas do software e o que usa o quê
- sm2_intervalos.png   intervalos produzidos pelo motor real (progresso.py)
- telas_*.png          pranchas com três capturas da versão mobile cada
- desktop_painel.png   captura da versão desktop
- metricas.json        linhas de código por módulo e volume de conteúdo

As capturas usam um progresso de exemplo (estudante fictício com algumas
semanas de uso), para que o painel mostre todos os seus elementos. Ele
fica numa pasta temporária: o progresso real em data/ não é tocado.

Observação: as capturas refletem a interface atual. As figuras do relatório
mostram a versão avaliada com usuários; rode de novo só se a versão nova
também entrar no relatório.

Uso:  python relatorio/gerar_figuras.py
"""

import csv
import io
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FIG = Path(__file__).resolve().parent / "figuras"
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)
FIG.mkdir(parents=True, exist_ok=True)

VERDE = "#0E7C5A"
VERDE_SUAVE = "#E1F1EA"
AMBAR = "#C27818"
INDIGO = "#3F5C9A"
RUBRO = "#B5392F"
TINTA = "#17211C"
TINTA2 = "#5B6560"
BORDA = "#C9C3B8"
PAPEL = "#F6F4EF"


# ════════════════════════════════════════════════════════════════════
# PROGRESSO DE EXEMPLO (para as capturas)
# ════════════════════════════════════════════════════════════════════
def progresso_exemplo():
    random.seed(7)
    hoje = date.today()
    iso = lambda d: d.isoformat()

    def item(rep, fac, intervalo, prox, ultima, acertos, tentativas):
        return {"repeticoes": rep, "facilidade": fac, "intervalo": intervalo,
                "proxima_revisao": iso(hoje + timedelta(days=prox)),
                "ultima_revisao": iso(hoje - timedelta(days=ultima)),
                "acertos": acertos, "tentativas": tentativas}

    itens = {
        "ALT": item(5, 2.8, 34, 12, 22, 6, 6), "GLI": item(4, 2.7, 26, 9, 17, 5, 5),
        "CT": item(4, 2.6, 23, 4, 19, 5, 6), "CREA": item(5, 2.7, 41, 20, 21, 6, 6),
        "AST": item(3, 2.5, 15, 3, 12, 4, 5), "K": item(2, 2.36, 6, 2, 4, 3, 4),
        "HbA1c": item(3, 2.5, 14, 6, 8, 3, 4), "GGT": item(1, 2.36, 1, 0, 1, 1, 2),
        "BT": item(1, 2.18, 1, -1, 2, 1, 3), "TropI": item(1, 2.5, 1, 0, 1, 1, 1),
        "Na": item(0, 1.96, 1, 0, 1, 0, 2), "UREIA": item(1, 2.5, 1, -2, 3, 1, 1),
    }
    sessoes = []
    for i in range(27, -1, -1):
        n = 0 if i == 0 else (random.randint(3, 14) if random.random() < 0.72 else 0)
        if n:
            sessoes.append({"data": iso(hoje - timedelta(days=i)), "revisados": n,
                            "acertos": int(n * 0.75)})
    pares = [(5, True), (4, False), (5, True), (4, True), (5, False), (4, True), (5, False),
             (4, True), (5, True), (3, False), (4, False), (5, True), (4, True), (5, False)]
    calibracao = [{"data": iso(hoje - timedelta(days=d % 9)), "confianca": c, "acertou": a}
                  for d, (c, a) in enumerate(pares)]
    return {"versao": 1, "criado_em": iso(hoje - timedelta(days=30)), "itens": itens,
            "sessoes": sessoes, "calibracao": calibracao, "conquistas": []}


# ════════════════════════════════════════════════════════════════════
# MÉTRICAS
# ════════════════════════════════════════════════════════════════════
def contar_linhas(caminho):
    linhas = io.open(caminho, encoding="utf-8").read().splitlines()
    return sum(1 for l in linhas if l.strip() and not l.strip().startswith("#"))


def metricas():
    modulos = {
        "Versão desktop (main.py)": ["main.py"],
        "Painel e revisão desktop": ["painel_inicio.py", "tela_painel.py", "tela_revisao.py"],
        "Desktop com tutor (main_enhanced.py, ollama_ia.py)": ["main_enhanced.py", "ollama_ia.py"],
        "Versão mobile (mobile/)": [str(p.relative_to(RAIZ)) for p in (RAIZ / "mobile").rglob("*.py")],
        "Motor de aprendizagem (progresso.py)": ["progresso.py"],
        "Geradores (imagens, logo, ícones)": ["criar_imagens.py", "criar_logo.py"],
        "Testes automatizados": ["test_kivy_completo.py", "test_desktop.py"],
    }
    codigo = {nome: sum(contar_linhas(RAIZ / a) for a in arqs) for nome, arqs in modulos.items()}

    dados = RAIZ / "data"
    marcadores = list(csv.DictReader(io.open(dados / "marcadores.csv", encoding="utf-8")))
    extras = json.load(io.open(dados / "marcadores_extras.json", encoding="utf-8"))["marcadores_extras"]
    imagens = json.load(io.open(dados / "marcadores_imagens.json", encoding="utf-8"))["marcadores_imagens"]
    conteudo = {
        "marcadores": len(marcadores),
        "sistemas": len({m["categoria"] for m in marcadores}),
        "flashcards": len(json.load(io.open(dados / "flashcards.json", encoding="utf-8"))["flashcards"]),
        "questoes": len(json.load(io.open(dados / "quiz_perguntas.json", encoding="utf-8"))),
        "casos_clinicos": len(json.load(io.open(dados / "casos_clinicos.json", encoding="utf-8"))),
        "exemplos": sum(len(m.get("exemplos", [])) for m in extras),
        "referencias": sum(len(m.get("referencias", [])) for m in extras),
        "referencias_unicas": len({r["url"] for m in extras for r in m.get("referencias", [])}),
        "videos": sum(len(m.get("videos", [])) for m in extras),
        "diagramas": sum(len(m.get("imagens", [])) for m in imagens),
        "marcadores_com_diagrama": len(imagens),
    }
    commits = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=RAIZ,
                             capture_output=True, text=True).stdout.strip()
    saida = {"codigo": codigo, "codigo_total": sum(codigo.values()),
             "conteudo": conteudo, "commits": int(commits or 0)}
    json.dump(saida, io.open(FIG / "metricas.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("metricas.json", saida["codigo_total"], "linhas,", conteudo)
    return saida


# ════════════════════════════════════════════════════════════════════
# ARQUITETURA
# ════════════════════════════════════════════════════════════════════
def arquitetura():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig, ax = plt.subplots(figsize=(10, 6.4), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 64)
    ax.axis("off")

    def caixa(x, y, w, h, titulo, linhas, cor, fundo, tracejada=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.6",
                                    linewidth=1.4, edgecolor=cor, facecolor=fundo,
                                    linestyle=(0, (4, 3)) if tracejada else "-"))
        ax.text(x + w / 2, y + h - 2.4, titulo, ha="center", va="top", fontsize=9.6,
                fontweight="bold", color=TINTA)
        ax.text(x + w / 2, y + h - 6.0, "\n".join(linhas), ha="center", va="top",
                fontsize=7.8, color=TINTA2, linespacing=1.45)

    def faixa(y, h, rotulo):
        ax.add_patch(FancyBboxPatch((0.5, y), 99, h, boxstyle="round,pad=0,rounding_size=1.2",
                                    linewidth=0, facecolor="#F1EEE8"))
        ax.text(2.2, y + h / 2, rotulo, rotation=90, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=TINTA2)

    def seta(x1, y1, x2, y2, rotulo="", tracejada=False, deslocamento=(0, 0)):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11,
                                     linewidth=1.2, color=TINTA2,
                                     linestyle=(0, (4, 3)) if tracejada else "-",
                                     shrinkA=2, shrinkB=2))
        if rotulo:
            ax.text((x1 + x2) / 2 + deslocamento[0], (y1 + y2) / 2 + deslocamento[1], rotulo,
                    ha="center", va="center", fontsize=7.2, color=TINTA2,
                    bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none"))

    faixa(44, 19, "INTERFACES")
    faixa(23, 18.5, "NÚCLEO")
    faixa(1, 19.5, "DADOS")

    caixa(6, 46, 28, 15, "Desktop", ["main.py · Tkinter", "painel, revisão, estudo,", "cards, quiz, casos"],
          VERDE, "white")
    caixa(37.5, 46, 28, 15, "Mobile", ["mobile/ · Kivy", "Android e iOS", "5 abas + revisão"],
          VERDE, "white")
    caixa(69, 46, 28, 15, "Desktop com tutor", ["main_enhanced.py · Tkinter", "reaproveita as telas", "do main.py + chat"],
          VERDE, "white")

    caixa(14, 25, 42, 14.5, "Motor de aprendizagem — progresso.py",
          ["SM-2 adaptado · fila do dia · reforço", "calibração · domínio · marcos",
           "vínculo pergunta → marcadores"], INDIGO, "white")
    caixa(65, 25, 32, 14.5, "Tutor local — ollama_ia.py",
          ["opcional, só no computador", "sem ele: respostas pela base", "do próprio app"],
          TINTA2, "white", tracejada=True)

    caixa(6, 3, 52, 15.5, "Conteúdo — data/ (somente leitura)",
          ["marcadores.csv · flashcards · quiz · casos clínicos",
           "marcadores_extras.json (casos, fontes, vídeos)", "16 diagramas em data/images/"],
          AMBAR, "white")
    caixa(63, 3, 34, 15.5, "Progresso do estudante",
          ["progresso.json (computador)", "pasta privada do app (celular)", "nunca sai do aparelho"],
          AMBAR, "white")

    seta(20, 46, 20, 39.5)
    seta(51.5, 46, 44, 39.5)
    seta(80, 46, 53, 39.5)
    seta(86, 46, 86, 39.5, "chat", tracejada=True, deslocamento=(3.5, 0))
    seta(35, 25, 35, 18.5, "lê", deslocamento=(2.5, 0))
    seta(50, 25, 72, 18.5, "lê e grava", deslocamento=(4, 1))

    fig.savefig(FIG / "arquitetura.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("arquitetura.png")


# ════════════════════════════════════════════════════════════════════
# SM-2: COMPORTAMENTO REAL DO MOTOR
# ════════════════════════════════════════════════════════════════════
def sm2():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from progresso import Progresso

    def simular(notas):
        caminho = Path(tempfile.gettempdir()) / f"bioq_sim_{random.random()}.json"
        p = Progresso(caminho)
        intervalos = [p.registrar_resposta("X", q)["intervalo"] for q in notas]
        if caminho.exists():
            caminho.unlink()
        return intervalos

    cenarios = [
        ("Sempre “Bom” (nota 4)", [4] * 6, VERDE, "o"),
        ("Sempre “Fácil” (nota 5)", [5] * 6, INDIGO, "s"),
        ("“Bom”, com um erro na 4ª revisão", [4, 4, 4, 1, 4, 4], RUBRO, "^"),
    ]
    resultados = {}
    fig, ax = plt.subplots(figsize=(8, 4.4), dpi=300)
    for rotulo, notas, cor, marca in cenarios:
        intervalos = simular(notas)
        resultados[rotulo] = intervalos
        x = list(range(1, len(intervalos) + 1))
        ax.plot(x, intervalos, marker=marca, color=cor, linewidth=2, markersize=6, label=rotulo)
        ax.annotate(f"{intervalos[-1]} d", (x[-1], intervalos[-1]), textcoords="offset points",
                    xytext=(8, -3), fontsize=8, color=cor, fontweight="bold")
    ax.set_yscale("log")
    ax.set_yticks([1, 2, 4, 7, 15, 30, 60, 120, 240])
    ax.set_yticklabels(["1", "2", "4", "7", "15", "30", "60", "120", "240"])
    ax.set_xticks(range(1, 7))
    ax.set_xlabel("Revisão de um mesmo marcador", fontsize=9.5)
    ax.set_ylabel("Dias até a próxima revisão (escala log.)", fontsize=9.5)
    ax.grid(True, which="major", color="#E6E1D8", linewidth=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(labelsize=8.5)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    ax.set_xlim(0.7, 6.6)
    fig.tight_layout()
    fig.savefig(FIG / "sm2_intervalos.png", dpi=300, facecolor="white")
    plt.close(fig)
    json.dump(resultados, io.open(FIG / "sm2_intervalos.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("sm2_intervalos.png", resultados)


# ════════════════════════════════════════════════════════════════════
# CAPTURAS
# ════════════════════════════════════════════════════════════════════
def capturas_mobile():
    """Abre o app mobile, captura as telas e monta as pranchas."""
    pasta = Path(tempfile.mkdtemp(prefix="bioq_telas_"))
    roteiro = f'''
import sys, os
sys.path.insert(0, r"{RAIZ}")
os.chdir(r"{RAIZ}")
from kivy.clock import Clock
from kivy.core.window import Window
import main_kivy_completo as M
app = M.BioquimicaApp()
OUT = r"{pasta}"
passos = []
t = [6.0]
def p(fn, foto=None, espera=1.3):
    passos.append((t[0], fn, foto)); t[0] += espera
def tela(): return app.tela_atual()
p(lambda: (app.casos_resolvidos.update({{1, 3, 4}}), app.ir_para("inicio", animar=False)), "inicio")
p(lambda: app.ir_para("estudo", animar=False), "estudo")
p(lambda: app.ir_para("detalhe", sigla="K", animar=False), "detalhe")
p(lambda: tela().mostrar_aba("casos"), "detalhe_casos")
p(lambda: app.ir_para("revisao", animar=False), "revisao_pergunta")
p(lambda: (tela()._definir_confianca(4), tela()._revelar()), "revisao_resposta", 1.6)
p(lambda: app.ir_para("cartas", animar=False), "cards_pergunta")
p(lambda: tela()._virar(), "cards_resposta")
p(lambda: (app.ir_para("pratica", animar=False), tela().iniciar_quiz()), "quiz")
def responder():
    q = tela().perguntas[0]
    tela().responder_quiz((q["resposta_correta"] + 1) % len(q["alternativas"]), q)
p(responder, "quiz_feedback")
p(lambda: (tela().trocar_modo("casos"), tela().abrir_caso(app.casos[3])), "caso")
p(lambda: (app.ir_para("tutor", animar=False), tela()._perguntar("Potássio alto")), "tutor", 1.8)
def agendar(momento, fn, foto):
    def rodar(_dt):
        fn()
        if foto:
            Clock.schedule_once(lambda _d: Window.screenshot(name=os.path.join(OUT, foto + ".png")), 0.9)
    Clock.schedule_once(rodar, momento)
for momento, fn, foto in passos:
    agendar(momento, fn, foto)
Clock.schedule_once(lambda _dt: app.stop(), t[0] + 1.5)
app.run()
'''
    r = subprocess.run([sys.executable, "-c", roteiro], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    capturas = {p.stem.rsplit("0001", 1)[0]: p for p in pasta.glob("*.png")}
    if len(capturas) < 12:
        print(r.stderr[-3000:])
        raise RuntimeError(f"capturas incompletas: {sorted(capturas)}")

    pranchas = {
        "telas_inicio_estudo": ["inicio", "estudo", "detalhe"],
        "telas_revisao": ["revisao_pergunta", "revisao_resposta", "cards_resposta"],
        "telas_pratica_tutor": ["quiz_feedback", "caso", "tutor"],
    }
    for nome, telas in pranchas.items():
        prancha(nome, [capturas[t] for t in telas])
    shutil.rmtree(pasta, ignore_errors=True)


def prancha(nome, arquivos):
    """Três telas lado a lado, com cantos arredondados e rótulos (a), (b), (c)."""
    from PIL import Image, ImageDraw, ImageFont
    from kivy import kivy_data_dir

    telas = [Image.open(a).convert("RGB") for a in arquivos]
    w, h = telas[0].size
    vao, margem, rotulo_h = 60, 30, 80
    largura = margem * 2 + w * 3 + vao * 2
    altura = margem * 2 + h + rotulo_h
    folha = Image.new("RGB", (largura, altura), "white")
    fonte = ImageFont.truetype(os.path.join(kivy_data_dir, "fonts", "Roboto-Bold.ttf"), 34)
    d = ImageDraw.Draw(folha)
    for i, tela in enumerate(telas):
        x = margem + i * (w + vao)
        mascara = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mascara).rounded_rectangle((0, 0, w - 1, h - 1), radius=38, fill=255)
        folha.paste(tela, (x, margem), mascara)
        d.rounded_rectangle((x - 1, margem - 1, x + w, margem + h), radius=39,
                            outline=BORDA, width=3)
        letra = f"({'abc'[i]})"
        tw = d.textlength(letra, font=fonte)
        d.text((x + (w - tw) / 2, margem + h + 22), letra, font=fonte, fill=TINTA)
    folha.save(FIG / f"{nome}.png", dpi=(300, 300))
    print(f"{nome}.png")


def captura_desktop():
    """Painel inicial da versão desktop, com o mesmo progresso de exemplo.

    A captura simula uma tela a 100%: o processo declara reconhecer DPI
    (para a imagem sair nítida) e o Tk é fixado em 96 DPI, que é como o
    app se desenha em qualquer tela sem essa declaração.
    """
    roteiro = f'''
import sys, os, time, ctypes, tkinter
sys.path.insert(0, r"{RAIZ}")
os.chdir(r"{RAIZ}")
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass
_init = tkinter.Tk.__init__
def _init_96dpi(self, *a, **k):
    _init(self, *a, **k)
    self.tk.call("tk", "scaling", 96 / 72)
tkinter.Tk.__init__ = _init_96dpi
import main as M
from PIL import ImageGrab
app = M.App()
app.geometry("1100x760+60+40")
def bombear(s):
    fim = time.time() + s
    while time.time() < fim:
        app.update_idletasks(); app.update(); time.sleep(0.02)
bombear(1.5)
app.lift(); app.attributes("-topmost", True); bombear(1.6)
x, y = app.winfo_rootx(), app.winfo_rooty()
w, h = app.winfo_width(), app.winfo_height()
ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(r"{FIG / 'desktop_painel.png'}")
app.destroy()
print("desktop_painel.png", w, h)
'''
    r = subprocess.run([sys.executable, "-c", roteiro], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180)
    print(r.stdout.strip() or r.stderr[-1500:])


def main():
    # O progresso de exemplo vai para uma pasta temporária (BIOQ_PASTA_ALUNO,
    # herdada pelos processos de captura): o progresso real do estudante em
    # data/ nunca é tocado, nem se a geração for interrompida no meio.
    pasta = Path(tempfile.mkdtemp(prefix="bioq_figuras_"))
    os.environ["BIOQ_PASTA_ALUNO"] = str(pasta)
    exemplo = pasta / "progresso.json"
    with io.open(pasta / "preferencias_mobile.json", "w", encoding="utf-8") as f:
        json.dump({"boas_vindas_vista": True}, f)   # capturas sem a apresentação
    try:
        json.dump(progresso_exemplo(), io.open(exemplo, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        metricas()
        arquitetura()
        sm2()
        capturas_mobile()
        # o quiz da captura mobile registra uma resposta; recomeça do exemplo
        json.dump(progresso_exemplo(), io.open(exemplo, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        captura_desktop()
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


if __name__ == "__main__":
    main()
