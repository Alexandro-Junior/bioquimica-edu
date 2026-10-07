"""Ícones vetoriais da versão mobile.

Os ícones anteriores eram caracteres da fonte DejaVu (⌂ ▤ ❐ ✉): cada um
com um peso, uma altura e um estilo, e alguns com o sentido errado (um
envelope para o tutor). Aqui todos seguem a mesma gramática, a dos
conjuntos de ícones de produto: grade de 24 × 24, traço de 2 unidades,
pontas e junções arredondadas, cantos com raio. Como são desenhados no
canvas, ficam nítidos em qualquer tamanho e mudam de cor como texto.

As formas são escritas em coordenadas de SVG (y para baixo) e
convertidas na hora de desenhar.
"""

import math

from kivy.graphics import Color, Ellipse, Line, Mesh
from kivy.metrics import dp
from kivy.properties import ColorProperty, StringProperty
from kivy.uix.widget import Widget


# ── geometria auxiliar ──────────────────────────────────────────────
def _arredondar(pontos, raio, fechado=False, passos=5):
    """Troca cada canto de uma poligonal por uma curva de raio `raio`."""
    pares = list(zip(pontos[0::2], pontos[1::2]))
    n = len(pares)
    if n < 3:
        return pontos
    saida = []
    indices = range(n) if fechado else range(1, n - 1)
    if not fechado:
        saida += list(pares[0])
    for i in indices:
        ax, ay = pares[i - 1]
        px, py = pares[i]
        bx, by = pares[(i + 1) % n]
        da = math.hypot(ax - px, ay - py) or 1
        db = math.hypot(bx - px, by - py) or 1
        r = min(raio, da / 2, db / 2)
        p1 = (px + (ax - px) / da * r, py + (ay - py) / da * r)
        p2 = (px + (bx - px) / db * r, py + (by - py) / db * r)
        for k in range(passos + 1):
            t = k / passos
            x = (1 - t) ** 2 * p1[0] + 2 * (1 - t) * t * px + t ** 2 * p2[0]
            y = (1 - t) ** 2 * p1[1] + 2 * (1 - t) * t * py + t ** 2 * p2[1]
            saida += [x, y]
    if not fechado:
        saida += list(pares[-1])
    return saida


def _arco(cx, cy, r, inicio, fim, passos=24):
    """Arco em graus, sentido horário na tela (y para baixo)."""
    pts = []
    for k in range(passos + 1):
        a = math.radians(inicio + (fim - inicio) * k / passos)
        pts += [cx + r * math.cos(a), cy + r * math.sin(a)]
    return pts


def _estrela(cx, cy, r_ext, r_int, pontas=5):
    pts = []
    for k in range(pontas * 2):
        r = r_ext if k % 2 == 0 else r_int
        a = math.radians(-90 + 180 / pontas * k)
        pts += [cx + r * math.cos(a), cy + r * math.sin(a)]
    return pts


