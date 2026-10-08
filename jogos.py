"""
Jogos didáticos do BioquímicaEDU: as regras, sem interface.

A proposta do projeto pede "jogos didáticos" ao lado do estudo, do quiz e
dos casos clínicos. São dois, curtos, e cada um treina uma coisa:

1. "Alto, normal ou baixo?" — aparece o resultado de um exame; o estudante
   diz se ele está abaixo, dentro ou acima da faixa de referência e recebe
   na hora a explicação do que aquele resultado sugere. É a primeira
   pergunta de qualquer interpretação de exame, e a que o quiz e os casos
   clínicos já supõem respondida.
2. Jogo da memória — pares de cartas: cada marcador com o órgão ou o
   sistema que ele avalia. Para quem está começando a disciplina.

O desenho segue a seção 2.4 do relatório e o item 2 de progresso.py:
- o jogo é um desafio voluntário (Kaya; Ercag, 2023), não um prêmio pelo
  estudo: os pontos só medem a partida, não desbloqueiam nada e não entram
  em ranking com outras pessoas (Deci; Koestner; Ryan, 1999);
- toda resposta vem com a explicação, isto é, feedback sobre a
  competência, o tipo de retorno que aumenta a motivação intrínseca;
- o recorde é pessoal: compara o estudante com ele mesmo.

Os valores do jogo 1 saem de faixas plausíveis por marcador
(FAIXAS_DO_JOGO), sempre com folga em relação aos limites de referência,
para que nenhuma resposta dependa de arredondamento. "Baixo" só aparece
quando tem significado clínico (troponina baixa, por exemplo, não tem).
Um marcador sem entrada na tabela ganha faixas calculadas a partir da
própria referência, e entra no jogo sem mudar este arquivo.
"""

from __future__ import annotations

import math
import random

CLASSES = ("baixo", "normal", "alto")
RODADAS = 10
TEMPO_RODADA = 15          # segundos, quando o relógio está ligado
PONTOS_ACERTO = 10
BONUS_SEQUENCIA = 5        # por acerto seguido, a partir do segundo
BONUS_MAXIMO = 20
PARES_MEMORIA = 6

# Faixas usadas para sortear valores: (mínimo, máximo) de cada situação.
# "casas" é o número de casas decimais com que o valor aparece. As faixas de
# referência ficam em data/marcadores.csv; estas só dizem onde sortear.
FAIXAS_DO_JOGO = {
    #          normal            alto              baixo          casas
    "ALT":   {"normal": (12, 48), "alto": (85, 620), "casas": 0},
    "AST":   {"normal": (14, 35), "alto": (65, 480), "casas": 0},
    "GGT":   {"normal": (12, 42), "alto": (75, 420), "casas": 0},
    "BT":    {"normal": (0.3, 1.0), "alto": (1.8, 9.5), "casas": 1},
    "CREA":  {"normal": (0.7, 1.1), "alto": (1.6, 6.5), "baixo": (0.3, 0.5), "casas": 1},
    "UREIA": {"normal": (18, 36), "alto": (60, 190), "baixo": (6, 11), "casas": 0},
    "AU":    {"normal": (3.8, 6.4), "alto": (8.0, 12.5), "casas": 1},
    # TFG alta (hiperfiltração) não tem corte definido: no jogo, só normal ou baixa
    "TFGe":  {"normal": (95, 125), "alto": None, "baixo": (12, 55), "casas": 0},
    "GLI":   {"normal": (74, 94), "alto": (115, 320), "baixo": (40, 60), "casas": 0},
    "HbA1c": {"normal": (4.3, 5.4), "alto": (6.2, 11.5), "baixo": (3.0, 3.6), "casas": 1},
    "CT":    {"normal": (130, 190), "alto": (240, 360), "casas": 0},
    "HDL":   {"normal": (43, 57), "alto": (68, 95), "baixo": (22, 35), "casas": 0},
    "LDL":   {"normal": (60, 120), "alto": (160, 260), "casas": 0},
    "TG":    {"normal": (50, 140), "alto": (200, 650), "casas": 0},
    "Na":    {"normal": (137, 144), "alto": (150, 162), "baixo": (118, 131), "casas": 0},
    "K":     {"normal": (3.7, 4.8), "alto": (5.6, 7.2), "baixo": (2.4, 3.1), "casas": 1},
    "Cl":    {"normal": (99, 105), "alto": (110, 120), "baixo": (85, 94), "casas": 0},
    "pH":    {"normal": (7.36, 7.44), "alto": (7.50, 7.62), "baixo": (7.10, 7.30), "casas": 2},
    "HCO3":  {"normal": (23, 25), "alto": (30, 40), "baixo": (8, 18), "casas": 0},
    "CKMB":  {"normal": (4, 20), "alto": (40, 180), "casas": 0},
    "TropI": {"normal": (0.01, 0.03), "alto": (0.12, 8.0), "casas": 2},
    "LDH":   {"normal": (160, 260), "alto": (380, 1200), "casas": 0},
}

