#!/usr/bin/env python3
"""
Gera a logo do BioquímicaEDU em vetor (SVG) e em PNG de alta resolução.

Conceito: o hexágono é o anel benzênico — a química —, e a gota dentro
dele é a amostra de sangue de onde vêm os marcadores. Juntos dizem
"bioquímica clínica" num símbolo só.

O texto é convertido em contornos a partir da fonte Roboto que vem com o
Kivy: o SVG não depende de fonte instalada na gráfica ou no computador de
quem abrir o arquivo, e amplia para banner sem perder qualidade.

Saída em assets/logo/:
  simbolo.svg / .png            ícone quadrado (app, favicon, cantos de slide)
  horizontal.svg / .png         símbolo + nome + subtítulo (documento, cabeçalho)
  vertical.svg / .png           empilhada (capa, centro de banner)
  horizontal_negativo.svg/.png  versão clara para fundo verde ou escuro
  vertical_negativo.svg/.png    empilhada clara, para fundo verde ou escuro
  marca_mono.svg / .png         só o desenho, numa cor (carimbo, impressão P&B)
  marca_mono_branca.svg / .png  idem, branca, para foto ou fundo escuro
  avatar_redes.png              1080 × 1080, sobrevive ao recorte em círculo
  favicon-32.png, apple-touch-icon.png (180), icone-512.png   para o site
  abertura.png                  logo vertical leve, para a tela de abertura

Também atualiza, no app: assets/icon.png (ícone clássico), assets/presplash.png
(abertura do Android) e assets/icone_frente.png + assets/icone_fundo.png — as
duas camadas do ícone adaptativo, sem as quais o Android 8+ encaixa o ícone
quadrado dentro de uma máscara e ele aparece "numa caixinha".

Identidade completa (conceito, cores, tipografia, usos): docs/IDENTIDADE_VISUAL.md

Uso:  python criar_logo.py
"""

import math
import os
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

BASE = Path(__file__).resolve().parent
SAIDA = BASE / "assets" / "logo"

VERDE = "#0E7C5A"
VERDE_ESCURO = "#0A5F45"
MENTA = "#E1F1EA"
TINTA = "#17211C"
TINTA2 = "#5B6560"
PAPEL = "#F6F4EF"
BRANCO = "#FFFFFF"

NOME = ("Bioquímica", "EDU")
SUBTITULO = "Marcadores bioquímicos no diagnóstico clínico"

K = 0.5523  # constante de Bézier para quartos de círculo
VAO_EDU = 12  # espaço entre "Bioquímica" e "EDU": sem ele o "a" encosta no "E"


# ════════════════════════════════════════════════════════════════════
# GEOMETRIA: uma forma é uma lista de comandos em coordenadas finais
# (eixo y para baixo, como no SVG). Daí saem o SVG e o PNG, então os
# dois arquivos são sempre o mesmo desenho.
# ════════════════════════════════════════════════════════════════════
class Forma:
    def __init__(self, cor=None, contorno=None, espessura=0, cantos="round",
                 pontas="round"):
        self.cmds = []          # ("M", [(x,y)]), ("L",...), ("Q",...), ("C",...), ("Z", [])
        self.cor = cor          # preenchimento
        self.contorno = contorno
        self.espessura = espessura
        self.cantos = cantos
        self.pontas = pontas

    def M(self, p): self.cmds.append(("M", [p])); return self
    def L(self, p): self.cmds.append(("L", [p])); return self
    def Q(self, c, p): self.cmds.append(("Q", [c, p])); return self
    def C(self, c1, c2, p): self.cmds.append(("C", [c1, c2, p])); return self
    def Z(self): self.cmds.append(("Z", [])); return self

    def transformada(self, escala, dx, dy):
        f = Forma(self.cor, self.contorno, self.espessura * escala,
                  self.cantos, self.pontas)
        f.cmds = [(op, [(x * escala + dx, y * escala + dy) for x, y in pts])
                  for op, pts in self.cmds]
        return f

    def recolorida(self, cor=None, contorno=None):
        f = Forma(cor, contorno, self.espessura, self.cantos, self.pontas)
        f.cmds = list(self.cmds)
        return f

    def caixa(self):
        pts = [p for _, ps in self.cmds for p in ps]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)

    def svg_d(self):
        partes = []
        for op, pts in self.cmds:
            partes.append(op + " ".join(f"{x:.2f},{y:.2f}" for x, y in pts))
        return " ".join(partes)