# ── formas (grade 24 × 24, y para baixo) ────────────────────────────
# ("linha", pontos, fechada) · ("curva", pontos, raio, fechada)
# ("circulo", cx, cy, r) · ("ponto", cx, cy, r) · ("cheio", pontos)
FORMAS = {
    "inicio": [
        ("curva", [3, 11, 12, 3.5, 21, 11], 1.5, False),
        ("curva", [5.5, 9.5, 5.5, 20.5, 18.5, 20.5, 18.5, 9.5], 2, False),
        ("curva", [10, 20.5, 10, 14.5, 14, 14.5, 14, 20.5], 1, False),
    ],
    "estudo": [
        ("curva", [12, 7, 9.5, 4.8, 2.8, 4.8, 2.8, 18, 9.5, 18, 12, 20], 1.5, False),
        ("curva", [12, 7, 14.5, 4.8, 21.2, 4.8, 21.2, 18, 14.5, 18, 12, 20], 1.5, False),
        ("linha", [12, 7, 12, 20], False),
    ],
    "cartas": [
        ("curva", [3.5, 9, 16.5, 9, 16.5, 20.5, 3.5, 20.5], 2.2, True),
        ("curva", [7.5, 9, 7.5, 4.5, 20.5, 4.5, 20.5, 16, 16.5, 16], 2.2, False),
    ],
    "pratica": [
        ("circulo", 12, 12, 9),
        ("circulo", 12, 12, 5),
        ("ponto", 12, 12, 1.6),
    ],
    "tutor": [
        ("curva", [3.2, 20.5, 3.2, 4.2, 20.8, 4.2, 20.8, 16.8, 7.4, 16.8, 3.2, 20.5],
         2.4, False),
        ("ponto", 8, 10.5, 1.1), ("ponto", 12, 10.5, 1.1), ("ponto", 16, 10.5, 1.1),
    ],
    "voltar":  [("linha", [15, 5, 8, 12, 15, 19], False)],
    "avancar": [("linha", [9, 5, 16, 12, 9, 19], False)],
    "seta": [
        ("linha", [4, 12, 20, 12], False),
        ("linha", [13.5, 5.5, 20, 12, 13.5, 18.5], False),
    ],
    "fechar": [("linha", [6, 6, 18, 18], False), ("linha", [18, 6, 6, 18], False)],
    "erro":   [("linha", [6.5, 6.5, 17.5, 17.5], False), ("linha", [17.5, 6.5, 6.5, 17.5], False)],
    "check":  [("linha", [4.5, 12.5, 9.5, 17.5, 19.5, 6.5], False)],
    "sobe": [
        ("linha", [12, 19.5, 12, 4.5], False),
        ("linha", [5.5, 11, 12, 4.5, 18.5, 11], False),
    ],
    "desce": [
        ("linha", [12, 4.5, 12, 19.5], False),
        ("linha", [5.5, 13, 12, 19.5, 18.5, 13], False),
    ],
    "busca": [("circulo", 10.8, 10.8, 6.8), ("linha", [15.8, 15.8, 20.5, 20.5], False)],
    "embaralhar": [
        ("linha", [3, 7, 7.5, 7, 16.5, 17, 21, 17], False),
        ("linha", [18, 14, 21, 17, 18, 20], False),
        ("linha", [3, 17, 7.5, 17, 16.5, 7, 21, 7], False),
        ("linha", [18, 4, 21, 7, 18, 10], False),
    ],
    "repetir": [
        ("arco", 12, 12, 8.5, 0, 270),
        ("linha", [12, 3.5, 15.5, 4.2, 18.5, 6.4, 20.5, 9.2], False),
        ("linha", [21, 4, 21, 9.5, 15.5, 9.5], False),
    ],
    "link": [
        ("curva", [18.5, 13.5, 18.5, 19.5, 4.5, 19.5, 4.5, 5.5, 10.5, 5.5], 2, False),
        ("linha", [14, 4, 20, 4, 20, 10], False),
        ("linha", [20, 4, 11.5, 12.5], False),
    ],
    "play": [("cheio", [8, 5, 19, 12, 8, 19])],
    "frasco": [
        ("curva", [10, 3, 10, 9.5, 4.6, 20.5, 19.4, 20.5, 14, 9.5, 14, 3], 1.2, False),
        ("linha", [8.5, 3, 15.5, 3], False),
        ("linha", [7, 15.5, 17, 15.5], False),
    ],
    "estrela":   [("cheio", _estrela(12, 12.6, 9.5, 4.2))],
    "estrela_v": [("curva", _estrela(12, 12.6, 9.5, 4.2), 0.8, True)],
    "acessibilidade": [
        ("circulo", 12, 12, 9.8),
        ("ponto", 12, 6.9, 1.5),
        ("linha", [7.2, 9.8, 12, 10.8, 16.8, 9.8], False),
        ("linha", [12, 10.8, 12, 14], False),
        ("linha", [9.3, 18.2, 12, 14, 14.7, 18.2], False),
    ],
    "voz": [
        ("curva", [3.5, 9, 7.5, 9, 12.5, 4.5, 12.5, 19.5, 7.5, 15, 3.5, 15], 1, True),
        ("arco", 12.5, 12, 4, -45, 45),
        ("arco", 12.5, 12, 7.5, -50, 50),
    ],
    "parar": [("cheio", [7, 7, 17, 7, 17, 17, 7, 17])],
    "libras": [
        ("curva", [7.5, 12.5, 7.5, 6, 9.5, 6, 9.5, 11], 1, False),
        ("curva", [9.5, 10.5, 9.5, 3.8, 11.7, 3.8, 11.7, 10.5], 1, False),
        ("curva", [11.7, 10.5, 11.7, 4.6, 13.9, 4.6, 13.9, 11], 1, False),
        ("curva", [13.9, 11, 13.9, 6.4, 16.1, 6.4, 16.1, 14.5], 1, False),
        ("curva", [7.5, 12.5, 5.2, 11, 4, 12.6, 8.4, 18.8, 10.6, 20.5, 14.5, 20.5,
                   16.1, 17.8, 16.1, 14.5], 1.6, False),
    ],
    "texto": [
        ("linha", [2.5, 19, 8, 5, 13.5, 19], False),
        ("linha", [4.6, 14, 11.4, 14], False),
        ("linha", [14.5, 19, 18, 10.5, 21.5, 19], False),
        ("linha", [15.8, 16, 20.2, 16], False),
    ],
    "contraste": [
        ("circulo", 12, 12, 9),
        ("cheio", [12, 3] + _arco(12, 12, 9, 90, 270)[2:] + [12, 21]),
    ],
    "foco": [
        ("curva", [3.5, 8, 3.5, 3.5, 8, 3.5], 1, False),
        ("curva", [16, 3.5, 20.5, 3.5, 20.5, 8], 1, False),
        ("curva", [20.5, 16, 20.5, 20.5, 16, 20.5], 1, False),
        ("curva", [8, 20.5, 3.5, 20.5, 3.5, 16], 1, False),
        ("circulo", 12, 12, 3.2),
    ],
    "movimento": [
        ("linha", [3, 8, 13, 8], False),
        ("linha", [3, 16, 9, 16], False),
        ("circulo", 17, 12, 4),
    ],
    "calendario": [
        ("curva", [3.5, 5.5, 20.5, 5.5, 20.5, 20.5, 3.5, 20.5], 2.2, True),
        ("linha", [3.5, 10, 20.5, 10], False),
        ("linha", [8, 3, 8, 7.5], False),
        ("linha", [16, 3, 16, 7.5], False),
    ],
    "info": [
        ("circulo", 12, 12, 9.2),
        ("linha", [12, 11, 12, 16.5], False),
        ("ponto", 12, 7.8, 1.25),
    ],
    "alerta": [
        ("curva", [12, 3.5, 21.5, 20, 2.5, 20], 1.6, True),
        ("linha", [12, 9.5, 12, 13.8], False),
        ("ponto", 12, 16.9, 1.2),
    ],
    "relogio": [("circulo", 12, 12, 9.2), ("linha", [12, 7, 12, 12, 15.5, 14], False)],
    "sessao": [
        ("linha", [8.5, 6, 20.5, 6], False),
        ("linha", [8.5, 12, 20.5, 12], False),
        ("linha", [8.5, 18, 20.5, 18], False),
        ("ponto", 4.5, 6, 1.3), ("ponto", 4.5, 12, 1.3), ("ponto", 4.5, 18, 1.3),
    ],
    "ponto": [("ponto", 12, 12, 4)],
}


