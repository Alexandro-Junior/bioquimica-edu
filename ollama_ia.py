"""
Módulo de IA com Ollama (Local, 100% privado)
Gerencia chat, quiz dinâmico e discussão de casos
"""

import threading
import requests
import json
from typing import Callable, Optional

class OllamaIA:
    def __init__(self, model="mistral", base_url="http://localhost:11434"):
        """
        Inicializa conexão com Ollama local

        Args:
            model: Modelo Ollama a usar (mistral, neural-chat, phi, etc)
            base_url: URL do servidor Ollama (default localhost:11434)
        """
        self.model = model
        self.base_url = base_url
        self.disponivel = False
        self.historico_chat = []
        self.thread_resposta = None

        # Verifica se Ollama está rodando
        self._verificar_conexao()

    def _verificar_conexao(self):
        """Verifica se Ollama está disponível"""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=2)
            self.disponivel = r.status_code == 200
            if self.disponivel:
                print(f"✓ Ollama conectado em {self.base_url}")
                # Lista modelos disponíveis
                modelos = [m.get("name", "?") for m in r.json().get("models", [])]
                print(f"  Modelos: {modelos}")
        except Exception as e:
            self.disponivel = False
            print(f"\n⚠️  Ollama não disponível")
            print(f"   Instalando Ollama:")
            print(f"   1. Acesse: https://ollama.com")
            print(f"   2. Baixe para Windows e instale")
            print(f"   3. Terminal: ollama pull mistral")
            print(f"   4. Terminal: ollama serve")
            print(f"   5. Reinicie este app")
            print(f"\n   Enquanto isso, o app funciona com respostas padrão.\n")

    def chat_marcador(self, nome_marcador: str, pergunta: str,
                     callback: Optional[Callable] = None) -> str:
        """
        Chat sobre um marcador específico

        Args:
            nome_marcador: Nome do marcador (ex: "ALT")
            pergunta: Pergunta do usuário
            callback: Função para atualizar UI em tempo real

        Returns:
            Resposta da IA
        """
        if not self.disponivel:
            return self._resposta_offline(nome_marcador, pergunta)

        prompt = f"""Você é um tutor de bioquímica clínica.
Está ajudando um estudante a entender o marcador bioquímico: {nome_marcador}

Pergunta do aluno: {pergunta}

Responda de forma:
- Clara e educacional
- Sem jargão muito técnico
- Com exemplos clínicos quando possível
- Citando valores de referência se relevante
- Máximo 200 palavras"""

        return self._gerar_resposta(prompt, callback)

    def quiz_dinamico(self, marcador: dict, callback: Optional[Callable] = None) -> dict:
        """
        Gera pergunta dinâmica sobre um marcador

        Args:
            marcador: Dict com dados do marcador
            callback: Função para atualizar UI

        Returns:
            Dict com pergunta, alternativas, resposta correta
        """
        if not self.disponivel:
            return self._quiz_offline(marcador)

        prompt = f"""Crie uma questão de múltipla escolha sobre o marcador bioquímico {marcador['nome']} ({marcador['sigla']}).

Dados do marcador:
- Categoria: {marcador['categoria']}
- Valor de referência: {marcador['valor_ref_min']}-{marcador['valor_ref_max']} {marcador['unidade']}
- Interpretação alta: {marcador['interpretacao_alta']}
- Interpretação baixa: {marcador['interpretacao_baixa']}

Gere em JSON:
{{
    "pergunta": "Texto da pergunta?",
    "alternativas": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "resposta_correta": 0,
    "explicacao": "Por que a resposta correta é..."
}}"""

        resposta = self._gerar_resposta(prompt, callback)
        try:
            # Extrai JSON da resposta
            inicio = resposta.find('{')
            fim = resposta.rfind('}') + 1
            if inicio >= 0 and fim > inicio:
                json_str = resposta[inicio:fim]
                return json.loads(json_str)
        except:
            pass

        return self._quiz_offline(marcador)

    def discussao_caso(self, caso: dict, diagnostico_usuario: str,
                       callback: Optional[Callable] = None) -> str:
        """
        Discussão socrática sobre diagnóstico

        Args:
            caso: Dict com dados do caso
            diagnostico_usuario: Diagnóstico que o aluno escolheu
            callback: Função para atualizar UI

        Returns:
            Feedback detalhado da IA
        """
        if not self.disponivel:
            return self._feedback_offline(caso, diagnostico_usuario)

        correto = diagnostico_usuario == caso["resposta_correta"]

        prompt = f"""Você é um médico professor. Um aluno analisou um caso clínico e seu diagnóstico foi:
"{diagnostico_usuario}"

Caso clínico:
Título: {caso['titulo']}
História: {caso['historia']}
Diagnóstico correto: {caso['resposta_correta']}
Explicação esperada: {caso['explicacao']}

{"ACERTOU! " if correto else "Está errado. "}
Forneça feedback educacional:
1. Se errou, explique onde errou
2. Mostre correlação entre exames e doença correta
3. Sugira próximas questões de estudo

Máximo 250 palavras, tom motivador."""

        return self._gerar_resposta(prompt, callback)

    def _gerar_resposta(self, prompt: str, callback: Optional[Callable] = None) -> str:
        """Gera resposta via Ollama com streaming"""
        try:
            resposta_completa = ""

            r = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "temperature": 0.7,
                },
                stream=True,
                timeout=60
            )

            if r.status_code == 200:
                for linha in r.iter_lines():
                    if linha:
                        try:
                            chunk = json.loads(linha)
                            texto = chunk.get("response", "")
                            resposta_completa += texto
                            if callback:
                                callback(texto)
                        except:
                            pass
                return resposta_completa.strip()
            else:
                return f"Erro {r.status_code}: {r.text}"

        except requests.exceptions.ConnectionError:
            print("✗ Não conseguiu conectar ao Ollama")
            print("  Instale: ollama pull mistral")
            print("  Execute: ollama serve")
            return "❌ Ollama não está rodando. Instale em ollama.com"
        except Exception as e:
            return f"❌ Erro: {e}"

    def _resposta_offline(self, nome_marcador: str, pergunta: str) -> str:
        """Resposta offline quando Ollama não está disponível"""
        return f"""ℹ️ Ollama não está disponível.

Para usar chat inteligente, instale Ollama:
1. Acesse: https://ollama.com
2. Baixe e instale
3. Abra terminal e execute: ollama pull mistral
4. Depois: ollama serve
5. Reabre este app

Enquanto isso, use o Modo Estudo para explorar {nome_marcador}."""

    def _quiz_offline(self, marcador: dict) -> dict:
        """Quiz offline - usa base de dados fixa"""
        return {
            "pergunta": f"Qual é a categoria do marcador {marcador['sigla']}?",
            "alternativas": [
                f"A) {marcador['categoria']}",
                "B) Categoria incorreta 1",
                "C) Categoria incorreta 2",
                "D) Categoria incorreta 3",
            ],
            "resposta_correta": 0,
            "explicacao": f"{marcador['nome']} ({marcador['sigla']}) pertence à categoria {marcador['categoria']}."
        }

    def _feedback_offline(self, caso: dict, diagnostico: str) -> str:
        """Feedback offline"""
        correto = diagnostico == caso["resposta_correta"]
        if correto:
            return f"✅ Diagnóstico correto!\n\n{caso['explicacao']}"
        else:
            return f"❌ Diagnóstico incorreto. O correto é: {caso['resposta_correta']}\n\n{caso['explicacao']}"

    def clear_historico(self):
        """Limpa histórico de chat"""
        self.historico_chat = []


# Instância global
ia = OllamaIA(model="mistral")
