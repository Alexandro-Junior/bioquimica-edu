#!/usr/bin/env python3
"""Validação rápida do BioquímicaEDU: dependências, dados e versão mobile.

Não abre janela. Confere se o Kivy está instalado, se as telas da versão
mobile importam e se os arquivos de data/ estão íntegros — inclusive o
que um JSON válido não garante, como a resposta correta de um caso estar
entre as alternativas oferecidas.

Para abrir o app de verdade e usar cada tela:  python test_kivy_completo.py

Uso:  python test_simple.py
Sai com código 0 se tudo passar e 1 se algo falhar.
"""

import csv
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
sys.path.insert(0, str(BASE_DIR))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def ler_json(nome):
    with open(DATA_DIR / nome, encoding="utf-8") as f:
        return json.load(f)


def verificar_dados(erros):
    with open(DATA_DIR / "marcadores.csv", encoding="utf-8") as f:
        marcadores = list(csv.DictReader(f))
    siglas = {m["sigla"] for m in marcadores}
    for m in marcadores:
        try:
            if float(m["valor_ref_min"]) > float(m["valor_ref_max"]):
                erros.append(f"marcadores.csv: {m['sigla']} com mínimo acima do máximo")
        except ValueError:
            erros.append(f"marcadores.csv: {m['sigla']} com faixa não numérica")
    print(f"    marcadores.csv: {len(marcadores)} marcadores")

    cards = ler_json("flashcards.json")["flashcards"]
    for i, c in enumerate(cards, 1):
        if not (c.get("pergunta") and c.get("resposta")):
            erros.append(f"flashcards.json: card {i} sem pergunta ou resposta")
    print(f"    flashcards.json: {len(cards)} cards")

    quiz = ler_json("quiz_perguntas.json")
    for i, p in enumerate(quiz, 1):
        alternativas = p.get("alternativas", [])
        if not 0 <= p.get("resposta_correta", -1) < len(alternativas):
            erros.append(f"quiz_perguntas.json: pergunta {i} com resposta fora das alternativas")
    print(f"    quiz_perguntas.json: {len(quiz)} perguntas")

    casos = ler_json("casos_clinicos.json")
    for caso in casos:
        nome = caso.get("titulo", "?")
        if caso.get("resposta_correta") not in caso.get("alternativas", []):
            # sem isso o caso é impossível de acertar
            erros.append(f"casos_clinicos.json: '{nome}' — resposta correta "
                         "não está entre as alternativas")
        for exame, d in caso.get("exames", {}).items():
            faltando = {"valor", "unidade", "ref_min", "ref_max"} - d.keys()
            if faltando:
                erros.append(f"casos_clinicos.json: '{nome}' / {exame} sem {sorted(faltando)}")
    print(f"    casos_clinicos.json: {len(casos)} casos")

    for arquivo, chave in (("marcadores_extras.json", "marcadores_extras"),
                           ("marcadores_imagens.json", "marcadores_imagens")):
        for item in ler_json(arquivo)[chave]:
            if item["sigla"] not in siglas:
                erros.append(f"{arquivo}: sigla {item['sigla']} não existe no CSV")
    for item in ler_json("marcadores_imagens.json")["marcadores_imagens"]:
        for img in item["imagens"]:
            if not (DATA_DIR / "images" / img["arquivo"]).exists():
                erros.append(f"imagem ausente: data/images/{img['arquivo']}")
    for item in ler_json("marcadores_extras.json")["marcadores_extras"]:
        for link in item.get("referencias", []) + item.get("videos", []):
            if not link.get("url", "").startswith("https://"):
                erros.append(f"marcadores_extras.json: {item['sigla']} com link não https")
    print("    extras e imagens: conferidos")


def main():
    erros = []
    print("\n[1] Kivy e versão mobile")
    try:
        from mobile.app import BioquimicaApp as App
        faltando = [n for n in ("inicio", "estudo", "detalhe", "cartas",
                                "pratica", "revisao", "tutor") if n not in App.TELAS]
        if faltando:
            erros.append(f"telas mobile ausentes: {faltando}")
        print(f"    OK: {len(App.TELAS)} telas registradas")
    except ImportError as e:
        erros.append(f"não foi possível importar a versão mobile: {e}")

    print("\n[2] Arquivos de dados")
    try:
        verificar_dados(erros)
    except (OSError, ValueError, KeyError) as e:
        erros.append(f"falha ao ler data/: {type(e).__name__}: {e}")

    print()
    for erro in erros:
        print(f"ERRO   {erro}")
    print("TUDO CERTO" if not erros else f"{len(erros)} problema(s) encontrado(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