def retangulo_arredondado(x, y, w, h, r, cor):
    f = Forma(cor=cor)
    f.M((x + r, y)).L((x + w - r, y))
    f.C((x + w - r + K * r, y), (x + w, y + r - K * r), (x + w, y + r))
    f.L((x + w, y + h - r))
    f.C((x + w, y + h - r + K * r), (x + w - r + K * r, y + h), (x + w - r, y + h))
    f.L((x + r, y + h))
    f.C((x + r - K * r, y + h), (x, y + h - r + K * r), (x, y + h - r))
    f.L((x, y + r))
    f.C((x, y + r - K * r), (x + r - K * r, y), (x + r, y))
    return f.Z()


def hexagono(cx, cy, r, cor, espessura):
    """Anel benzênico: hexágono de ponta para cima, traço com cantos redondos."""
    f = Forma(contorno=cor, espessura=espessura)
    for i in range(6):
        a = math.radians(-90 + 60 * i)
        p = (cx + r * math.cos(a), cy + r * math.sin(a))
        (f.M if i == 0 else f.L)(p)
    return f.Z()


def gota(cx, cy, R, topo_y, cor):
    """Gota: ponta em cima, base circular de raio R centrada em (cx, cy)."""
    H = cy - topo_y
    f = Forma(cor=cor)
    f.M((cx, topo_y))
    f.C((cx - 0.08 * R, topo_y + 0.30 * H), (cx - R, cy - 0.80 * R), (cx - R, cy))
    f.C((cx - R, cy + K * R), (cx - K * R, cy + R), (cx, cy + R))
    f.C((cx + K * R, cy + R), (cx + R, cy + K * R), (cx + R, cy))
    f.C((cx + R, cy - 0.80 * R), (cx + 0.08 * R, topo_y + 0.30 * H), (cx, topo_y))
    return f.Z()


def arco(cx, cy, r, de, ate, cor, espessura):
    """Arco curto (até 90°) como uma Bézier cúbica — o brilho da gota."""
    a1, a2 = math.radians(de), math.radians(ate)
    k = 4 / 3 * math.tan((a2 - a1) / 4)
    p0 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
    p3 = (cx + r * math.cos(a2), cy + r * math.sin(a2))
    c1 = (p0[0] - k * r * math.sin(a1), p0[1] + k * r * math.cos(a1))
    c2 = (p3[0] + k * r * math.sin(a2), p3[1] - k * r * math.cos(a2))
    return Forma(contorno=cor, espessura=espessura).M(p0).C(c1, c2, p3)


def marca(traco=BRANCO, gota_cor=BRANCO, brilho=VERDE):
    """Só o desenho (hexágono + gota), sem a placa, em coordenadas 512 × 512.

    `brilho=None` tira o reflexo: na versão de uma cor só, ele sumiria
    contra o fundo ou viraria um risco solto.
    """
    formas = [hexagono(256, 256, 150, traco, 30)]
    cx, cy, R = 256, 290, 54
    formas.append(gota(cx, cy, R, 176, gota_cor))
    if brilho:
        # reflexo curto na base da gota: é o que a faz ler como líquido
        formas.append(arco(cx, cy, R * 0.60, 105, 165, brilho, 11))
    return formas


def simbolo(fundo=VERDE, traco=BRANCO, gota_cor=BRANCO, brilho=VERDE):
    """O símbolo em 512 × 512: a marca sobre a placa arredondada."""
    return [retangulo_arredondado(0, 0, 512, 512, 114, fundo),
            *marca(traco, gota_cor, brilho)]


def centralizada(formas, escala, lado=512):
    """A marca reduzida em torno do centro do quadro de 512."""
    deslocamento = lado / 2 * (1 - escala)
    return [f.transformada(escala, deslocamento, deslocamento) for f in formas]


# ════════════════════════════════════════════════════════════════════
# TEXTO EM CONTORNOS
# ════════════════════════════════════════════════════════════════════
class _Caneta(BasePen):
    """Recebe o desenho de um glifo e o transforma em Forma."""

    def __init__(self, glyphset, forma, escala, x0, y0):
        super().__init__(glyphset)
        self.f, self.s, self.x0, self.y0 = forma, escala, x0, y0

    def _p(self, pt):  # unidades da fonte (y para cima) -> y para baixo
        return (self.x0 + pt[0] * self.s, self.y0 - pt[1] * self.s)

    def _moveTo(self, pt): self.f.M(self._p(pt))
    def _lineTo(self, pt): self.f.L(self._p(pt))
    def _curveToOne(self, p1, p2, p3): self.f.C(self._p(p1), self._p(p2), self._p(p3))
    def _qCurveToOne(self, p1, p2): self.f.Q(self._p(p1), self._p(p2))
    def _closePath(self): self.f.Z()


