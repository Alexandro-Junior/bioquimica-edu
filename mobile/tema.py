"""Tema visual da versão mobile.

Mesma identidade do painel desktop — papel quente com acentos de
reagente — refinada para telas pequenas:

- uma única cor forte (o verde de laboratório) para a ação principal,
  para o olho saber onde tocar;
- âmbar, rubro e índigo com significado fixo (atenção, fragilidade,
  metacognição), nunca como decoração;
- cores por sistema só em pontos e etiquetas, para orientar sem pesar.

Acessibilidade faz parte do tema, não é um modo à parte:

- toda cor usada em texto tem contraste de pelo menos 4,5:1 com o fundo
  em que aparece (WCAG 2.2, nível AA) — inclusive as de sistema, que têm
  um tom de ponto e outro, mais escuro, para texto;
- o tema de alto contraste troca a paleta inteira (preto no branco,
  bordas visíveis no lugar de sombras);
- o tamanho do texto segue a escala escolhida no app multiplicada pela
  do sistema, e `dpt()` faz as caixas de texto crescerem junto;
- com movimento reduzido, as animações viram mudanças instantâneas.

As cores são listas alteradas no lugar: quem guardou uma referência
(ESTILO_TEXTO, variantes de botão) enxerga a paleta nova sem reimportar.
"""

import os

from kivy import kivy_data_dir
from kivy.core.text import LabelBase
from kivy.metrics import Metrics, dp
from kivy.utils import get_color_from_hex as _hex


def rgba(hexa, alfa=1.0):
    cor = _hex(hexa)
    cor[3] = alfa
    return cor


# ── Paletas ─────────────────────────────────────────────────────────
# Contrastes conferidos com a fórmula da WCAG; os comentários trazem a
# razão contra o fundo em que cada tom aparece como texto.
PALETAS = {
    "padrao": {
        "fundo":          "#F6F4EF",
        "superficie":     "#FFFFFF",
        "superficie_alt": "#EFEBE3",
        "borda":          "#E3DED4",
        "borda_forte":    "#C9C2B6",

        "tinta":          "#17211C",   # 15,9:1 no fundo
        "tinta2":         "#4A534E",   # 7,2:1 no fundo, 6,7:1 em superficie_alt
        "tinta3":         "#5F6964",   # 5,2:1 no fundo, 4,8:1 em superficie_alt

        "acento":         "#0E7C5A",   # branco sobre ele: 5,2:1
        "acento_escuro":  "#0A5F45",   # 6,6:1 em acento_suave
        "acento_suave":   "#E1F1EA",

        "ambar":          "#9A5A0A",   # branco sobre ele: 5,5:1
        "ambar_suave":    "#FBEFDB",   # âmbar sobre ele: 4,8:1
        "rubro":          "#B5392F",   # branco sobre ele: 5,9:1
        "rubro_suave":    "#FBE8E5",   # rubro sobre ele: 5,0:1
        "indigo":         "#3F5C9A",   # branco sobre ele: 6,5:1
        "indigo_suave":   "#E8EDF7",

        "branco":         "#FFFFFF",
        "sombra":         "#17211C",
    },
    "alto_contraste": {
        "fundo":          "#FFFFFF",
        "superficie":     "#FFFFFF",
        "superficie_alt": "#EDEDED",
        "borda":          "#1A1A1A",
        "borda_forte":    "#000000",

        "tinta":          "#000000",
        "tinta2":         "#1F1F1F",
        "tinta3":         "#383838",   # 11:1 no branco

        "acento":         "#005A3E",   # branco sobre ele: 8,6:1
        "acento_escuro":  "#003D2A",
        "acento_suave":   "#DDF0E7",

        "ambar":          "#6E3D00",
        "ambar_suave":    "#FCEBD2",
        "rubro":          "#8C1A11",
        "rubro_suave":    "#FBE3E0",
        "indigo":         "#1F3570",
        "indigo_suave":   "#E2E8F6",

        "branco":         "#FFFFFF",
        "sombra":         "#000000",
    },
}

