"""Leitura dos arquivos de conteúdo em data/.

Toda falha de leitura devolve uma coleção vazia e registra o motivo: o
app abre mesmo com um arquivo faltando, e a tela afetada mostra um
estado vazio em vez de fechar.
"""

import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMG_DIR = DATA_DIR / "images"


def _ler_json(nome, padrao):
    try:
        with open(DATA_DIR / nome, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[dados] falha ao ler {nome}: {e}")
        return padrao


def carregar_marcadores():
    marcadores = []
    try:
        with open(DATA_DIR / "marcadores.csv", encoding="utf-8") as f:
            for linha in csv.DictReader(f):
                try:
                    linha["valor_ref_min"] = float(linha["valor_ref_min"])
                    linha["valor_ref_max"] = float(linha["valor_ref_max"])
                except (TypeError, ValueError):
                    continue
                marcadores.append(linha)
    except OSError as e:
        print(f"[dados] falha ao ler marcadores.csv: {e}")
    return marcadores


def carregar_flashcards():
    return _ler_json("flashcards.json", {}).get("flashcards", [])


def carregar_extras():
    dados = _ler_json("marcadores_extras.json", {})
    return {m["sigla"]: m for m in dados.get("marcadores_extras", [])}


def carregar_imagens():
    dados = _ler_json("marcadores_imagens.json", {})
    return {m["sigla"]: m for m in dados.get("marcadores_imagens", [])}


def carregar_quiz():
    return _ler_json("quiz_perguntas.json", [])


def carregar_casos():
    return _ler_json("casos_clinicos.json", [])


def contar(n, singular, plural):
    """contar(1, "marcador", "marcadores") -> "1 marcador"."""
    return f"{n} {singular if n == 1 else plural}"


def formatar_numero(valor):
    """7.0 -> "7", 0.04 -> "0,04": faixa de referência legível em português."""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).replace(".", ",")