class Fonte:
    def __init__(self, arquivo):
        self.ttf = TTFont(arquivo)
        self.cmap = self.ttf.getBestCmap()
        self.glifos = self.ttf.getGlyphSet()
        self.upem = self.ttf["head"].unitsPerEm
        self.hmtx = self.ttf["hmtx"]
        os2 = self.ttf["OS/2"]
        self.altura_maiuscula = getattr(os2, "sCapHeight", 0) or 0.71 * self.upem

    def largura(self, texto, tamanho, espaco=0):
        s = tamanho / self.upem
        total = sum(self.hmtx[self.cmap[ord(c)]][0] for c in texto)
        return total * s + espaco * tamanho * max(0, len(texto) - 1)

    def texto(self, texto, tamanho, x, linha_base, cor, espaco=0):
        """Uma Forma com o texto em contornos; espaco em fração do tamanho."""
        f = Forma(cor=cor)
        s = tamanho / self.upem
        for c in texto:
            nome = self.cmap[ord(c)]
            self.glifos[nome].draw(_Caneta(self.glifos, f, s, x, linha_base))
            x += self.hmtx[nome][0] * s + espaco * tamanho
        return f


def fonte_kivy(nome):
    from kivy import kivy_data_dir
    return Fonte(os.path.join(kivy_data_dir, "fonts", nome))


# ════════════════════════════════════════════════════════════════════
# COMPOSIÇÕES
# ════════════════════════════════════════════════════════════════════
def composicao_horizontal(negrito, regular, negativo=False):
    cor_nome = BRANCO if negativo else TINTA
    cor_edu = MENTA if negativo else VERDE
    cor_sub = "#D7EDE4" if negativo else TINTA2
    marca = (simbolo(fundo=BRANCO, traco=VERDE, gota_cor=VERDE, brilho=BRANCO)
             if negativo else simbolo())

    lado = 300
    s = lado / 512
    formas = [f.transformada(s, 0, 0) for f in marca]

    x = lado + 70
    t_nome = 150
    base_nome = 168
    nome = negrito.texto(NOME[0], t_nome, x, base_nome, cor_nome, espaco=-0.01)
    x_edu = x + negrito.largura(NOME[0], t_nome, espaco=-0.01) + VAO_EDU
    edu = negrito.texto(NOME[1], t_nome, x_edu, base_nome, cor_edu, espaco=-0.01)
    largura_nome = x_edu + negrito.largura(NOME[1], t_nome, espaco=-0.01) - x

    t_sub = 52
    largura_sub = regular.largura(SUBTITULO, t_sub, espaco=0.005)
    # o subtítulo acompanha a largura do nome, para o bloco de texto ter
    # bordas alinhadas dos dois lados
    t_sub = t_sub * largura_nome / largura_sub
    sub = regular.texto(SUBTITULO, t_sub, x, 248, cor_sub, espaco=0.005)
    formas += [nome, edu, sub]
    return formas, (x + largura_nome + 8, lado)


def composicao_vertical(negrito, regular, negativo=False):
    cor_nome = BRANCO if negativo else TINTA
    cor_edu = MENTA if negativo else VERDE
    cor_sub = "#D7EDE4" if negativo else TINTA2
    placa = (simbolo(fundo=BRANCO, traco=VERDE, gota_cor=VERDE, brilho=BRANCO)
             if negativo else simbolo())
    lado = 420
    t_nome = 150
    t_sub = 46
    w_bio = negrito.largura(NOME[0], t_nome, espaco=-0.01)
    w_edu = negrito.largura(NOME[1], t_nome, espaco=-0.01)
    w_nome = w_bio + VAO_EDU + w_edu
    w_sub = regular.largura(SUBTITULO, t_sub, espaco=0.005)
    # a largura sai do maior elemento: fixá-la menor que o nome
    # descentralizava o símbolo em relação ao texto
    largura_total = max(lado, w_nome, w_sub)
    centro = largura_total / 2

    s = lado / 512
    formas = [f.transformada(s, centro - lado / 2, 0) for f in placa]

    altura_maiuscula = negrito.altura_maiuscula * t_nome / negrito.upem
    base = lado + 80 + altura_maiuscula
    x = centro - w_nome / 2
    formas.append(negrito.texto(NOME[0], t_nome, x, base, cor_nome, espaco=-0.01))
    formas.append(negrito.texto(NOME[1], t_nome, x + w_bio + VAO_EDU, base, cor_edu,
                                espaco=-0.01))
    formas.append(regular.texto(SUBTITULO, t_sub, centro - w_sub / 2,
                                base + 88, cor_sub, espaco=0.005))
    return formas, (largura_total, base + 110)


