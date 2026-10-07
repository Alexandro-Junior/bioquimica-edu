"""Tutor do BioquímicaEDU com provedores de resposta trocáveis.

O tutor pergunta ao primeiro provedor disponível; se ele falhar ou
devolver algo inútil, passa ao seguinte. A base local é sempre o último
da fila e nunca falha, então o estudante sempre recebe uma resposta.

Provedores:
- BaseLocal    responde com o conteúdo curado do próprio app: faixa de
               referência, interpretação e condições associadas. Offline,
               determinístico, sem risco de inventar valores.
- ModeloLocal  modelo de linguagem rodando no computador pelo Ollama
               (Llama, Mistral, Gemma...). Nada sai da máquina.

Um provedor de nuvem (por exemplo, Gemini) entra como mais uma classe com
`nome`, `disponivel()` e `responder()`, chamando um servidor intermediário
que guarda a chave da API — nunca a chave dentro do app. Ver
docs/ANALISE_EVOLUCAO.md.

Regra para qualquer modelo: o conteúdo curado do marcador vai junto da
pergunta, com a instrução de não contradizê-lo. Em educação em saúde, um
valor de referência inventado com confiança é pior do que nenhuma
resposta.
"""

from __future__ import annotations

import re


def formatar_numero(valor):
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).replace(".", ",")


def faixa(m):
    return (f"{formatar_numero(m['valor_ref_min'])} – "
            f"{formatar_numero(m['valor_ref_max'])} {m.get('unidade', '')}").strip()


def ficha(m):
    """Conteúdo curado de um marcador, em texto corrido."""
    def associado(chave):
        texto = (m.get(chave) or "").strip()
        return "" if not texto or texto == "—" else f"\nAssociado a: {texto}"

    return (f"{m['nome']} ({m['sigla']})\n"
            f"Referência: {faixa(m)}\n\n"
            f"Elevado: {m.get('interpretacao_alta') or '—'}"
            f"{associado('doencas_associadas_alta')}\n\n"
            f"Baixo: {m.get('interpretacao_baixa') or '—'}"
            f"{associado('doencas_associadas_baixa')}")


def instrucao_modelo(m, pergunta):
    """Prompt com o conteúdo do app como fonte de verdade."""
    return (
        "Você é tutor de bioquímica clínica para estudantes de graduação. "
        "Responda em português do Brasil, em até 150 palavras, de forma clara.\n"
        "Use APENAS os dados abaixo como fonte para valores de referência e "
        "interpretações. Se a pergunta pedir algo que os dados não cobrem, diga "
        "que isso está fora do conteúdo do app e sugira consultar a bibliografia. "
        "Não faça diagnóstico de casos reais de pacientes.\n\n"
        f"DADOS DO MARCADOR:\n{ficha(m)}\n\n"
        f"PERGUNTA DO ESTUDANTE: {pergunta}"
    )


def _tem_palavra(texto, palavras):
    return any(re.search(rf"\b{re.escape(p)}\b", texto) for p in palavras)


class BaseLocal:
    nome = "base do app"

    def __init__(self, marcadores):
        self.marcadores = marcadores

    def disponivel(self):
        return True

    def responder(self, pergunta, marcador):
        if marcador is not None:
            return ficha(marcador)
        texto = pergunta.lower()
        # palavra inteira: "foi" e "depois" não são cumprimento
        if _tem_palavra(texto, ("oi", "olá", "ola", "bom dia", "boa tarde", "boa noite")):
            return "Olá! Digite o nome ou a sigla de um marcador para começar."
        if _tem_palavra(texto, ("obrigado", "obrigada", "valeu")):
            return "De nada. Bons estudos!"
        if _tem_palavra(texto, ("ajuda", "como funciona", "o que você faz")):
            return ("Digite a sigla ou o nome de um marcador — por exemplo ALT, "
                    "Glicose ou Potássio — e eu mostro a faixa de referência e o que "
                    "significa estar alto ou baixo.")
        disponiveis = ", ".join(m["sigla"] for m in self.marcadores)
        return f"Não encontrei esse marcador na base.\n\nDisponíveis: {disponiveis}"


class ModeloLocal:
    """Modelo rodando no computador via Ollama (ollama_ia.OllamaIA)."""

    def __init__(self, ia):
        self.ia = ia
        self.nome = f"modelo local ({getattr(ia, 'model', 'Ollama')})"

    def disponivel(self):
        return bool(self.ia is not None and getattr(self.ia, "disponivel", False))

    def responder(self, pergunta, marcador):
        if marcador is None:
            return None  # sem marcador não há dado curado para ancorar a resposta
        return self.ia.gerar(instrucao_modelo(marcador, pergunta))


def resposta_util(texto):
    if not texto or not str(texto).strip():
        return False
    # ollama_ia devolve falhas como texto ("❌ Erro: ...", "Erro 404: ...")
    return not str(texto).strip().lower().startswith(("erro", "error", "[erro", "❌"))


class Assistente:
    def __init__(self, provedores):
        self.provedores = list(provedores)

    def responder(self, pergunta, marcador):
        """Devolve (texto, nome do provedor que respondeu, aviso ou None)."""
        aviso = None
        for provedor in self.provedores:
            if not provedor.disponivel():
                continue
            try:
                texto = provedor.responder(pergunta, marcador)
            except Exception as e:
                print(f"[tutor] {provedor.nome} falhou: {type(e).__name__}: {e}")
                texto = None
                aviso = f"O {provedor.nome} não respondeu; usei a base do app."
            if resposta_util(texto):
                return texto, provedor.nome, aviso
        return BaseLocal([]).responder(pergunta, marcador), "base do app", aviso
