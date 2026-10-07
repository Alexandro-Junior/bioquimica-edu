#!/usr/bin/env python3
"""
Teste de regressão das versões desktop (main.py e main_enhanced.py).

Abre cada tela das duas versões e o detalhe de um marcador com todas as
abas, resolve todos os casos clínicos e faz um Quiz Dinâmico inteiro.
Falha se alguma tela levantar exceção, inclusive erros que o Tk só
reporta em segundo plano (callbacks e comandos agendados).

O teste grava numa pasta temporária própria (BIOQ_PASTA_ALUNO), então
o progresso real (data/progresso.json) nunca é tocado — nem se o teste
for interrompido no meio.

Uso:  python test_desktop.py
"""

import os
import shutil
import sys
import tempfile
import time
import traceback

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)
PASTA_TESTE = tempfile.mkdtemp(prefix="bioquimicaedu_teste_desktop_")
os.environ["BIOQ_PASTA_ALUNO"] = PASTA_TESTE   # antes de importar progresso
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

VERSOES = (
    ("main", ["inicio", "revisao", "estudo", "flashcards", "quiz", "diagnostico"]),
    ("main_enhanced", ["inicio", "estudo", "flashcards", "quiz", "diagnostico",
                       "estudo_enhanced", "quiz_dinamico"]),
)
ABAS = ("info", "fontes", "videos", "exemplos", "imagens")


def processar(app, segundos=0.0):
    """Roda o laço do Tk por um tempo, como se o usuário esperasse."""
    fim = time.monotonic() + segundos
    while True:
        app.update()
        if time.monotonic() >= fim:
            return
        time.sleep(0.02)


def vigiar_erros(app, falhas, modulo):
    """Transforma erros de segundo plano do Tk em falhas do teste.

    Sem isto, uma exceção dentro de um callback (clique, after) só vira
    um traceback impresso, e o teste passaria mesmo assim.
    """
    def callback(exc, valor, tb):
        falhas.append(f"{modulo}:callback")
        print(f"FALHA  {modulo}: erro em callback: {exc.__name__}: {valor}")
        traceback.print_exception(exc, valor, tb)

    def bgerror(mensagem, *_):
        falhas.append(f"{modulo}:bgerror")
        print(f"FALHA  {modulo}: erro de segundo plano do Tk: {mensagem}")

    app.report_callback_exception = callback
    app.tk.createcommand("bgerror", bgerror)


def testar_casos(app, modulo, falhas):
    """Abre e responde cada caso clínico; confere o exame qualitativo."""
    app.mostrar("diagnostico")
    tela = app.telas["diagnostico"]
    for caso in tela.casos:
        tela._abrir(caso)
        processar(app)
        tela._verificar_diag(caso["resposta_correta"], caso)
        processar(app)
    # cetonas "MASSIVAS" não podem aparecer como BAIXO (ordem alfabética)
    caso = next(c for c in tela.casos if "Cetonas" in c["exames"])
    tela._abrir(caso)
    processar(app)
    textos = []
    pilha = [tela]
    while pilha:
        w = pilha.pop()
        pilha.extend(w.winfo_children())
        if w.winfo_class() == "Label":
            textos.append(w.cget("text"))
    if "ALTERADO" not in textos:
        raise AssertionError("exame qualitativo (cetonas) sem o status ALTERADO")
    print(f"ok     {modulo}: {len(tela.casos)} casos clínicos resolvidos")


def testar_quiz_dinamico(app, modulo):
    """Faz um quiz inteiro. Sem Ollama, a pergunta vem da base offline."""
    if sys.modules[modulo].ia is None:
        print(f"pulado {modulo}: quiz dinâmico (módulo de IA não carregou; "
              "instale o requests)")
        return
    app.mostrar("quiz_dinamico")
    tela = app.telas["quiz_dinamico"]
    tela.num_perguntas.set(5)
    tela._iniciar()
    for _ in range(5):
        prazo = time.monotonic() + 10
        while not any(w.winfo_class() == "Button" for w in tela.area.winfo_children()):
            if time.monotonic() > prazo:
                raise AssertionError("pergunta do quiz dinâmico não apareceu")
            processar(app, 0.05)
        botoes = [w for w in tela.area.winfo_children() if w.winfo_class() == "Button"]
        botoes[0].invoke()          # responde
        processar(app)
        tela.area.winfo_children()[-1].invoke()  # "Próxima" / "Resultado"
        processar(app)
    if tela.indice != 5:
        raise AssertionError(f"quiz dinâmico parou na pergunta {tela.indice}")
    print(f"ok     {modulo}: quiz dinâmico completo")


def testar_versao(modulo, telas, falhas):
    mod = __import__(modulo)
    Classe = getattr(mod, "App", None) or mod.AppEnhanced
    app = Classe()
    vigiar_erros(app, falhas, modulo)
    app.update()

    for nome in telas:
        try:
            app.mostrar(nome)
            app.update_idletasks()
            app.update()
            print(f"ok     {modulo}: {nome}")
        except Exception as e:
            falhas.append(f"{modulo}:{nome}")
            print(f"FALHA  {modulo}: {nome}: {type(e).__name__}: {e}")
            traceback.print_exc()

    # potássio tem conteúdo em todas as abas do detalhe
    try:
        app.mostrar("estudo")
        tela = app.telas["estudo"]
        m = next(x for x in tela.marcadores if x["sigla"] == "K")
        tela._detalhe(m)
        for aba in ABAS:
            tela.aba_atual.set(aba)
            tela._atualizar_detalhe(m)
            app.update_idletasks()
            app.update()
        print(f"ok     {modulo}: detalhe K, {len(ABAS)} abas")
    except Exception as e:
        falhas.append(f"{modulo}:detalhe")
        print(f"FALHA  {modulo}: detalhe: {type(e).__name__}: {e}")
        traceback.print_exc()

    extras = [("casos", lambda: testar_casos(app, modulo, falhas))]
    if "quiz_dinamico" in telas:
        extras.append(("quiz_dinamico", lambda: testar_quiz_dinamico(app, modulo)))
    if modulo == "main":
        def rolagem_depois_de_sair():
            # entrar no painel liga a roda do mouse; sair sem <Leave>
            # (clique num atalho) não pode deixá-la presa ao canvas morto
            app.mostrar("inicio")
            app.telas["inicio"]._ligar_rolagem()
            app.mostrar("estudo")
            app.event_generate("<MouseWheel>", delta=-120, when="now")
            processar(app)
            print(f"ok     {modulo}: rolagem depois de sair do painel")
        extras.append(("rolagem", rolagem_depois_de_sair))

    for nome, teste in extras:
        try:
            teste()
        except Exception as e:
            falhas.append(f"{modulo}:{nome}")
            print(f"FALHA  {modulo}: {nome}: {type(e).__name__}: {e}")
            traceback.print_exc()

    # deixa as animações e agendamentos pendentes dispararem: um comando
    # Tcl apagado junto com a tela anterior apareceria aqui como bgerror
    processar(app, 1.2)
    app.destroy()


def main():
    falhas = []
    try:
        for modulo, telas in VERSOES:
            testar_versao(modulo, telas, falhas)
    finally:
        shutil.rmtree(PASTA_TESTE, ignore_errors=True)

    print("TODAS AS TELAS ABRIRAM" if not falhas else f"{len(falhas)} falha(s): {falhas}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
