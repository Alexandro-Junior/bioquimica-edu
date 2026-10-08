"""
Cálculos clínicos usados no app, sem interface.

Taxa de filtração glomerular estimada (TFGe) pela equação CKD-EPI 2021,
só com creatinina, que não usa raça:

    TFGe = 142 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^−1,200 × 0,9938^idade
           × 1,012 [se mulher]

    κ = 0,7 (mulher) ou 0,9 (homem); α = −0,241 (mulher) ou −0,302 (homem)
    Scr: creatinina sérica em mg/dL (método rastreável ao IDMS)
    resultado em mL/min/1,73 m²

Fontes:
- Inker LA et al. New Creatinine- and Cystatin C-Based Equations to
  Estimate GFR without Race. N Engl J Med 2021;385:1737-1749.
  https://doi.org/10.1056/NEJMoa2102953
- National Kidney Foundation, CKD-EPI Creatinine Equation (2021):
  https://www.kidney.org/ckd-epi-creatinine-equation-2021
- Categorias G1 a G5: KDIGO 2024 Clinical Practice Guideline for the
  Evaluation and Management of CKD. Kidney Int 2024;105(4S):S117-S314.
  https://doi.org/10.1016/j.kint.2023.10.018

A equação vale para adultos (18 anos ou mais) com creatinina estável: na
lesão renal aguda, com a creatinina subindo, ela superestima a função.
"""

from __future__ import annotations

IDADE_MINIMA = 18
IDADE_MAXIMA = 120
CREATININA_MINIMA = 0.1    # mg/dL
CREATININA_MAXIMA = 30.0

# (limite inferior, código, descrição): da maior TFG para a menor
CATEGORIAS_TFG = [
    (90, "G1", "Normal ou alta"),
    (60, "G2", "Levemente diminuída"),
    (45, "G3a", "Leve a moderadamente diminuída"),
    (30, "G3b", "Moderada a gravemente diminuída"),
    (15, "G4", "Gravemente diminuída"),
    (0, "G5", "Falência renal"),
]


class DadoInvalido(ValueError):
    """Entrada fora do que a equação aceita; a mensagem vai para a tela."""


def ler_numero(texto: str, nome: str) -> float:
    """Aceita vírgula ou ponto decimal ("1,2" ou "1.2")."""
    try:
        return float(str(texto).strip().replace(",", "."))
    except ValueError:
        raise DadoInvalido(f"Digite um número em {nome}.") from None


def tfg_ckd_epi_2021(creatinina: float, idade: float, feminino: bool) -> float:
    """TFGe em mL/min/1,73 m², sem arredondar."""
    if not CREATININA_MINIMA <= creatinina <= CREATININA_MAXIMA:
        raise DadoInvalido("A creatinina deve estar entre 0,1 e 30 mg/dL.")
    if not IDADE_MINIMA <= idade <= IDADE_MAXIMA:
        raise DadoInvalido("A equação CKD-EPI vale para adultos: idade de 18 a 120 anos.")
    kappa = 0.7 if feminino else 0.9
    alfa = -0.241 if feminino else -0.302
    razao = creatinina / kappa
    tfg = (142 * min(razao, 1.0) ** alfa * max(razao, 1.0) ** -1.200
           * 0.9938 ** idade)
    return tfg * 1.012 if feminino else tfg


def categoria_tfg(tfg: float) -> tuple[str, str]:
    """(código, descrição) da categoria KDIGO."""
    for limite, codigo, descricao in CATEGORIAS_TFG:
        if tfg >= limite:
            return codigo, descricao
    return CATEGORIAS_TFG[-1][1:]
