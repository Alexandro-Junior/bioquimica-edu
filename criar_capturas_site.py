"""Capturas de tela para o site (site/imagens/), com progresso de exemplo.

Usa o mesmo roteiro de captura do relatório (relatorio/gerar_figuras.py),
numa pasta de aluno temporária: o progresso real em data/ não é tocado.
A conversa com o tutor só é capturada se o Gemini estiver configurado.

    python criar_capturas_site.py
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "site" / "imagens"
sys.path.insert(0, str(RAIZ / "relatorio"))

pasta_aluno = Path(tempfile.mkdtemp(prefix="bioq_site_"))
os.environ["BIOQ_PASTA_ALUNO"] = str(pasta_aluno)

import gerar_figuras as g  # noqa: E402  (depois de BIOQ_PASTA_ALUNO)

CELULAR = (400, 840)
COMPUTADOR = (1184, 760)
TAB_S4_EM_PE = (800, 1280)      # Galaxy Tab S4: 2560 × 1600 px a 320 dpi
TAB_S4_DEITADO = (1280, 800)
VOZ = {"leitura_voz": True, "atalho_libras": True}

# (nome no site, tamanho, preferências, passos do roteiro)
CAPTURAS = [
    ("computador-inicio", COMPUTADOR, {}, ['p(lambda: app.ir_para("inicio", animar=False), "foto")']),
    ("tablet-estudo", TAB_S4_EM_PE, {}, ['p(lambda: app.ir_para("estudo", animar=False), "foto")']),
    ("tablet-deitado-inicio", TAB_S4_DEITADO, {}, ['p(lambda: app.ir_para("inicio", animar=False), "foto")']),
    ("celular-inicio", CELULAR, VOZ, ['p(lambda: app.ir_para("inicio", animar=False), "foto")']),
    ("celular-revisao", CELULAR, VOZ, [
        'p(lambda: app.ir_para("revisao", animar=False), None)',
        'p(lambda: (tela()._definir_confianca(4), tela()._revelar()), "foto", 1.8)']),
    ("celular-detalhe", CELULAR, VOZ, [
        'p(lambda: app.ir_para("estudo", animar=False), None, 0.6)',
        'p(lambda: app.ir_para("detalhe", sigla="K", animar=False), "foto")']),
    ("celular-acessibilidade", CELULAR, VOZ, [
        'p(lambda: app.ir_para("inicio", animar=False), None, 0.6)',
        'p(lambda: app.ir_para("acessibilidade", animar=False), "foto")']),
    ("celular-alto-contraste", CELULAR,
     {**VOZ, "tema": "alto_contraste", "escala_texto": 1.3, "fonte_leitura": "hiperlegivel"}, [
        'p(lambda: app.ir_para("estudo", animar=False), None, 0.6)',
        'p(lambda: app.ir_para("detalhe", sigla="K", animar=False), "foto")']),
]


def salvar_webp(origem, nome):
    imagem = Image.open(origem).convert("RGB")
    destino = SAIDA / f"{nome}.webp"
    imagem.save(destino, "WEBP", quality=88, method=6)
    print(f"{destino.name}: {imagem.width} × {imagem.height}, {destino.stat().st_size // 1024} KB")


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="bioq_site_capturas_"))
    try:
        for nome, tamanho, prefs, passos in CAPTURAS:
            fotos = g.capturar(pasta_aluno, tmp / nome, tamanho, prefs, "\n".join(passos))
            if "foto" not in fotos:
                raise RuntimeError(f"captura {nome} não saiu")
            salvar_webp(fotos["foto"], nome)

        from assistente import ler_config_nuvem
        cfg = ler_config_nuvem()
        if cfg["chave"] or cfg["servidor"]:
            fotos = g.capturar(pasta_aluno, tmp / "tutor", CELULAR, VOZ, "\n".join([
                'p(lambda: app.ir_para("tutor", animar=False), None)',
                'p(lambda: tela()._perguntar("ALT ou AST: qual a diferença?"), "foto", 1.2, '
                'ate=lambda: not tela().ocupado)']), nuvem=True)
            salvar_webp(fotos["foto"], "celular-tutor")
        else:
            print("celular-tutor.webp NÃO gerada: Gemini sem chave (docs/TUTOR_GEMINI.md)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(pasta_aluno, ignore_errors=True)


if __name__ == "__main__":
    main()
