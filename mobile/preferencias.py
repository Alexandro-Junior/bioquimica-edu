"""Preferências de leitura, foco e acessibilidade do estudante.

Ficam num JSON no próprio aparelho, ao lado do progresso. Nada aqui é
dado pessoal: são escolhas de interface.

O arquivo é tratado como entrada não confiável (pode ter sido editado à
mão ou corrompido): cada campo é validado contra a lista de valores
aceitos, e o que não passar volta ao padrão sem derrubar o app.
"""

import json
from pathlib import Path

# campo: (padrão, valores aceitos)
ESQUEMA = {
    "tema":                 ("padrao", ("padrao", "alto_contraste")),
    "fonte_leitura":        ("padrao", ("padrao", "hiperlegivel")),
    "escala_texto":         (1.0, (1.0, 1.15, 1.3, 1.5)),
    "movimento_reduzido":   (False, (True, False)),
    "modo_foco":            (False, (True, False)),
    "itens_por_sessao":     (12, (5, 12, 20)),
    "leitura_voz":          (False, (True, False)),
    "velocidade_voz":       (1.0, (0.8, 1.0, 1.25)),
    "atalho_libras":        (False, (True, False)),
    "relogio_jogo":         (False, (True, False)),   # tempo por rodada no "Alto, normal ou baixo?"
    "boas_vindas_vista":    (False, (True, False)),   # tutorial visto neste aparelho
    # "" = ainda não escolheu; a sessão do Google em si fica no cofre (conta.py)
    "modo_acesso":          ("", ("", "sem_conta", "google")),
}

ESCALAS_TEXTO = [(1.0, "Padrão"), (1.15, "Grande"), (1.3, "Maior"), (1.5, "Máximo")]
TAMANHOS_SESSAO = [(5, "Curta · 5"), (12, "Média · 12"), (20, "Longa · 20")]
VELOCIDADES_VOZ = [(0.8, "Devagar"), (1.0, "Normal"), (1.25, "Rápida")]


def padrao():
    return {chave: valor for chave, (valor, _) in ESQUEMA.items()}


def validar(dados):
    """Só passam chaves conhecidas com valores da lista; o resto é padrão."""
    limpo = padrao()
    if not isinstance(dados, dict):
        return limpo
    for chave, (_, aceitos) in ESQUEMA.items():
        valor = dados.get(chave)
        # bool é subclasse de int em Python: True == 1 não pode valer como escala
        if isinstance(valor, bool) != isinstance(aceitos[0], bool):
            continue
        if valor in aceitos:
            limpo[chave] = valor
    return limpo


class Preferencias:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.dados = self._carregar()

    def _carregar(self):
        try:
            with open(self.caminho, encoding="utf-8") as f:
                return validar(json.load(f))
        except FileNotFoundError:
            return padrao()
        except (OSError, ValueError) as e:
            print(f"[preferências] arquivo ilegível ({type(e).__name__}); usando o padrão")
            return padrao()

    def __getitem__(self, chave):
        return self.dados[chave]

    def definir(self, chave, valor):
        if chave not in ESQUEMA:
            raise KeyError(chave)
        novo = validar({**self.dados, chave: valor})
        if novo[chave] != valor:
            raise ValueError(f"valor inválido para {chave}: {valor!r}")
        self.dados = novo
        self.salvar()

    def salvar(self):
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            temporario = self.caminho.with_suffix(".tmp")
            with open(temporario, "w", encoding="utf-8") as f:
                json.dump(self.dados, f, ensure_ascii=False, indent=2)
            # troca atômica: um desligamento no meio não deixa o arquivo pela metade
            temporario.replace(self.caminho)
        except OSError as e:
            print(f"[preferências] não foi possível salvar: {e}")
