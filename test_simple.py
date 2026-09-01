#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste simples: Verifica se main_kivy_completo.py funciona"""

import sys
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

print("\n[TEST] Iniciando validacao BioquimicaEDU Mobile...\n")

# Test 1: Imports
print("[1] Verificando imports...")
try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    print("    OK: Kivy")
except ImportError as e:
    print(f"    ERRO: Kivy nao instalado")
    sys.exit(1)

try:
    import main_kivy_completo
    print("    OK: main_kivy_completo.py")
except Exception as e:
    print(f"    ERRO ao importar: {e}")
    sys.exit(1)

# Test 2: Data files
print("\n[2] Verificando arquivos de dados...")
files = {
    "marcadores.csv": 20,
    "flashcards.json": 50,
    "quiz_perguntas.json": 12,
    "casos_clinicos.json": 5,
}

for fname, expected in files.items():
    fpath = DATA_DIR / fname
    if not fpath.exists():
        print(f"    AVISO: {fname} nao encontrado")
        continue

    try:
        if fname.endswith(".csv"):
            with open(fpath, encoding="utf-8") as f:
                count = len(list(csv.DictReader(f)))
        else:
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    if "flashcards" in data:
                        count = len(data["flashcards"])
                    else:
                        count = len(data.get(list(data.keys())[0], []))
                else:  # é uma lista
                    count = len(data)

        print(f"    OK: {fname} ({count} itens)")
    except Exception as e:
        print(f"    ERRO: {fname} - {e}")

# Test 3: Classes
print("\n[3] Verificando classes...")
try:
    from main_kivy_completo import (
        TelaInicial, TelaEstudo, TelaFlashcards,
        TelaQuiz, TelaDiagnostico, TelaTutor, BioquimicaApp
    )
    print("    OK: Todas as classes importam")
except Exception as e:
    print(f"    ERRO: {e}")
    sys.exit(1)

# Test 4: App initialization
print("\n[4] Testando app initialization...")
try:
    app = BioquimicaApp()
    print(f"    OK: App criada")
    # xp/streak sao criados em build(), nao em __init__
    if hasattr(app, 'xp'):
        print(f"       Status: XP={app.xp}, Streak={app.streak}")
    else:
        print(f"       (XP/Streak inicializam ao chamar build())")
except Exception as e:
    print(f"    ERRO: {e}")
    sys.exit(1)

print("\n[RESULTADO] SUCESSO! Teste com: python main_kivy_completo.py\n")