# Interpretações de "baixo" que não são achado clínico útil para o jogo
SEM_SENTIDO_CLINICO = ("raro", "não clinicamente")

# Nome do órgão ou sistema na carta do jogo da memória
SISTEMAS = {
    "Hepático": "Fígado",
    "Renal": "Rins",
    "Glicêmico": "Metabolismo da glicose",
    "Lipídico": "Gorduras do sangue",
    "Eletrólito": "Eletrólitos e ácido-base",
    "Cardíaco": "Coração",
}


# ── jogo 1: alto, normal ou baixo? ──────────────────────────────────
def classificar(valor: float, minimo: float, maximo: float) -> str:
    if valor < minimo:
        return "baixo"
    if valor > maximo:
        return "alto"
    return "normal"


def _casas(numero: float) -> int:
    texto = f"{numero:.6f}".rstrip("0").rstrip(".")
    return len(texto.split(".", 1)[1]) if "." in texto else 0


def baixo_tem_sentido(m: dict) -> bool:
    if m["valor_ref_min"] <= 0:
        return False   # faixa "até X": não existe valor baixo
    interpretacao = str(m.get("interpretacao_baixa", "")).strip().lower()
    return bool(interpretacao) and not interpretacao.startswith(SEM_SENTIDO_CLINICO)


def faixas(m: dict) -> dict:
    """Onde sortear o valor de cada situação, para um marcador."""
    if m["sigla"] in FAIXAS_DO_JOGO:
        f = FAIXAS_DO_JOGO[m["sigla"]]
        return {"normal": f["normal"], "alto": f["alto"], "baixo": f.get("baixo"),
                "casas": f["casas"]}
    # marcador novo: faixas proporcionais à própria referência
    minimo, maximo = m["valor_ref_min"], m["valor_ref_max"]
    largura = maximo - minimo
    casas = max(_casas(minimo), _casas(maximo))
    if minimo <= 0:
        normal = (0.4 * maximo, 0.9 * maximo)
        alto = (1.25 * maximo, 2.0 * maximo)
    else:
        normal = (minimo + 0.15 * largura, maximo - 0.15 * largura)
        alto = (maximo + 0.3 * largura, maximo + 1.5 * largura)
    baixo = None
    if baixo_tem_sentido(m):
        inferior = minimo - 1.5 * largura
        baixo = ((inferior, minimo - 0.3 * largura) if inferior > 0
                 else (0.4 * minimo, 0.85 * minimo))
    return {"normal": normal, "alto": alto, "baixo": baixo, "casas": casas}


def classes_possiveis(m: dict) -> tuple[str, ...]:
    f = faixas(m)
    return tuple(c for c in CLASSES if f[c])


