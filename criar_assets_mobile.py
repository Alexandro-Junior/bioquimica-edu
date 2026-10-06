#!/usr/bin/env python3
"""
Gera o ícone e a tela de abertura do app Android/iOS.

O buildozer.spec exige assets/icon.png e assets/presplash.png; sem eles o
APK não compila. Os desenhos são feitos aqui com Pillow, sem baixar nada:
um anel benzênico branco sobre o verde de laboratório do app.

Uso:  python criar_assets_mobile.py
"""

import math
import os
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

VERDE = (14, 124, 90)
VERDE_ESCURO = (10, 95, 69)
PAPEL = (246, 244, 239)
TINTA = (23, 33, 28)
TINTA2 = (91, 101, 96)

ESCALA = 4  # desenha grande e reduz: bordas suaves sem serrilhado


def _hexagono(cx, cy, r):
    return [(cx + r * math.cos(math.radians(60 * i + 30)),
             cy + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]


def desenhar_marca(lado):
    """Quadrado arredondado verde com o anel benzênico."""
    L = lado * ESCALA
    img = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, L - 1, L - 1),
                                          radius=int(L * 0.225), fill=VERDE)

    # Faixa mais escura na base, para dar volume. É recortada pela própria
    # forma do ícone: desenhada como outro retângulo arredondado, ela
    # vazava um contorno claro pela borda inferior.
    mascara = Image.new("L", (L, L), 0)
    ImageDraw.Draw(mascara).rectangle((0, int(L * 0.62), L, L), fill=95)
    mascara = ImageChops.multiply(mascara, img.getchannel("A"))
    faixa = Image.new("RGBA", (L, L), (*VERDE_ESCURO, 0))
    faixa.putalpha(mascara)
    img = Image.alpha_composite(img, faixa)

    d = ImageDraw.Draw(img)
    cx, cy, r = L / 2, L / 2, L * 0.27
    espessura = int(L * 0.055)
    pontos = _hexagono(cx, cy, r)
    d.line(pontos + [pontos[0]], fill="white", width=espessura, joint="curve")
    for px, py in pontos:  # cantos arredondados
        d.ellipse((px - espessura / 2, py - espessura / 2,
                   px + espessura / 2, py + espessura / 2), fill="white")
    ri = r * 0.52
    d.ellipse((cx - ri, cy - ri, cx + ri, cy + ri),
              outline="white", width=int(espessura * 0.8))
    return img.resize((lado, lado), Image.LANCZOS)


def fonte(nome, tamanho):
    """Roboto que já vem com o Kivy; cai para a fonte padrão se faltar."""
    try:
        from kivy import kivy_data_dir
        return ImageFont.truetype(os.path.join(kivy_data_dir, "fonts", nome), tamanho)
    except Exception:
        return ImageFont.load_default()


def criar_icone():
    desenhar_marca(512).save(ASSETS / "icon.png")
    print("assets/icon.png")


def criar_presplash():
    largura, altura = 1080, 1920
    tela = Image.new("RGB", (largura, altura), PAPEL)
    marca = desenhar_marca(300)
    tela.paste(marca, ((largura - 300) // 2, 700), marca)

    d = ImageDraw.Draw(tela)
    titulo = "BioquímicaEDU"
    f_titulo = fonte("Roboto-Bold.ttf", 78)
    w = d.textlength(titulo, font=f_titulo)
    d.text(((largura - w) / 2, 1060), titulo, font=f_titulo, fill=TINTA)

    subtitulo = "Marcadores bioquímicos no diagnóstico clínico"
    f_sub = fonte("Roboto-Regular.ttf", 38)
    w = d.textlength(subtitulo, font=f_sub)
    d.text(((largura - w) / 2, 1168), subtitulo, font=f_sub, fill=TINTA2)

    tela.save(ASSETS / "presplash.png")
    print("assets/presplash.png")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    criar_icone()
    criar_presplash()