class Icone(Widget):
    """Ícone vetorial centralizado na própria caixa.

    `tamanho` é o lado do desenho; a caixa padrão tem uma folga em volta,
    como tinham os ícones de fonte, para não mudar o espaçamento das telas.
    """

    color = ColorProperty([0, 0, 0, 1])
    disabled_color = ColorProperty([0, 0, 0, 1])
    nome = StringProperty("")

    def __init__(self, nome, tamanho=dp(22), espessura=None, **kwargs):
        # argumentos de Label que os ícones de fonte aceitavam
        for chave in ("halign", "valign", "font_name", "font_size", "text"):
            kwargs.pop(chave, None)
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (tamanho * 1.25, tamanho * 1.25))
        self.tamanho = tamanho
        self.espessura = espessura
        super().__init__(**kwargs)
        self.nome = nome
        self.bind(pos=self._desenhar, size=self._desenhar, color=self._desenhar,
                  nome=self._desenhar, disabled=self._desenhar)
        self._desenhar()

    def _desenhar(self, *_):
        self.canvas.clear()
        formas = FORMAS.get(self.nome)
        if not formas:
            return
        lado = min(self.tamanho, self.width, self.height) or self.tamanho
        # x + largura/2, e não center_x: quando `pos` muda, este método roda
        # antes de o Kivy atualizar center_x, que ainda traria a posição velha
        x0 = self.x + (self.width - lado) / 2
        y0 = self.y + (self.height - lado) / 2
        k = lado / 24.0
        # traço de 2 unidades da grade, nunca fino demais para enxergar
        traco = self.espessura or max(dp(1.4), 2 * k)
        largura = traco / 2  # Line.width do Kivy é meia espessura

        def tela(pontos):
            saida = []
            for i in range(0, len(pontos), 2):
                saida += [x0 + pontos[i] * k, y0 + lado - pontos[i + 1] * k]
            return saida

        cor = self.disabled_color if self.disabled else self.color
        with self.canvas:
            Color(*cor)
            for forma in formas:
                tipo = forma[0]
                if tipo == "linha":
                    Line(points=tela(forma[1]), width=largura, cap="round",
                         joint="round", close=forma[2])
                elif tipo == "curva":
                    pontos = _arredondar(forma[1], forma[2], fechado=forma[3])
                    Line(points=tela(pontos), width=largura, cap="round",
                         joint="round", close=forma[3])
                elif tipo == "arco":
                    _, cx, cy, r, a1, a2 = forma
                    Line(points=tela(_arco(cx, cy, r, a1, a2)), width=largura,
                         cap="round", joint="round")
                elif tipo == "circulo":
                    _, cx, cy, r = forma
                    px, py = tela([cx, cy])
                    Line(circle=(px, py, r * k), width=largura)
                elif tipo == "ponto":
                    _, cx, cy, r = forma
                    px, py = tela([cx, cy])
                    Ellipse(pos=(px - r * k, py - r * k), size=(2 * r * k, 2 * r * k))
                elif tipo == "cheio":
                    pts = tela(forma[1])
                    n = len(pts) // 2
                    cx = sum(pts[0::2]) / n
                    cy = sum(pts[1::2]) / n
                    vertices = [cx, cy, 0, 0]
                    for i in range(n + 1):
                        j = i % n
                        vertices += [pts[2 * j], pts[2 * j + 1], 0, 0]
                    Mesh(vertices=vertices, indices=list(range(n + 2)),
                         mode="triangle_fan")
                    # contorno fino arredonda os vértices do preenchimento
                    Line(points=pts, width=largura * 0.6, joint="round", close=True)
