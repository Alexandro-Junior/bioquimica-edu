"""Testes do conteúdo de estudo (data/) e da calculadora de TFG estimada.

Conferem o que um erro de digitação nos dados quebraria em silêncio: um
marcador sem fontes ou sem casos, um link que não é https, uma questão
com resposta fora das alternativas, um símbolo que a fonte do app não
desenha (vira um quadradinho na tela) e a equação CKD-EPI 2021.

    python test_conteudo.py
"""

import json
import os
import sys
from pathlib import Path

import calculos
from calculos import DadoInvalido, categoria_tfg, ler_numero, tfg_ckd_epi_2021
from mobile import dados
from progresso import marcadores_no_texto

RAIZ = Path(__file__).resolve().parent
MARCADORES = dados.carregar_marcadores()
EXTRAS = dados.carregar_extras()
SIGLAS = [m["sigla"] for m in MARCADORES]
NOMES = {m["sigla"]: m["nome"] for m in MARCADORES}
SISTEMAS = {"Hepático", "Renal", "Glicêmico", "Lipídico", "Eletrólito", "Cardíaco"}

# o que a proposta do projeto lista como conteúdo obrigatório
DA_PROPOSTA = {"ALT", "AST", "GGT", "BT", "CREA", "UREIA", "TFGe", "GLI", "HbA1c", "CT",
               "HDL", "LDL", "TG", "Na", "K", "Cl", "HCO3", "pH", "CKMB", "TropI", "LDH"}

TESTES = []


def teste(fn):
    TESTES.append(fn)
    return fn


@teste
def todos_os_marcadores_da_proposta_existem():
    faltando = DA_PROPOSTA - set(SIGLAS)
    assert not faltando, f"marcadores da proposta ausentes: {sorted(faltando)}"
    assert len(SIGLAS) == len(set(SIGLAS)), "sigla repetida no CSV"


@teste
def cada_marcador_tem_dados_completos():
    campos = ("nome", "unidade", "interpretacao_alta", "interpretacao_baixa",
              "doencas_associadas_alta", "doencas_associadas_baixa")
    for m in MARCADORES:
        assert m["categoria"] in SISTEMAS, (m["sigla"], m["categoria"])
        assert m["valor_ref_min"] < m["valor_ref_max"], m["sigla"]
        for campo in campos:
            assert str(m.get(campo, "")).strip(), (m["sigla"], campo)


@teste
def cada_marcador_tem_fontes_videos_e_casos():
    for sigla in SIGLAS:
        e = EXTRAS.get(sigla)
        assert e, f"{sigla} sem material complementar"
        # os marcadores novos já nascem com pelo menos duas fontes e dois casos
        minimo = 2 if sigla in ("TFGe", "HCO3") else 1
        assert len(e.get("referencias", [])) >= minimo, f"{sigla}: poucas fontes"
        assert e.get("videos"), f"{sigla}: sem vídeo"
        assert len(e.get("exemplos", [])) >= minimo, f"{sigla}: poucos casos"
        for ref in e["referencias"] + e["videos"]:
            assert ref["url"].startswith("https://"), (sigla, ref["url"])
            assert ref["titulo"].strip(), sigla
        for v in e["videos"]:
            assert v["url"].startswith("https://www.youtube.com/watch?v="), (sigla, v["url"])
        for ex in e["exemplos"]:
            for campo in ("titulo", "descricao", "valores", "conducao"):
                assert ex.get(campo, "").strip(), (sigla, campo)
        for a in e.get("aprofundamento", []):
            assert a["titulo"].strip() and len(a["texto"]) > 40, sigla


@teste
def bilirrubinas_tfg_e_bicarbonato_aprofundados():
    titulos = [a["titulo"] for a in EXTRAS["BT"].get("aprofundamento", [])]
    assert "Bilirrubina direta e indireta" in titulos, titulos
    for sigla in ("TFGe", "HCO3"):
        assert EXTRAS[sigla].get("aprofundamento"), sigla


