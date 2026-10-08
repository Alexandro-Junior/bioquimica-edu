"""Testes das regras dos jogos didáticos, sem interface.

O principal: o valor sorteado para cada situação (baixo, normal, alto)
precisa cair nessa situação pela faixa de referência do próprio app, já
arredondado como aparece na tela, para todos os marcadores. Uma resposta
"certa" que o app marcasse como errada ensinaria a coisa errada.

O recorde dos jogos é gravado num progresso temporário: o arquivo real do
estudante não é tocado.

    python test_jogos.py
"""

import os
import random
import sys
import tempfile
from pathlib import Path

PASTA_TESTE = Path(tempfile.mkdtemp(prefix="bioquimicaedu_jogos_"))
os.environ["BIOQ_PASTA_ALUNO"] = str(PASTA_TESTE)   # antes de importar progresso

import jogos  # noqa: E402
from mobile import dados  # noqa: E402
from progresso import Progresso  # noqa: E402

MARCADORES = dados.carregar_marcadores()
SEM_BAIXO = {"ALT", "AST", "GGT", "BT", "AU", "CT", "LDL", "TG", "CKMB", "TropI", "LDH"}

TESTES = []


def teste(fn):
    TESTES.append(fn)
    return fn


@teste
def todo_marcador_tem_faixas_no_jogo():
    faltando = [m["sigla"] for m in MARCADORES if m["sigla"] not in jogos.FAIXAS_DO_JOGO]
    assert not faltando, f"sem faixas próprias (usariam o cálculo genérico): {faltando}"


@teste
def valor_sorteado_cai_na_situacao_pedida():
    rng = random.Random(7)
    for m in MARCADORES:
        for classe in jogos.classes_possiveis(m):
            for _ in range(300):
                valor = jogos.sortear_valor(m, classe, rng)
                obtida = jogos.classificar(valor, m["valor_ref_min"], m["valor_ref_max"])
                assert obtida == classe, (m["sigla"], classe, valor)
                assert valor not in (m["valor_ref_min"], m["valor_ref_max"]), \
                    f"{m['sigla']}: {valor} no limite exato da faixa"
                assert valor >= 0, (m["sigla"], valor)


@teste
def baixo_so_onde_tem_sentido_clinico():
    for m in MARCADORES:
        tem_baixo = "baixo" in jogos.classes_possiveis(m)
        assert tem_baixo == (m["sigla"] not in SEM_BAIXO), m["sigla"]
        # a tabela e a regra automática dizem a mesma coisa
        assert tem_baixo == jogos.baixo_tem_sentido(m), m["sigla"]


@teste
def toda_resposta_vem_com_explicacao():
    for m in MARCADORES:
        for classe in jogos.classes_possiveis(m):
            texto = jogos.explicacao(m, classe)
            assert len(texto) > 20, (m["sigla"], classe, texto)
    k = next(m for m in MARCADORES if m["sigla"] == "K")
    assert jogos.explicacao(k, "alto").startswith("Hipercalemia")
    assert "Pode aparecer em: Vômitos" in jogos.explicacao(k, "baixo")
    hdl = next(m for m in MARCADORES if m["sigla"] == "HDL")
    assert "Pode aparecer" not in jogos.explicacao(hdl, "alto"), "doença '—' não aparece"


@teste
def marcador_novo_entra_no_jogo_sem_tabela():
    bicarbonato = {"sigla": "HCO3_teste", "nome": "Bicarbonato", "categoria": "Eletrólito",
                   "valor_ref_min": 22.0, "valor_ref_max": 29.0, "unidade": "mEq/L",
                   "interpretacao_baixa": "Acidose metabólica"}
    ate_x = {"sigla": "X_teste", "nome": "Teste", "categoria": "Cardíaco",
             "valor_ref_min": 0.0, "valor_ref_max": 0.014, "unidade": "ng/mL",
             "interpretacao_baixa": "Acidose"}
    assert jogos.classes_possiveis(bicarbonato) == jogos.CLASSES
    assert jogos.classes_possiveis(ate_x) == ("normal", "alto")
    rng = random.Random(3)
    for m in (bicarbonato, ate_x):
        for classe in jogos.classes_possiveis(m):
            for _ in range(200):
                valor = jogos.sortear_valor(m, classe, rng)
                assert jogos.classificar(valor, m["valor_ref_min"], m["valor_ref_max"]) == \
                    classe, (m["sigla"], classe, valor)