# Cada sistema tem dois tons: o do ponto/barra (pode ser claro) e o de
# texto (escuro o bastante para 4,5:1 sobre o fundo tingido da etiqueta).
CATEGORIAS = {
    "padrao": {
        "Hepático":   ("#B7791F", "#8A5A12"),
        "Renal":      ("#2E7DB5", "#1F6699"),
        "Glicêmico":  ("#7B5CB8", "#6B4FA3"),
        "Lipídico":   ("#C0567B", "#A23E66"),
        "Eletrólito": ("#1C9A92", "#0F716A"),
        "Cardíaco":   ("#B5392F", "#A3322A"),
    },
    "alto_contraste": {
        "Hepático":   ("#7A4D00", "#5C3A00"),
        "Renal":      ("#0B4F80", "#0B4F80"),
        "Glicêmico":  ("#4E2F8C", "#4E2F8C"),
        "Lipídico":   ("#80244A", "#80244A"),
        "Eletrólito": ("#005650", "#005650"),
        "Cardíaco":   ("#8C1A11", "#8C1A11"),
    },
}

# Estágios de memória: frio para quente conforme o item fixa
ESTAGIOS = {
    "padrao": {
        "novo":        "#CBD2CD",
        "aprendendo":  "#E0A458",
        "firmando":    "#5B9BD5",
        "consolidado": "#0E7C5A",
    },
    "alto_contraste": {
        "novo":        "#9A9A9A",
        "aprendendo":  "#B86B00",
        "firmando":    "#1F5FA8",
        "consolidado": "#005A3E",
    },
}

ROTULO_ESTAGIO = {
    "novo":        "Não estudados",
    "aprendendo":  "Aprendendo",
    "firmando":    "Firmando",
    "consolidado": "Consolidados",
}

COR = {"transparente": [0, 0, 0, 0]}
COR_CATEGORIA = {}
COR_CATEGORIA_TEXTO = {}
COR_ESTAGIO = {}

# Ajustes vigentes; quem altera é aplicar_ajustes()
AJUSTES = {"tema": "padrao", "escala_texto": 1.0, "movimento_reduzido": False}
_ESCALA_SISTEMA = Metrics.fontscale   # fonte grande do Android, se houver


def _trocar(destino, chave, valor):
    """Atualiza a lista no lugar, preservando quem já a referencia."""
    if chave in destino:
        destino[chave][:] = valor
    else:
        destino[chave] = list(valor)


def aplicar_tema(nome):
    nome = nome if nome in PALETAS else "padrao"
    for chave, hexa in PALETAS[nome].items():
        _trocar(COR, chave, rgba(hexa))
    for categoria, (ponto, texto) in CATEGORIAS[nome].items():
        _trocar(COR_CATEGORIA, categoria, rgba(ponto))
        _trocar(COR_CATEGORIA_TEXTO, categoria, rgba(texto))
    for estagio, hexa in ESTAGIOS[nome].items():
        _trocar(COR_ESTAGIO, estagio, rgba(hexa))
    AJUSTES["tema"] = nome


def aplicar_ajustes(tema="padrao", escala_texto=1.0, movimento_reduzido=False,
                    fonte="padrao"):
    """Aplica as preferências de leitura antes de a interface ser montada."""
    aplicar_tema(tema)
    aplicar_fonte(fonte)
    AJUSTES["escala_texto"] = escala_texto
    AJUSTES["movimento_reduzido"] = bool(movimento_reduzido)
    Metrics.fontscale = _ESCALA_SISTEMA * escala_texto


