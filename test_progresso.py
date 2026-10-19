"""Testes do motor de revisão espaçada e do arquivo de progresso.

    python test_progresso.py

Tudo roda em pastas temporárias: o progresso real do estudante não é lido
nem alterado.
"""

import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

import progresso
from progresso import Progresso

TESTES = []


def teste(fn):
    TESTES.append(fn)
    return fn


def novo(dia=date(2026, 3, 2)):
    progresso._hoje = lambda: dia
    return Progresso(Path(tempfile.mkdtemp(prefix="bioq_teste_")) / "progresso.json")


@teste
def acertos_repetidos_no_mesmo_dia_nao_alongam_o_intervalo():
    # cards, quiz e jogos no mesmo dia levavam um marcador de 2 a 238 dias
    p = novo()
    primeiro = p.registrar_resposta("GLI", 4)
    for _ in range(5):
        e = p.registrar_resposta("GLI", 4)
    assert e["intervalo"] == primeiro["intervalo"], e
    assert e["repeticoes"] == 1 and e["proxima_revisao"] == primeiro["proxima_revisao"], e
    assert e["acertos"] == 6 and e["tentativas"] == 6, "os acertos continuam contando"


@teste
def erro_no_mesmo_dia_ainda_reinicia_o_ciclo():
    p = novo()
    p.registrar_resposta("K", 4)
    e = p.registrar_resposta("K", 1)
    assert e["repeticoes"] == 0 and e["intervalo"] == 1, e
    # depois do erro, o primeiro acerto do dia volta a agendar normalmente
    e = p.registrar_resposta("K", 4)
    assert e["repeticoes"] == 1, e


@teste
def em_dias_diferentes_o_intervalo_cresce():
    dia = date(2026, 3, 2)
    p = novo(dia)
    intervalos = []
    for _ in range(4):
        e = p.registrar_resposta("ALT", 4)
        intervalos.append(e["intervalo"])
        dia += timedelta(days=e["intervalo"])
        progresso._hoje = lambda d=dia: d
    assert intervalos == sorted(intervalos) and len(set(intervalos)) == 4, intervalos


@teste
def salvar_troca_o_arquivo_de_uma_vez():
    p = novo()
    p.registrar_resposta("CT", 4)
    pasta = p.caminho.parent
    assert json.loads(p.caminho.read_text(encoding="utf-8"))["itens"]["CT"]["acertos"] == 1
    assert not list(pasta.glob("*.tmp")), "o arquivo temporário deveria sumir"


@teste
def arquivo_ilegivel_e_guardado_e_nao_sobrescrito():
    p = novo()
    p.registrar_resposta("CT", 4)
    p.caminho.write_text('{"itens": {"CT": {"repeti', encoding="utf-8")   # gravação interrompida
    q = Progresso(p.caminho)
    assert q.dados["itens"] == {}
    guardados = list(p.caminho.parent.glob("progresso.ilegivel-*.json"))
    assert len(guardados) == 1, "o arquivo ilegível deveria ser posto de lado"
    q.registrar_resposta("K", 4)
    assert guardados[0].read_text(encoding="utf-8").startswith('{"itens"'), "foi sobrescrito"


@teste
def datas_e_registros_invalidos_nao_derrubam_o_app():
    p = novo()
    p.registrar_resposta("CT", 4)
    dados = json.loads(p.caminho.read_text(encoding="utf-8"))
    dados["itens"]["K"] = dict(dados["itens"]["CT"], proxima_revisao="amanhã")
    dados["sessoes"].append({"data": "2026-03-01"})                 # sem revisados
    dados["calibracao"].append({"data": "2026-03-01", "acertou": True})   # sem confiança
    p.caminho.write_text(json.dumps(dados), encoding="utf-8")
    q = Progresso(p.caminho)
    assert "K" not in q.dados["itens"] and "CT" in q.dados["itens"]
    assert all("revisados" in s for s in q.dados["sessoes"])
    assert all("confianca" in c for c in q.dados["calibracao"])
    q.resumo(["CT", "K"], {"CT": "Lipídico", "K": "Eletrólito"})   # o painel inicial sai daqui


if __name__ == "__main__":
    original = progresso._hoje
    falhas = 0
    for fn in TESTES:
        nome = fn.__name__.replace("_", " ")
        try:
            fn()
            print(f"  ✓ {nome}")
        except Exception as e:   # noqa: BLE001
            falhas += 1
            print(f"  ✗ {nome}: {type(e).__name__}: {e}")
        finally:
            progresso._hoje = original
    print(f"\n{len(TESTES) - falhas}/{len(TESTES)} testes do progresso passaram")
    sys.exit(1 if falhas else 0)
