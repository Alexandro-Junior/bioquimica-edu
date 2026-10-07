#!/usr/bin/env python3
"""Testes do motor de aprendizado (progresso.py) e do parser da IA.

Não abre janela nem precisa de Kivy ou Tkinter. Cada teste usa um
arquivo de progresso temporário: o estudo real (data/progresso.json)
nunca é lido nem alterado.

Uso:  python test_progresso.py      (ou: python -m pytest test_progresso.py)
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import progresso  # noqa: E402
from progresso import Progresso, marcadores_no_texto  # noqa: E402

SIGLAS = ["ALT", "AST", "Na", "K", "TropI", "GLI"]
NOMES = {"ALT": "Alanina Aminotransferase", "Na": "Sódio", "K": "Potássio",
         "TropI": "Troponina I", "GLI": "Glicose"}


class BaseProgresso(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = Path(self.pasta.name) / "progresso.json"
        self.hoje = date(2026, 3, 10)
        relogio = mock.patch.object(progresso, "_hoje", lambda: self.hoje)
        relogio.start()
        self.addCleanup(relogio.stop)
        self.addCleanup(self.pasta.cleanup)

    def novo(self):
        return Progresso(self.caminho)


class TestSM2(BaseProgresso):
    def test_intervalos_crescem_com_acertos(self):
        p = self.novo()
        self.assertEqual(p.registrar_resposta("ALT", 4)["intervalo"], 1)
        self.assertEqual(p.registrar_resposta("ALT", 4)["intervalo"], 6)
        e = p.registrar_resposta("ALT", 4)
        self.assertEqual(e["intervalo"], round(6 * 2.5))
        self.assertEqual(e["proxima_revisao"],
                         (self.hoje + timedelta(days=e["intervalo"])).isoformat())

    def test_facil_no_primeiro_contato_pula_para_quatro_dias(self):
        self.assertEqual(self.novo().registrar_resposta("ALT", 5)["intervalo"],
                         progresso.INTERVALO_FACIL_INICIAL)

    def test_erro_recomeca_ciclo_e_derruba_facilidade(self):
        p = self.novo()
        p.registrar_resposta("ALT", 4)
        p.registrar_resposta("ALT", 4)
        e = p.registrar_resposta("ALT", 0)
        self.assertEqual(e["repeticoes"], 0)
        self.assertEqual(e["intervalo"], progresso.INTERVALO_1)
        self.assertLess(e["facilidade"], 2.5)

    def test_facilidade_nunca_abaixo_do_minimo(self):
        p = self.novo()
        for _ in range(20):
            e = p.registrar_resposta("ALT", 0)
        self.assertEqual(e["facilidade"], progresso.FACILIDADE_MINIMA)

    def test_qualidade_fora_da_escala_e_limitada(self):
        e = self.novo().registrar_resposta("ALT", 99)
        self.assertEqual(e["acertos"], 1)
        self.assertLessEqual(e["facilidade"], 2.6)

    def test_reforco_do_mesmo_dia_sai_no_primeiro_acerto(self):
        p = self.novo()
        p.registrar_resposta("ALT", 0)
        self.assertEqual(p.reforco_hoje(SIGLAS), ["ALT"])
        p.registrar_resposta("ALT", 3)
        self.assertEqual(p.reforco_hoje(SIGLAS), [])

    def test_fila_prioriza_erro_depois_vencido_depois_novo(self):
        p = self.novo()
        p.registrar_resposta("AST", 4)          # volta amanhã
        p.registrar_resposta("ALT", 0)          # errado hoje
        self.hoje += timedelta(days=1)          # AST venceu; ALT também
        p.registrar_resposta("GLI", 0)          # errado no novo dia
        fila = p.fila_do_dia(SIGLAS)
        self.assertEqual(fila[0], "GLI")
        self.assertEqual(set(fila[1:3]), {"ALT", "AST"})
        self.assertEqual(fila[3:], ["Na", "K", "TropI"])

    def test_registrar_atividade_usa_peso_do_diagnostico(self):
        p = self.novo()
        p.registrar_atividade(["ALT"], False, peso="diagnostico")
        p.registrar_atividade(["AST"], False, peso="quiz")
        # nota 2 derruba a facilidade menos que nota 1
        self.assertGreater(p.estado("ALT")["facilidade"], p.estado("AST")["facilidade"])

    def test_calibracao_exige_amostra_minima(self):
        p = self.novo()
        for _ in range(9):
            p.registrar_resposta("ALT", 4, confianca=5)
        self.assertFalse(p.calibracao()["suficiente"])
        p.registrar_resposta("ALT", 4, confianca=5)
        cal = p.calibracao()
        self.assertTrue(cal["suficiente"])
        self.assertAlmostEqual(cal["desvio"], 0.0)

    def test_sequencia_conta_a_partir_de_ontem(self):
        p = self.novo()
        for _ in range(3):
            p.registrar_resposta("ALT", 4)
            self.hoje += timedelta(days=1)
        # hoje ainda sem estudo: não zera
        self.assertEqual(p.sequencia(), 3)
        self.hoje += timedelta(days=1)
        self.assertEqual(p.sequencia(), 0)


class TestPersistencia(BaseProgresso):
    def test_salva_e_recarrega(self):
        p = self.novo()
        p.registrar_resposta("ALT", 4, confianca=3)
        recarregado = self.novo()
        self.assertEqual(recarregado.estado("ALT"), p.estado("ALT"))
        self.assertEqual(len(recarregado.dados["calibracao"]), 1)

    def test_gravacao_nao_deixa_temporarios(self):
        p = self.novo()
        for _ in range(3):
            p.registrar_resposta("ALT", 4)
        self.assertEqual(os.listdir(self.pasta.name), ["progresso.json"])

    def test_falha_na_gravacao_preserva_arquivo_anterior(self):
        p = self.novo()
        p.registrar_resposta("ALT", 4)
        original = self.caminho.read_text(encoding="utf-8")
        with mock.patch.object(progresso.json, "dump", side_effect=OSError("disco cheio")):
            p.registrar_resposta("AST", 4)
        self.assertEqual(self.caminho.read_text(encoding="utf-8"), original)
        self.assertEqual(os.listdir(self.pasta.name), ["progresso.json"])

    def test_json_ilegivel_comeca_do_zero(self):
        self.caminho.write_text("{ quebrado", encoding="utf-8")
        self.assertEqual(self.novo().dados["itens"], {})

    def test_json_fora_do_formato_nao_derruba(self):
        for conteudo in ([], "texto", {"itens": [], "sessoes": {}, "calibracao": "x"},
                         {"itens": {"ALT": "não é dict"}, "sessoes": [{"sem": "data"}]}):
            self.caminho.write_text(json.dumps(conteudo), encoding="utf-8")
            p = self.novo()
            p.resumo(SIGLAS, {})  # tudo que a tela inicial lê
            p.registrar_resposta("ALT", 4)

    def test_item_incompleto_e_descartado(self):
        self.caminho.write_text(json.dumps({"itens": {"ALT": {"tentativas": 2}}}),
                                encoding="utf-8")
        p = self.novo()
        self.assertEqual(p.estado("ALT")["tentativas"], 0)
        self.assertEqual(p.estado("ALT")["facilidade"], progresso.FACILIDADE_INICIAL)

    def test_data_de_revisao_ilegivel_nao_derruba(self):
        completo = {"repeticoes": 1, "facilidade": 2.5, "intervalo": 1, "acertos": 1,
                    "tentativas": 1, "ultima_revisao": "2026-03-09"}
        self.caminho.write_text(json.dumps({"itens": {
            "ALT": {**completo, "proxima_revisao": "ontem"},
            "AST": {**completo, "proxima_revisao": 20260309},
            "GLI": {**completo, "proxima_revisao": "2026-03-09"},
        }}), encoding="utf-8")
        p = self.novo()
        self.assertEqual(p.vencidos(SIGLAS), ["GLI"])
        p.resumo(SIGLAS, {})

    def test_casos_resolvidos_fora_do_formato(self):
        self.caminho.write_text(json.dumps({"casos_resolvidos": [3, {"x": 1}, [2], True, "7"]}),
                                encoding="utf-8")
        p = self.novo()
        self.assertEqual(p.casos_resolvidos(), {3, "7"})
        p.marcar_caso_resolvido(4)
        self.assertEqual(self.novo().casos_resolvidos(), {3, "7", 4})


class TestVinculoComMarcadores(unittest.TestCase):
    def test_preposicao_na_nao_vira_sodio(self):
        self.assertEqual(marcadores_no_texto("Na hepatite alcoólica a AST sobe",
                                             SIGLAS, NOMES), ["AST"])

    def test_forma_ionica_e_nome_completo(self):
        self.assertIn("Na", marcadores_no_texto("Na+ de 128 mEq/L", SIGLAS, NOMES))
        self.assertIn("K", marcadores_no_texto("potássio elevado", SIGLAS, NOMES))

    def test_apelido(self):
        self.assertEqual(marcadores_no_texto("troponina positiva", SIGLAS, NOMES), ["TropI"])

    def test_sigla_dentro_de_palavra_nao_casa(self):
        self.assertEqual(marcadores_no_texto("ALTERAÇÃO discreta", SIGLAS, {}), [])


class TestParserDaIA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # o módulo testa a conexão ao ser importado; aqui não há servidor
        import requests
        with mock.patch.object(requests, "get", side_effect=requests.ConnectionError):
            import ollama_ia
        cls.mod = ollama_ia

    def extrair(self, texto):
        return self.mod.OllamaIA._extrair_questao(texto)

    def test_questao_valida_com_texto_em_volta(self):
        q = self.extrair('Aqui está: {"pergunta": "P?", "alternativas": ["a", "b"], '
                         '"resposta_correta": 1, "explicacao": "porque"} Fim.')
        self.assertEqual(q["resposta_correta"], 1)
        self.assertEqual(q["explicacao"], "porque")

    def test_questoes_invalidas_sao_rejeitadas(self):
        for texto in (
            "sem json",
            "{ inválido }",
            '{"pergunta": "P?", "alternativas": ["a"], "resposta_correta": 0}',
            '{"pergunta": "P?", "alternativas": ["a", "b"], "resposta_correta": 2}',
            '{"pergunta": "P?", "alternativas": ["a", "b"], "resposta_correta": "0"}',
            '{"pergunta": "P?", "alternativas": "a b", "resposta_correta": 0}',
            '{"pergunta": "", "alternativas": ["a", "b"], "resposta_correta": 0}',
            '{"pergunta": "P?", "alternativas": ["a", "b"], "resposta_correta": true}',
        ):
            self.assertIsNone(self.extrair(texto), texto)

    def test_temperatura_vai_em_options(self):
        ia = self.mod.OllamaIA.__new__(self.mod.OllamaIA)
        ia.model, ia.base_url = "mistral", "http://localhost:11434"
        resposta = mock.MagicMock(status_code=200)
        resposta.iter_lines.return_value = [b'{"response": "Ol"}', b"lixo", b'{"response": "a"}']
        resposta.__enter__.return_value = resposta
        with mock.patch.object(self.mod.requests, "post", return_value=resposta) as post:
            self.assertEqual(ia._gerar_resposta("oi"), "Ola")
        corpo = post.call_args.kwargs["json"]
        self.assertEqual(corpo["options"], {"temperature": 0.7})
        self.assertNotIn("temperature", corpo)

    def test_erro_http_vira_mensagem_reconhecivel(self):
        ia = self.mod.OllamaIA.__new__(self.mod.OllamaIA)
        ia.model, ia.base_url = "mistral", "http://localhost:11434"
        resposta = mock.MagicMock(status_code=404)
        resposta.__enter__.return_value = resposta
        with mock.patch.object(self.mod.requests, "post", return_value=resposta):
            self.assertTrue(ia._gerar_resposta("oi").startswith("❌"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