def sortear_valor(m: dict, classe: str, rng: random.Random | None = None) -> float:
    rng = rng or random.Random()
    f = faixas(m)
    a, b = f[classe]
    if a > 0 and b / a > 4:
        # faixa larga (troponina de 0,12 a 8): sorteio em escala log, para
        # não sair quase sempre perto do teto
        valor = math.exp(rng.uniform(math.log(a), math.log(b)))
    else:
        valor = rng.uniform(a, b)
    return round(valor, f["casas"])


def sortear_rodadas(marcadores: list[dict], n: int = RODADAS,
                    rng: random.Random | None = None) -> list[dict]:
    """n rodadas, sem repetir marcador enquanto houver marcadores novos."""
    rng = rng or random.Random()
    if not marcadores:
        return []
    fila = []
    while len(fila) < n:
        lote = list(marcadores)
        rng.shuffle(lote)
        fila += lote
    rodadas = []
    for m in fila[:n]:
        classe = rng.choice(classes_possiveis(m))
        rodadas.append({"sigla": m["sigla"], "classe": classe,
                        "valor": sortear_valor(m, classe, rng)})
    return rodadas


def explicacao(m: dict, classe: str) -> str:
    """O que o resultado sugere, com as doenças da base de dados."""
    if classe == "normal":
        return ("Dentro da faixa de referência: sozinho, este resultado não indica "
                "alteração.")
    sufixo = {"alto": "alta", "baixo": "baixa"}[classe]   # colunas do CSV
    interpretacao = m.get(f"interpretacao_{sufixo}", "").strip().rstrip(".")
    doencas = m.get(f"doencas_associadas_{sufixo}", "").strip()
    texto = f"{interpretacao}." if interpretacao else ""
    if doencas and doencas != "—":
        texto += f" Pode aparecer em: {doencas}."
    return texto.strip()


def pontos(acertou: bool, sequencia: int, usou_dica: bool = False) -> int:
    """Pontos de uma resposta. `sequencia` conta este acerto (1 = o primeiro)."""
    if not acertou:
        return 0
    total = PONTOS_ACERTO + min(BONUS_MAXIMO, BONUS_SEQUENCIA * max(0, sequencia - 1))
    # com a faixa de referência à vista, a resposta vira comparação de números
    return total // 2 if usou_dica else total


def estrelas(acertos: int, total: int) -> int:
    """De 0 a 3, pela proporção de acertos."""
    if not total:
        return 0
    proporcao = acertos / total
    if proporcao >= 0.9:
        return 3
    if proporcao >= 0.7:
        return 2
    return 1 if proporcao >= 0.4 else 0


# ── jogo 2: memória ─────────────────────────────────────────────────
def montar_memoria(marcadores: list[dict], pares: int = PARES_MEMORIA,
                   rng: random.Random | None = None) -> list[dict]:
    """Cartas embaralhadas: um marcador de cada sistema e o sistema dele.

    Um marcador por sistema garante que cada carta de sistema tenha um
    único par possível na mesa.
    """
    rng = rng or random.Random()
    por_sistema = {}
    for m in marcadores:
        por_sistema.setdefault(m["categoria"], []).append(m)
    sistemas = list(por_sistema)
    rng.shuffle(sistemas)
    cartas = []
    for sistema in sistemas[:pares]:
        m = rng.choice(por_sistema[sistema])
        cartas.append({"par": m["sigla"], "tipo": "marcador", "titulo": m["sigla"],
                       "subtitulo": m["nome"], "categoria": sistema})
        cartas.append({"par": m["sigla"], "tipo": "sistema",
                       "titulo": SISTEMAS.get(sistema, sistema), "subtitulo": sistema,
                       "categoria": sistema})
    rng.shuffle(cartas)
    return cartas


def forma_par(a: dict, b: dict) -> bool:
    return a is not b and a["par"] == b["par"] and a["tipo"] != b["tipo"]


def estrelas_memoria(jogadas: int, pares: int) -> int:
    """De 1 a 3, pelas jogadas além do mínimo (uma por par)."""
    sobra = jogadas - pares
    if sobra <= 3:
        return 3
    return 2 if sobra <= 8 else 1
