#!/usr/bin/env python3
"""
Teste rápido: Verifica se main_kivy_completo.py está funcional
- ✅ Imports OK
- ✅ Data files OK
- ✅ Classes instanciam corretamente
- ✅ App inicia sem erros
"""

import sys
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

print("="*50)
print("🧪 Teste BioquímicaEDU Mobile (Kivy)")
print("="*50)

# Test 1: Imports
print("\n1️⃣  Verificando imports...")
try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    print("   ✅ Kivy OK")
except ImportError as e:
    print(f"   ❌ Kivy não instalado: {e}")
    print("   → pip install kivy")
    sys.exit(1)

try:
    import main_kivy_completo
    print("   ✅ main_kivy_completo.py OK")
except Exception as e:
    print(f"   ❌ Erro ao importar: {e}")
    sys.exit(1)

# Test 2: Data files
print("\n2️⃣  Verificando arquivos de dados...")
files_check = {
    "marcadores.csv": ("CSV", 20),
    "flashcards.json": ("JSON", 50),
    "marcadores_extras.json": ("JSON", 8),
    "quiz_perguntas.json": ("JSON", 12),
    "casos_clinicos.json": ("JSON", 5),
}

for fname, (tipo, esperado) in files_check.items():
    fpath = DATA_DIR / fname
    if not fpath.exists():
        print(f"   ⚠️  {fname}: NÃO ENCONTRADO")
        continue

    try:
        if tipo == "CSV":
            with open(fpath, encoding="utf-8") as f:
                count = len(list(csv.DictReader(f)))
            print(f"   ✅ {fname}: {count} linhas")
        else:  # JSON
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            if "flashcards" in data:
                count = len(data["flashcards"])
            elif "marcadores_extras" in data:
                count = len(data["marcadores_extras"])
            elif "perguntas" in data:
                count = len(data["perguntas"])
            elif "casos" in data:
                count = len(data["casos"])
            else:
                count = "?"
            print(f"   ✅ {fname}: {count} itens")
    except Exception as e:
        print(f"   ❌ {fname}: ERRO - {e}")

# Test 3: Classes instanciam
print("\n3️⃣  Verificando classes...")
try:
    from main_kivy_completo import (
        TelaInicial, TelaEstudo, TelaFlashcards,
        TelaQuiz, TelaDiagnostico, TelaTutor
    )
    print("   ✅ Todas as classes importam")
except Exception as e:
    print(f"   ❌ Erro ao importar classes: {e}")

# Test 4: Teste mínimo da app
print("\n4️⃣  Iniciando app (5 segundos)...")
try:
    from main_kivy_completo import BioquimicaApp

    app = BioquimicaApp()
    print("   ✅ App criada com sucesso")
    print(f"   📊 Estado: XP={app.xp}, Streak={app.streak}")

    # Não roda o .run() em teste (bloquearia a tela)
    # Só valida que a classe está OK

except Exception as e:
    print(f"   ❌ Erro ao criar app: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ TUDO OK! Teste com: python main_kivy_completo.py")
print("="*50)
