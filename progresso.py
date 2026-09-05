"""
Motor de aprendizado do BioquímicaEDU.

Guarda o que o estudante já domina e decide o que ele deve revisar hoje.
Tudo fica em data/progresso.json, no computador do usuário.

Três decisões de projeto, cada uma com um porquê:

1. Agendamento por repetição espaçada (SM-2, o algoritmo do SuperMemo/Anki).
   Revisar às vésperas da prova rende menos do que revisar em intervalos
   crescentes. Meta-análise em educação médica: diferença média
   padronizada de 0.78 a favor da repetição espaçada (n = 21.415).
   https://pubmed.ncbi.nlm.nih.gov/41601436/

2. Nada de pontos soltos. A literatura de gamificação mostra o efeito de
   super-justificação: recompensa extrínseca pode reduzir a motivação de
   quem já estuda por interesse próprio. Por isso os números aqui medem
   domínio e memória — informação sobre o aprendizado, não prêmio.

3. Registro de calibração. Estudantes tendem a superestimar o quanto
   sabem, e os que sabem menos erram mais a própria estimativa. Guardar
   confiança declarada junto do acerto permite mostrar essa diferença,
   que é justamente o que o estudante sozinho não enxerga.
   https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6775028/
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
ARQUIVO = BASE_DIR / "data" / "progresso.json"

# ── SM-2 ────────────────────────────────────────────────────────────
FACILIDADE_INICIAL = 2.5
FACILIDADE_MINIMA = 1.3   # abaixo disso o item volta cedo demais para ser útil
INTERVALO_1 = 1           # dias, após o primeiro acerto
INTERVALO_2 = 6           # dias, após o segundo acerto
INTERVALO_FACIL_INICIAL = 4   # atalho quando o item já sai fácil de primeira

# Estágios de memória, por intervalo de revisão já alcançado
ESTAGIOS = [
    ("novo",        "Ainda não estudado"),
    ("aprendendo",  "Visto há pouco, memória frágil"),
    ("firmando",    "Revisado algumas vezes"),
    ("consolidado", "Retido a longo prazo"),
]


def _hoje() -> date:
    return date.today()


def _iso(d: date) -> str:
    return d.isoformat()


class Progresso:
    """Estado de aprendizado do estudante, persistido em disco."""

    def __init__(self, caminho: Path | None = None):
        self.caminho = Path(caminho) if caminho else ARQUIVO
        self.dados = self._carregar()

    # ── persistência ────────────────────────────────────────────────
    def _vazio(self) -> dict:
        return {
            "versao": 1,
            "criado_em": _iso(_hoje()),
            "itens": {},        # sigla -> estado de memória
            "sessoes": [],      # histórico diário
            "calibracao": [],   # (confiança declarada, acertou)
            "conquistas": [],
        }

    def _carregar(self) -> dict:
        if not self.caminho.exists():
            return self._vazio()
        try:
            with open(self.caminho, encoding="utf-8") as f:
                dados = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[progresso] arquivo ilegível ({e}); começando do zero")
            return self._vazio()

        base = self._vazio()
        base.update({k: v for k, v in dados.items() if k in base})
        return base

    def salvar(self) -> None:
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as f:
                json.dump(self.dados, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"[progresso] não foi possível salvar: {e}")

    # ── estado de um item ───────────────────────────────────────────
    def estado(self, sigla: str) -> dict:
        return self.dados["itens"].get(sigla, {
            "repeticoes": 0,
            "facilidade": FACILIDADE_INICIAL,
            "intervalo": 0,
            "proxima_revisao": None,
            "ultima_revisao": None,
            "acertos": 0,
            "tentativas": 0,
        })

    def estagio(self, sigla: str) -> str:
        e = self.estado(sigla)
        if e["tentativas"] == 0:
            return "novo"
        if e["intervalo"] >= 21:
            return "consolidado"
        if e["intervalo"] >= INTERVALO_2:
            return "firmando"
        return "aprendendo"

    # ── SM-2 ────────────────────────────────────────────────────────
    def registrar_resposta(self, sigla: str, qualidade: int,
                           confianca: int | None = None) -> dict:
        """Registra uma resposta e reagenda o item.

        qualidade: 0 a 5, como no SM-2. Abaixo de 3 conta como falha e o
        item volta para o início do ciclo.
        confianca: 1 a 5, o quanto o estudante achou que sabia ANTES de
        ver o resultado. Usada só para medir calibração.
        """
        qualidade = max(0, min(5, int(qualidade)))
        e = dict(self.estado(sigla))

        e["tentativas"] += 1
        acertou = qualidade >= 3
        if acertou:
            e["acertos"] += 1

        if not acertou:
            # Falhou: recomeça o ciclo, mas preserva a facilidade aprendida
            e["repeticoes"] = 0
            e["intervalo"] = INTERVALO_1
        else:
            e["repeticoes"] += 1
            if e["repeticoes"] == 1:
                # "Fácil" logo de cara pula o passo de 1 dia. Sem isso, as
                # quatro notas dariam o mesmo agendamento no primeiro
                # contato, e a escolha do estudante pareceria não valer
                # nada. É o mesmo atalho que o Anki usa.
                e["intervalo"] = INTERVALO_FACIL_INICIAL if qualidade == 5 else INTERVALO_1
            elif e["repeticoes"] == 2:
                e["intervalo"] = INTERVALO_2
            else:
                e["intervalo"] = max(1, round(e["intervalo"] * e["facilidade"]))

        # Ajuste da facilidade (fórmula do SM-2)
        f = e["facilidade"] + (0.1 - (5 - qualidade) * (0.08 + (5 - qualidade) * 0.02))
        e["facilidade"] = max(FACILIDADE_MINIMA, round(f, 3))

        hoje = _hoje()
        e["ultima_revisao"] = _iso(hoje)
        e["proxima_revisao"] = _iso(hoje + timedelta(days=e["intervalo"]))

        self.dados["itens"][sigla] = e

        if confianca is not None:
            self.dados["calibracao"].append({
                "data": _iso(hoje),
                "confianca": max(1, min(5, int(confianca))),
                "acertou": acertou,
            })
            # mantém a janela recente, que é a que interessa
            self.dados["calibracao"] = self.dados["calibracao"][-200:]

        self._registrar_sessao(acertou)
        self.salvar()
        return e

    def _registrar_sessao(self, acertou: bool) -> None:
        hoje = _iso(_hoje())
        sessoes = self.dados["sessoes"]
        if sessoes and sessoes[-1]["data"] == hoje:
            atual = sessoes[-1]
        else:
            atual = {"data": hoje, "revisados": 0, "acertos": 0}
            sessoes.append(atual)
        atual["revisados"] += 1
        if acertou:
            atual["acertos"] += 1
        self.dados["sessoes"] = sessoes[-365:]

    # ── consultas para a tela ───────────────────────────────────────
    def vencidos(self, siglas: list[str]) -> list[str]:
        """Itens já estudados cuja data de revisão chegou."""
        hoje = _hoje()
        atrasados = []
        for s in siglas:
            e = self.estado(s)
            prox = e.get("proxima_revisao")
            if prox and date.fromisoformat(prox) <= hoje:
                atrasados.append((date.fromisoformat(prox), s))
        atrasados.sort()  # mais atrasado primeiro
        return [s for _, s in atrasados]

    def nunca_vistos(self, siglas: list[str]) -> list[str]:
        return [s for s in siglas if self.estado(s)["tentativas"] == 0]

    def reforco_hoje(self, siglas: list[str]) -> list[str]:
        """Itens errados hoje e ainda não reacertados.

        O SM-2 puro agendaria esses itens só para amanhã. Mas errar e não
        rever na mesma sessão desperdiça o momento em que a correção
        gruda: por isso eles voltam ainda hoje, como fazem os passos de
        aprendizado do Anki.
        """
        hoje = _iso(_hoje())
        return [s for s in siglas
                if self.estado(s)["ultima_revisao"] == hoje
                and self.estado(s)["repeticoes"] == 0
                and self.estado(s)["tentativas"] > 0]

    def fila_do_dia(self, siglas: list[str], limite: int = 12) -> list[str]:
        """O que estudar hoje, em ordem de proveito.

        1. O que você errou hoje — corrigir enquanto o erro está fresco
        2. O que venceu — no ponto de quase esquecer, onde revisar rende mais
        3. Conteúdo novo — só depois que a dívida de revisão foi paga
        """
        fila = list(self.reforco_hoje(siglas))
        for s in self.vencidos(siglas):
            if s not in fila:
                fila.append(s)
        if len(fila) < limite:
            for s in self.nunca_vistos(siglas):
                if s not in fila:
                    fila.append(s)
                if len(fila) >= limite:
                    break
        return fila[:limite]

    def dominio(self, sigla: str) -> float:
        """0.0 a 1.0 — o quanto este item parece retido."""
        e = self.estado(sigla)
        if e["tentativas"] == 0:
            return 0.0
        acerto = e["acertos"] / e["tentativas"]
        # intervalo de 30 dias conta como retenção plena
        retencao = min(1.0, e["intervalo"] / 30)
        return round(0.4 * acerto + 0.6 * retencao, 3)

    def dominio_geral(self, siglas: list[str]) -> float:
        if not siglas:
            return 0.0
        return round(sum(self.dominio(s) for s in siglas) / len(siglas), 3)

    def contagem_estagios(self, siglas: list[str]) -> dict[str, int]:
        contagem = {nome: 0 for nome, _ in ESTAGIOS}
        for s in siglas:
            contagem[self.estagio(s)] += 1
        return contagem

    def pontos_fracos(self, siglas: list[str], n: int = 3) -> list[tuple[str, float]]:
        """Itens já tentados com menor domínio — onde revisar rende mais."""
        tentados = [(s, self.dominio(s)) for s in siglas
                    if self.estado(s)["tentativas"] > 0]
        tentados.sort(key=lambda t: t[1])
        return tentados[:n]

    # ── calibração ──────────────────────────────────────────────────
    def calibracao(self) -> dict | None:
        """Compara confiança declarada com acerto real.

        Retorna None enquanto não houver amostra suficiente para dizer
        algo honesto (evita rotular o estudante com base em 3 respostas).
        """
        registros = self.dados["calibracao"]
        if len(registros) < 10:
            return {"amostra": len(registros), "suficiente": False}

        confianca_media = sum(r["confianca"] for r in registros) / len(registros)
        acerto_real = sum(1 for r in registros if r["acertou"]) / len(registros)
        confianca_pct = (confianca_media - 1) / 4  # escala 1-5 -> 0-1
        desvio = confianca_pct - acerto_real

        if desvio > 0.15:
            leitura = "Você tem se achado mais preparado do que os acertos mostram"
        elif desvio < -0.15:
            leitura = "Você sabe mais do que imagina: confie um pouco mais"
        else:
            leitura = "Sua percepção está próxima do seu desempenho real"

        return {
            "amostra": len(registros),
            "suficiente": True,
            "confianca": round(confianca_pct, 3),
            "acerto": round(acerto_real, 3),
            "desvio": round(desvio, 3),
            "leitura": leitura,
        }

    # ── sequência de dias ───────────────────────────────────────────
    def sequencia(self) -> int:
        """Dias seguidos com estudo, contando de hoje ou de ontem para trás.

        Contar a partir de ontem evita zerar a sequência de quem ainda
        não estudou hoje — o objetivo é informar, não punir.
        """
        datas = {s["data"] for s in self.dados["sessoes"] if s["revisados"] > 0}
        if not datas:
            return 0
        hoje = _hoje()
        inicio = hoje if _iso(hoje) in datas else hoje - timedelta(days=1)
        if _iso(inicio) not in datas:
            return 0
        n, dia = 0, inicio
        while _iso(dia) in datas:
            n += 1
            dia -= timedelta(days=1)
        return n

    def revisados_hoje(self) -> int:
        hoje = _iso(_hoje())
        for s in reversed(self.dados["sessoes"]):
            if s["data"] == hoje:
                return s["revisados"]
        return 0

    def atividade_recente(self, dias: int = 28) -> list[tuple[str, int]]:
        """Últimos N dias como (data, revisões) — alimenta o gráfico."""
        por_data = {s["data"]: s["revisados"] for s in self.dados["sessoes"]}
        hoje = _hoje()
        return [
            (_iso(hoje - timedelta(days=i)), por_data.get(_iso(hoje - timedelta(days=i)), 0))
            for i in range(dias - 1, -1, -1)
        ]

    # ── conquistas ──────────────────────────────────────────────────
    def conquistas(self, siglas: list[str]) -> list[dict]:
        """Marcos ligados a aprendizado, não a tempo de uso.

        Cada um corresponde a algo que o estudante de fato passou a saber
        ou a um hábito de estudo com efeito comprovado — nunca a "abriu o
        app N vezes".
        """
        contagem = self.contagem_estagios(siglas)
        consolidados = contagem["consolidado"]
        vistos = len(siglas) - contagem["novo"]
        cal = self.calibracao()
        seq = self.sequencia()

        definicoes = [
            ("primeiro_contato", "Primeiro estudo",
             "Estudou o primeiro marcador", vistos >= 1),
            ("panorama", "Panorama completo",
             f"Já estudou todos os {len(siglas)} marcadores", vistos >= len(siglas)),
            ("primeira_retencao", "Primeira retenção",
             "Consolidou um marcador na memória de longo prazo", consolidados >= 1),
            ("memoria_solida", "Memória sólida",
             "Consolidou 10 marcadores", consolidados >= 10),
            ("dominio_amplo", "Domínio amplo",
             "Consolidou metade dos marcadores", consolidados >= len(siglas) / 2),
            ("ritmo", "Ritmo de estudo",
             "Estudou em 7 dias seguidos", seq >= 7),
            ("autoconhecimento", "Autoconhecimento",
             "Sua confiança ficou alinhada ao desempenho real",
             bool(cal and cal.get("suficiente") and abs(cal["desvio"]) <= 0.15)),
        ]

        obtidas = []
        for chave, titulo, descricao, alcancada in definicoes:
            if alcancada and chave not in self.dados["conquistas"]:
                self.dados["conquistas"].append(chave)
            obtidas.append({
                "chave": chave, "titulo": titulo,
                "descricao": descricao, "alcancada": alcancada,
            })
        return obtidas

    # ── resumo para a tela inicial ──────────────────────────────────
    def resumo(self, siglas: list[str], categorias: dict[str, str]) -> dict:
        """Tudo que a tela inicial precisa, em uma chamada."""
        fila = self.fila_do_dia(siglas)
        vencidos = self.vencidos(siglas)
        reforco = self.reforco_hoje(siglas)
        contagem = self.contagem_estagios(siglas)

        por_categoria = {}
        for sigla in siglas:
            cat = categorias.get(sigla, "Outros")
            por_categoria.setdefault(cat, []).append(sigla)
        dominio_categoria = {
            cat: self.dominio_geral(itens) for cat, itens in por_categoria.items()
        }

        return {
            "fila": fila,
            "vencidos": len(vencidos),
            "reforco": len(reforco),
            "novos": len(self.nunca_vistos(siglas)),
            "estagios": contagem,
            "dominio_geral": self.dominio_geral(siglas),
            "dominio_categoria": dominio_categoria,
            "pontos_fracos": self.pontos_fracos(siglas),
            "calibracao": self.calibracao(),
            "sequencia": self.sequencia(),
            "revisados_hoje": self.revisados_hoje(),
            "atividade": self.atividade_recente(),
            "conquistas": self.conquistas(siglas),
            "minutos_estimados": max(1, round(len(fila) * 0.75)),
        }