@teste
def cards_e_quiz_cobrem_os_novos_marcadores():
    cards = dados.carregar_flashcards()
    for sigla in ("TFGe", "HCO3"):
        ligados = [c for c in cards
                   if sigla in marcadores_no_texto(f"{c['pergunta']} {c['resposta']}",
                                                   SIGLAS, NOMES)]
        assert ligados, f"nenhum card leva a {sigla} para a revisão"
    quiz = dados.carregar_quiz()
    assert len({q["id"] for q in quiz}) == len(quiz), "id de questão repetido"
    for q in quiz:
        assert 0 <= q["resposta_correta"] < len(q["alternativas"]), q["id"]
    textos = " ".join(f"{q['pergunta']} {q['explicacao']}" for q in quiz)
    for sigla in ("TFGe", "HCO3"):
        assert sigla in marcadores_no_texto(textos, SIGLAS, NOMES), f"quiz sem {sigla}"


@teste
def nenhum_simbolo_fora_das_fontes_do_app():
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        print("    (fontTools não instalado: conferência de símbolos pulada)")
        return
    from kivy import kivy_data_dir
    fontes = [Path(kivy_data_dir) / "fonts" / "Roboto-Regular.ttf",
              RAIZ / "assets" / "fontes" / "AtkinsonHyperlegible-Regular.ttf"]
    mapas = [set(TTFont(f).getBestCmap()) for f in fontes if f.exists()]
    assert mapas, "nenhuma fonte encontrada"
    faltando = {}
    for arquivo in [RAIZ / "data" / "marcadores.csv", *sorted((RAIZ / "data").glob("*.json"))]:
        for ch in set(arquivo.read_text(encoding="utf-8")) - set("\n\r\t"):
            if not all(ord(ch) in mapa for mapa in mapas):
                faltando.setdefault(ch, []).append(arquivo.name)
    assert not faltando, f"símbolos que viram quadradinho: {faltando}"


# ── calculadora ─────────────────────────────────────────────────────
@teste
def tfg_ckd_epi_2021_confere_com_a_formula():
    # 142 × 0,9938^50 × 1,012 = 105,3 (creatinina igual a κ: os outros termos valem 1)
    assert round(tfg_ckd_epi_2021(0.7, 50, True), 1) == 105.3
    assert round(tfg_ckd_epi_2021(0.9, 50, False), 1) == 104.0
    assert round(tfg_ckd_epi_2021(1.9, 62, False)) == 39   # caso do diabetes na ficha
    assert round(tfg_ckd_epi_2021(2.4, 78, False)) == 27   # caso da lesão renal aguda
    # cai com creatinina e idade maiores
    assert tfg_ckd_epi_2021(1.5, 40, False) < tfg_ckd_epi_2021(1.0, 40, False)
    assert tfg_ckd_epi_2021(1.0, 80, True) < tfg_ckd_epi_2021(1.0, 30, True)


@teste
def categorias_kdigo_nos_limites():
    esperado = {120: "G1", 90: "G1", 89: "G2", 60: "G2", 59: "G3a", 45: "G3a", 44: "G3b",
                30: "G3b", 29: "G4", 15: "G4", 14: "G5", 0: "G5"}
    for tfg, codigo in esperado.items():
        assert categoria_tfg(tfg)[0] == codigo, (tfg, categoria_tfg(tfg))
    assert len(calculos.CATEGORIAS_TFG) == 6


@teste
def calculadora_recusa_entradas_invalidas():
    assert ler_numero("1,2", "creatinina") == 1.2 and ler_numero(" 0.9 ", "x") == 0.9
    for args in ((0, 50, True), (40, 50, True), (1.0, 12, False), (1.0, 130, False)):
        try:
            tfg_ckd_epi_2021(*args)
        except DadoInvalido:
            continue
        raise AssertionError(f"deveria recusar {args}")
    try:
        ler_numero("abc", "idade")
    except DadoInvalido as e:
        assert "idade" in str(e)
    else:
        raise AssertionError("texto deveria ser recusado")


if __name__ == "__main__":
    os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")
    falhas = 0
    for fn in TESTES:
        try:
            fn()
            print(f"  ✓ {fn.__name__.replace('_', ' ')}")
        except Exception as e:
            falhas += 1
            print(f"  ✗ {fn.__name__.replace('_', ' ')}: {type(e).__name__}: {e}")
    print(f"\n{len(TESTES) - falhas}/{len(TESTES)} testes do conteúdo passaram")
    sys.exit(1 if falhas else 0)