def enquadrar(formas, tamanho, margem):
    """Translada tudo para começar na margem e devolve o tamanho final."""
    x0 = min(f.caixa()[0] for f in formas)
    y0 = min(f.caixa()[1] for f in formas)
    x1 = max(f.caixa()[2] + f.espessura / 2 for f in formas)
    y1 = max(f.caixa()[3] + f.espessura / 2 for f in formas)
    x0 = min(x0, 0)
    y0 = min(y0, 0)
    formas = [f.transformada(1, margem - x0, margem - y0) for f in formas]
    return formas, (x1 - x0 + 2 * margem, y1 - y0 + 2 * margem)


# ════════════════════════════════════════════════════════════════════
# SAÍDAS
# ════════════════════════════════════════════════════════════════════
def salvar_svg(formas, tamanho, caminho, titulo):
    w, h = tamanho
    linhas = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
              f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{titulo}">',
              f"  <title>{titulo}</title>"]
    for f in formas:
        if f.contorno:
            linhas.append(f'  <path d="{f.svg_d()}" fill="none" stroke="{f.contorno}" '
                          f'stroke-width="{f.espessura:.2f}" stroke-linejoin="{f.cantos}" '
                          f'stroke-linecap="{f.pontas}"/>')
        else:
            linhas.append(f'  <path d="{f.svg_d()}" fill="{f.cor}"/>')
    linhas.append("</svg>")
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(caminho.relative_to(BASE))


