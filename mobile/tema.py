"""Tema visual da versão mobile.

Mesma identidade do painel desktop — papel quente com acentos de
reagente — refinada para telas pequenas:

- uma única cor forte (o verde de laboratório) para a ação principal,
  para o olho saber onde tocar;
- âmbar, rubro e índigo com significado fixo (atenção, fragilidade,
  metacognição), nunca como decoração;
- cores por sistema só em pontos e etiquetas, para orientar sem pesar.
"""

import os

from kivy import kivy_data_dir
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.utils import get_color_from_hex as _hex


def rgba(hexa, alfa=1.0):
    cor = _hex(hexa)
    cor[3] = alfa
    return cor


# ── Cores ───────────────────────────────────────────────────────────
COR = {
    "fundo":          rgba("#F6F4EF"),
    "superficie":     rgba("#FFFFFF"),
    "superficie_alt": rgba("#EFEBE3"),
    "borda":          rgba("#E6E1D8"),

    "tinta":          rgba("#17211C"),
    "tinta2":         rgba("#5B6560"),
    "tinta3":         rgba("#98A19C"),

    "acento":         rgba("#0E7C5A"),
    "acento_escuro":  rgba("#0A5F45"),
    "acento_suave":   rgba("#E1F1EA"),

    "ambar":          rgba("#C27818"),
    "ambar_suave":    rgba("#FBEFDB"),
    "rubro":          rgba("#B5392F"),
    "rubro_suave":    rgba("#FBE8E5"),
    "indigo":         rgba("#3F5C9A"),
    "indigo_suave":   rgba("#E8EDF7"),

    "branco":         rgba("#FFFFFF"),
    "transparente":   (0, 0, 0, 0),
    "sombra":         rgba("#17211C"),
}

# Um tom por sistema, usado só em pontos e etiquetas
COR_CATEGORIA = {
    "Hepático":   rgba("#B7791F"),
    "Renal":      rgba("#2E7DB5"),
    "Glicêmico":  rgba("#7B5CB8"),
    "Lipídico":   rgba("#C0567B"),
    "Eletrólito": rgba("#1C9A92"),
    "Cardíaco":   rgba("#B5392F"),
}

# Estágios de memória: frio para quente conforme o item fixa
COR_ESTAGIO = {
    "novo":        rgba("#CBD2CD"),
    "aprendendo":  rgba("#E0A458"),
    "firmando":    rgba("#5B9BD5"),
    "consolidado": rgba("#0E7C5A"),
}

ROTULO_ESTAGIO = {
    "novo":        "Não estudados",
    "aprendendo":  "Aprendendo",
    "firmando":    "Firmando",
    "consolidado": "Consolidados",
}


def cor_categoria(categoria):
    return COR_CATEGORIA.get(categoria, COR["tinta3"])


# ── Tipografia ──────────────────────────────────────────────────────
# Roboto (padrão do Kivy) tem todos os acentos do português.
ESTILO_TEXTO = {
    "display":   {"font_size": "30sp", "bold": True,  "color": COR["tinta"]},
    "titulo":    {"font_size": "22sp", "bold": True,  "color": COR["tinta"]},
    "subtitulo": {"font_size": "17sp", "bold": True,  "color": COR["tinta"]},
    "corpo":     {"font_size": "14.5sp", "bold": False, "color": COR["tinta"]},
    "apoio":     {"font_size": "13sp", "bold": False, "color": COR["tinta2"]},
    "micro":     {"font_size": "11.5sp", "bold": False, "color": COR["tinta3"]},
    "secao":     {"font_size": "13sp", "bold": True,  "color": COR["tinta2"]},
}

# ── Ícones ──────────────────────────────────────────────────────────
# A DejaVuSans vem com o Kivy (inclusive no APK) e desenha estes símbolos.
# Glifos que ela não tem (lupa, fogo, troféu) são desenhados no canvas.
LabelBase.register(name="Icones",
                   fn_regular=os.path.join(kivy_data_dir, "fonts", "DejaVuSans.ttf"))

ICONE = {
    "inicio":     "⌂",  # ⌂
    "estudo":     "▤",  # ▤
    "cartas":     "❐",  # ❐
    "pratica":    "◎",  # ◎
    "tutor":      "✉",  # ✉
    "voltar":     "‹",  # ‹
    "avancar":    "›",  # ›
    "seta":       "→",  # →
    "fechar":     "✕",  # ✕
    "check":      "✓",  # ✓
    "erro":       "✗",  # ✗
    "estrela":    "★",  # ★
    "estrela_v":  "☆",  # ☆
    "raio":       "⚡",  # ⚡
    "embaralhar": "⇄",  # ⇄
    "repetir":    "↻",  # ↻
    "link":       "↗",  # ↗
    "play":       "▶",  # ▶
    "frasco":     "⚗",  # ⚗
    "atomo":      "⚛",  # ⚛
    "sobe":       "↑",  # ↑
    "desce":      "↓",  # ↓
    "ponto":      "●",  # ●
}

# ── Medidas ─────────────────────────────────────────────────────────
RAIO_CARTAO = dp(20)
RAIO_BOTAO = dp(14)
MARGEM = dp(16)
ALTURA_TOQUE = dp(48)   # mínimo recomendado para alvos de toque