# ── Fonte de leitura ────────────────────────────────────────────────
# A interface usa o nome "Roboto" (padrão do Kivy). Para a opção de leitura
# facilitada, o mesmo nome passa a apontar para a Atkinson Hyperlegible
# (Braille Institute, licença OFL): letras desenhadas para se diferenciarem
# mesmo com baixa visão (I, l e 1; O e 0; b, d, p e q). Como todo texto do
# app usa o nome padrão, a troca vale em todas as telas sem mudar código.
_FONTES_KIVY = os.path.join(kivy_data_dir, "fonts")
_FONTES_APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "assets", "fontes")
FONTES = {
    "padrao": [os.path.join(_FONTES_KIVY, f"Roboto-{peso}.ttf")
               for peso in ("Regular", "Italic", "Bold", "BoldItalic")],
    "hiperlegivel": [os.path.join(_FONTES_APP, f"AtkinsonHyperlegible-{peso}.ttf")
                     for peso in ("Regular", "Regular", "Bold", "Bold")],
}


def aplicar_fonte(nome):
    arquivos = FONTES.get(nome, FONTES["padrao"])
    if not all(os.path.exists(a) for a in arquivos):
        arquivos, nome = FONTES["padrao"], "padrao"   # arquivo ausente: não quebra
    regular, italico, negrito, negrito_italico = arquivos
    LabelBase.register(name="Roboto", fn_regular=regular, fn_italic=italico,
                       fn_bold=negrito, fn_bolditalic=negrito_italico)
    AJUSTES["fonte"] = nome


def alto_contraste():
    return AJUSTES["tema"] == "alto_contraste"


def movimento():
    """False quando o estudante pediu menos animação."""
    return not AJUSTES["movimento_reduzido"]


def escala():
    """Fator total de texto (sistema × app)."""
    return Metrics.fontscale


def texto_grande():
    """Texto grande o bastante para pedir layouts em mais linhas."""
    return Metrics.fontscale > 1.12


def dpt(valor):
    """dp que cresce com o texto: para caixas cuja altura é de um texto."""
    return dp(valor) * max(1.0, Metrics.fontscale)


def formato():
    """Classe de largura da janela (como no Material Design 3).

    "compacto"  < 600 dp   celular: barra de abas embaixo, uma coluna
    "medio"     < 840 dp   tablet em pé: menu lateral, conteúdo centralizado
    "expandido" ≥ 840 dp   tablet deitado e computador: duas ou três colunas
    """
    from kivy.core.window import Window
    largura = Window.width / dp(1)
    if largura < 600:
        return "compacto"
    if largura < 840:
        return "medio"
    return "expandido"


def cor_categoria(categoria):
    return COR_CATEGORIA.get(categoria, COR["tinta3"])


def cor_categoria_texto(categoria):
    return COR_CATEGORIA_TEXTO.get(categoria, COR["tinta2"])


aplicar_tema("padrao")


# ── Tipografia ──────────────────────────────────────────────────────
# Roboto (padrão do Kivy) tem todos os acentos do português. Escala de
# poucos degraus, para a hierarquia vir do tamanho e do peso, não da cor.
ESTILO_TEXTO = {
    "display":   {"font_size": "28sp", "bold": True,  "color": COR["tinta"]},
    "titulo":    {"font_size": "21sp", "bold": True,  "color": COR["tinta"]},
    "subtitulo": {"font_size": "17sp", "bold": True,  "color": COR["tinta"]},
    "corpo":     {"font_size": "15sp", "bold": False, "color": COR["tinta"]},
    "apoio":     {"font_size": "13.5sp", "bold": False, "color": COR["tinta2"]},
    "micro":     {"font_size": "12sp", "bold": False, "color": COR["tinta3"]},
    "secao":     {"font_size": "12sp", "bold": True,  "color": COR["tinta2"]},
}

# Mantido para quem ainda use texto com a fonte de símbolos; os ícones
# da interface são vetoriais (mobile/icones.py).
LabelBase.register(name="Icones",
                   fn_regular=os.path.join(kivy_data_dir, "fonts", "DejaVuSans.ttf"))

# ── Medidas ─────────────────────────────────────────────────────────
RAIO_CARTAO = dp(18)
RAIO_BOTAO = dp(14)
MARGEM = dp(16)
ALTURA_TOQUE = dp(48)   # mínimo recomendado para alvos de toque