def salvar_png(formas, tamanho, caminho, largura_px, fundo=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath

    w, h = tamanho
    dpi = 100
    fig = plt.figure(figsize=(largura_px / dpi, largura_px * h / w / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    if fundo:
        fig.patch.set_facecolor(fundo)
    else:
        fig.patch.set_alpha(0)

    pontos_por_unidade = largura_px / dpi * 72 / w
    for f in formas:
        verts, codes = [], []
        for op, pts in f.cmds:
            if op == "M":
                verts += pts; codes += [MPath.MOVETO]
            elif op == "L":
                verts += pts; codes += [MPath.LINETO]
            elif op == "Q":
                verts += pts; codes += [MPath.CURVE3] * 2
            elif op == "C":
                verts += pts; codes += [MPath.CURVE4] * 3
            elif op == "Z":
                verts.append(verts[-1] if verts else (0, 0)); codes.append(MPath.CLOSEPOLY)
        caminho_mpl = MPath(verts, codes)
        if f.contorno:
            ax.add_patch(PathPatch(caminho_mpl, fill=False, edgecolor=f.contorno,
                                   linewidth=f.espessura * pontos_por_unidade,
                                   joinstyle=f.cantos, capstyle=f.pontas))
        else:
            ax.add_patch(PathPatch(caminho_mpl, facecolor=f.cor, edgecolor="none",
                                   linewidth=0))
    fig.savefig(caminho, dpi=dpi, transparent=fundo is None)
    plt.close(fig)
    print(caminho.relative_to(BASE))


def salvar(formas, tamanho, nome, largura_px, titulo, fundo_png=None):
    salvar_svg(formas, tamanho, SAIDA / f"{nome}.svg", titulo)
    salvar_png(formas, tamanho, SAIDA / f"{nome}.png", largura_px, fundo_png)


def atualizar_assets_app(simbolo_formas):
    """Ícone e abertura do app com o mesmo símbolo da logo."""
    from PIL import Image, ImageDraw, ImageFont
    salvar_png(simbolo_formas, (512, 512), BASE / "assets" / "icon.png", 512)

    largura, altura = 1080, 1920
    tela = Image.new("RGB", (largura, altura), PAPEL)
    temp = SAIDA / "_presplash_simbolo.png"
    salvar_png(simbolo_formas, (512, 512), temp, 300)
    marca = Image.open(temp).convert("RGBA")
    tela.paste(marca, ((largura - 300) // 2, 700), marca)
    temp.unlink()

    from kivy import kivy_data_dir
    d = ImageDraw.Draw(tela)
    f_titulo = ImageFont.truetype(os.path.join(kivy_data_dir, "fonts", "Roboto-Bold.ttf"), 78)
    f_sub = ImageFont.truetype(os.path.join(kivy_data_dir, "fonts", "Roboto-Regular.ttf"), 38)
    w_bio = d.textlength(NOME[0], font=f_titulo)
    w_edu = d.textlength(NOME[1], font=f_titulo)
    x = (largura - w_bio - w_edu) / 2
    d.text((x, 1060), NOME[0], font=f_titulo, fill=TINTA)
    d.text((x + w_bio, 1060), NOME[1], font=f_titulo, fill=VERDE)
    w = d.textlength(SUBTITULO, font=f_sub)
    d.text(((largura - w) / 2, 1168), SUBTITULO, font=f_sub, fill=TINTA2)
    tela.save(BASE / "assets" / "presplash.png")
    print("assets/presplash.png")


def icone_adaptativo(desenho):
    """As duas camadas do ícone adaptativo do Android (8.0 em diante).

    O sistema recorta a camada da frente com a máscara do fabricante
    (círculo, squircle, gota...). Só o círculo central de 66 dp, num quadro
    de 108 dp (61%), nunca é cortado: o desenho fica dentro dele.
    """
    lado_px = 432  # 108 dp em xxxhdpi
    # o hexágono, com o traço, ocupa 64% do quadro de 512; a 0,72 fica com
    # 46% da camada, ~70% da área visível (72 dp), como os ícones do sistema
    frente = centralizada(desenho, 0.72)
    salvar_png(frente, (512, 512), BASE / "assets" / "icone_frente.png", lado_px)
    salvar_png([retangulo_arredondado(0, 0, 512, 512, 0, VERDE)], (512, 512),
               BASE / "assets" / "icone_fundo.png", lado_px)


def avatar_redes(desenho):
    """Quadrado cheio de verde: redes sociais recortam o avatar em círculo."""
    formas = [retangulo_arredondado(0, 0, 512, 512, 0, VERDE), *centralizada(desenho, 0.82)]
    salvar_png(formas, (512, 512), SAIDA / "avatar_redes.png", 1080)


def icones_site(placa):
    salvar_png(placa, (512, 512), SAIDA / "favicon-32.png", 32)
    # o iOS arredonda sozinho: placa sem cantos, com o desenho com folga
    quadrada = [retangulo_arredondado(0, 0, 512, 512, 0, VERDE), *centralizada(marca(), 0.86)]
    salvar_png(quadrada, (512, 512), SAIDA / "apple-touch-icon.png", 180)
    salvar_png(placa, (512, 512), SAIDA / "icone-512.png", 512)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    negrito = fonte_kivy("Roboto-Bold.ttf")
    regular = fonte_kivy("Roboto-Regular.ttf")

    placa = simbolo()
    salvar(placa, (512, 512), "simbolo", 2048, "BioquímicaEDU")

    formas, tam = composicao_horizontal(negrito, regular)
    formas, tam = enquadrar(formas, tam, 24)
    salvar(formas, tam, "horizontal", 3200, "BioquímicaEDU")

    formas, tam = composicao_horizontal(negrito, regular, negativo=True)
    formas, tam = enquadrar(formas, tam, 24)
    salvar(formas, tam, "horizontal_negativo", 3200, "BioquímicaEDU")

    formas, tam = composicao_vertical(negrito, regular)
    formas, tam = enquadrar(formas, tam, 24)
    salvar(formas, tam, "vertical", 2400, "BioquímicaEDU")
    # versão leve para a tela de abertura do app (a de 2400 px pesa na memória)
    salvar_png(formas, tam, SAIDA / "abertura.png", 720)

    formas, tam = composicao_vertical(negrito, regular, negativo=True)
    formas, tam = enquadrar(formas, tam, 24)
    salvar(formas, tam, "vertical_negativo", 2400, "BioquímicaEDU")

    # uma cor só: sem placa e sem reflexo
    mono = marca(traco=TINTA, gota_cor=TINTA, brilho=None)
    salvar(mono, (512, 512), "marca_mono", 1024, "BioquímicaEDU")
    branca = marca(traco=BRANCO, gota_cor=BRANCO, brilho=None)
    salvar(branca, (512, 512), "marca_mono_branca", 1024, "BioquímicaEDU")

    desenho_app = marca()
    avatar_redes(desenho_app)
    icones_site(placa)
    icone_adaptativo(desenho_app)
    atualizar_assets_app(placa)


if __name__ == "__main__":
    main()
