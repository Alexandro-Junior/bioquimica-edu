#!/usr/bin/env python3
"""
Teste de regressão das versões desktop (main.py e main_enhanced.py).

Abre cada tela das duas versões e o detalhe de um marcador com todas as
abas. Falha se alguma tela levantar exceção ao ser montada.

O progresso real (data/progresso.json) é salvo antes e restaurado no
final, então rodar o teste não mexe no estudo de ninguém.

Uso:  python test_desktop.py
"""

import os
import shutil
import sys
import tempfile
import traceback

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)
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


def testar_versao(modulo, telas, falhas):
    mod = __import__(modulo)
    Classe = getattr(mod, "App", None) or getattr(mod, "AppEnhanced")
    app = Classe()
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

    app.destroy()


def main():
    real = os.path.join(RAIZ, "data", "progresso.json")
    copia = os.path.join(tempfile.gettempdir(), "bioquimica_progresso_teste.json")
    existia = os.path.exists(real)
    if existia:
        shutil.copy(real, copia)

    falhas = []
    try:
        for modulo, telas in VERSOES:
            testar_versao(modulo, telas, falhas)
    finally:
        if existia:
            shutil.copy(copia, real)
        elif os.path.exists(real):
            os.remove(real)

    print("TODAS AS TELAS ABRIRAM" if not falhas else f"{len(falhas)} falha(s): {falhas}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