@teste
def rodadas_sem_repetir_marcador():
    rodadas = jogos.sortear_rodadas(MARCADORES, rng=random.Random(1))
    assert len(rodadas) == jogos.RODADAS
    siglas = [r["sigla"] for r in rodadas]
    assert len(set(siglas)) == len(siglas), siglas
    # com muitas partidas, as três situações aparecem
    vistas = {r["classe"] for s in range(30)
              for r in jogos.sortear_rodadas(MARCADORES, rng=random.Random(s))}
    assert vistas == set(jogos.CLASSES), vistas
    assert jogos.sortear_rodadas([], rng=random.Random(1)) == []


@teste
def pontos_com_sequencia_e_dica():
    assert jogos.pontos(False, 5) == 0
    assert jogos.pontos(True, 1) == 10
    assert jogos.pontos(True, 2) == 15
    assert jogos.pontos(True, 9) == 30, "o bônus tem teto"
    assert jogos.pontos(True, 1, usou_dica=True) == 5
    assert [jogos.estrelas(a, 10) for a in (10, 9, 8, 7, 5, 4, 3, 0)] == [3, 3, 2, 2, 1, 1, 0, 0]
    assert jogos.estrelas(0, 0) == 0


@teste
def memoria_tem_um_par_por_sistema():
    for semente in range(20):
        cartas = jogos.montar_memoria(MARCADORES, rng=random.Random(semente))
        assert len(cartas) == 2 * jogos.PARES_MEMORIA
        sistemas = [c for c in cartas if c["tipo"] == "sistema"]
        assert len({c["titulo"] for c in sistemas}) == jogos.PARES_MEMORIA, "sistema repetido"
        for carta in cartas:
            pares = [o for o in cartas if jogos.forma_par(carta, o)]
            assert len(pares) == 1, (carta, pares)
    a, b = cartas[0], cartas[1]
    assert not jogos.forma_par(a, a)
    assert jogos.estrelas_memoria(6, 6) == 3 and jogos.estrelas_memoria(14, 6) == 2
    assert jogos.estrelas_memoria(30, 6) == 1


@teste
def recorde_pessoal_gravado_e_validado():
    caminho = PASTA_TESTE / "progresso_jogos.json"
    p = Progresso(caminho)
    assert p.recorde("faixas") is None
    assert p.registrar_partida("faixas", 120) is False, "a primeira partida não 'bate' nada"
    assert p.registrar_partida("faixas", 90) is False
    assert p.registrar_partida("faixas", 150) is True
    assert Progresso(caminho).recorde("faixas") == 150, "o recorde não foi salvo"
    # memória: menos jogadas é melhor
    assert p.registrar_partida("memoria", 12, menor_e_melhor=True) is False
    assert p.registrar_partida("memoria", 9, menor_e_melhor=True) is True
    assert p.registrar_partida("memoria", 15, menor_e_melhor=True) is False
    assert p.recorde("memoria") == 9 and p.dados["jogos"]["memoria"]["partidas"] == 3
    # arquivo editado à mão: o campo estranho volta ao padrão sem derrubar o resto
    caminho.write_text('{"jogos": ["lixo"], "casos_resolvidos": [3]}', encoding="utf-8")
    p = Progresso(caminho)
    assert p.recorde("faixas") is None and p.casos_resolvidos() == {3}
    caminho.write_text('{"jogos": {"faixas": "lixo", "memoria": {"recorde": "9"}}}',
                       encoding="utf-8")
    p = Progresso(caminho)
    assert p.recorde("faixas") is None and p.recorde("memoria") is None
    assert p.registrar_partida("faixas", 40) is False and p.recorde("faixas") == 40


if __name__ == "__main__":
    import shutil
    falhas = 0
    try:
        for fn in TESTES:
            try:
                fn()
                print(f"  ✓ {fn.__name__.replace('_', ' ')}")
            except Exception as e:
                falhas += 1
                print(f"  ✗ {fn.__name__.replace('_', ' ')}: {type(e).__name__}: {e}")
    finally:
        shutil.rmtree(PASTA_TESTE, ignore_errors=True)
    print(f"\n{len(TESTES) - falhas}/{len(TESTES)} testes dos jogos passaram")
    sys.exit(1 if falhas else 0)
