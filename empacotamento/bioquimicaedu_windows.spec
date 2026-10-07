# -*- mode: python ; coding: utf-8 -*-
"""Executável do BioquímicaEDU para Windows: um arquivo .exe só.

    pip install pyinstaller
    pyinstaller empacotamento/bioquimicaedu_windows.spec --noconfirm

Saída: dist/BioquimicaEDU-Windows.exe

Vai junto: o código do app, data/ e assets/. Nunca vão: o progresso e as
preferências de quem gerou o executável, nem o .env com a chave do Gemini.
O tutor com IA do executável fala com o servidor intermediário configurado
em config/tutor_nuvem.json (docs/TUTOR_GEMINI.md, parte 3), se existir.
"""

from pathlib import Path

from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, hookspath, runtime_hooks
from kivy_deps import angle, glew, sdl2
from PIL import Image

RAIZ = Path(SPECPATH).resolve().parent
PESSOAIS = {"progresso.json", "preferencias_mobile.json", "preferencias.json"}

dados = []
for pasta in ("data", "assets"):
    for arquivo in sorted((RAIZ / pasta).rglob("*")):
        if arquivo.is_file() and arquivo.name not in PESSOAIS and not arquivo.name.startswith("~$"):
            dados.append((str(arquivo), str(arquivo.parent.relative_to(RAIZ))))
config_nuvem = RAIZ / "config" / "tutor_nuvem.json"
if config_nuvem.exists():
    dados.append((str(config_nuvem), "config"))
assert not any(Path(origem).name == ".env" for origem, _ in dados), ".env não pode ir no executável"

# ícone do Windows, a partir do ícone do app
icone = Path(workpath) / "BioquimicaEDU.ico"
icone.parent.mkdir(parents=True, exist_ok=True)
Image.open(RAIZ / "assets" / "icon.png").save(icone, sizes=[(16, 16), (24, 24), (32, 32),
                                                          (48, 48), (64, 64), (128, 128), (256, 256)])

dependencias = get_deps_minimal(video=None, audio=None, camera=None, spelling=None)
# a versão clássica (Tkinter) e os geradores de imagens não fazem parte do app
dependencias["excludes"] = list(dependencias.get("excludes", [])) + [
    "tkinter", "_tkinter", "matplotlib", "numpy", "pandas", "scipy", "IPython",
]

a = Analysis(
    [str(RAIZ / "empacotamento" / "iniciar_app.py")],
    pathex=[str(RAIZ)],
    datas=dados,
    hookspath=hookspath(),
    runtime_hooks=runtime_hooks(),
    noarchive=False,
    **dependencias,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + angle.dep_bins)],
    name="BioquimicaEDU-Windows",
    icon=str(icone),
    console=False,          # sem a janela preta do terminal
    upx=False,              # compactar o .exe aumenta os falsos alarmes de antivírus
    runtime_tmpdir=None,
)
