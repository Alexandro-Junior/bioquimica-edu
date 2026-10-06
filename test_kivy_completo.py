#!/usr/bin/env python3
"""
Teste de fumaça da versão mobile: abre o app de verdade e usa cada tela.

Importar o módulo não basta — a versão mobile antiga importava sem erro
e mesmo assim fechava ao abrir. Este teste monta o app, navega por todas
as telas e exercita os fluxos principais (revisão, cards, quiz, caso
clínico, tutor, detalhe de marcador e o botão voltar).

O progresso real do estudante (data/progresso.json) é salvo antes e
restaurado no fim: os passos respondem questões e gravariam no arquivo.

Uso:  python test_kivy_completo.py
Sai com código 0 se tudo passar e 1 se algum passo falhar.
"""

import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
os.chdir(BASE)

PROGRESSO = BASE / "data" / "progresso.json"
COPIA = Path(tempfile.gettempdir()) / "bioquimicaedu_progresso_backup.json"


def main():
    existia = PROGRESSO.exists()
    if existia:
        shutil.copy(PROGRESSO, COPIA)
        PROGRESSO.unlink()   # começa de um estudante novo

    from kivy.clock import Clock
    from mobile.app import BioquimicaApp

    app = BioquimicaApp()
    falhas = []
    passos = []

    def passo(nome):
        def registrar(fn):
            passos.append((nome, fn))
            return fn
        return registrar

    def tela():
        return app.tela_atual()

    def esperar_tela(nome):
        atual = app.gerenciador.current
        assert atual == nome, f"esperava a tela '{nome}', está em '{atual}'"

    @passo("abrir todas as abas")
    def _():
        for nome in ("inicio", "estudo", "cartas", "pratica", "tutor"):
            app.ir_para(nome, animar=False)
            esperar_tela(nome)

    @passo("estudo: busca, filtro e detalhe com abas")
    def _():
        app.ir_para("estudo", animar=False)
        t = tela()
        t.busca.campo.text = "potássio"
        assert len(t.lista.children) == 1, "a busca deveria achar só o potássio"
        t.busca.campo.text = ""
        t._escolher("Cardíaco")
        assert len(t.lista.children) == 3, "Cardíaco tem CK-MB, troponina e LDH"
        app.ir_para("detalhe", sigla="K", animar=False)
        for chave, _rotulo in tela().abas:
            tela().mostrar_aba(chave)
        app.voltar()
        esperar_tela("estudo")

    @passo("revisão: confiança, resposta e autoavaliação")
    def _():
        # a revisão começa pelo botão do Início, e o voltar retorna para lá
        app.ir_para("inicio", animar=False)
        app.ir_para("revisao", animar=False)
        t = tela()
        assert t.fila, "um estudante novo deveria ter marcadores para estudar"
        sigla = t.fila[0]
        t._definir_confianca(4)
        t._revelar()
        t._responder(4)
        assert app.progresso.estado(sigla)["tentativas"] == 1
        app.voltar()
        esperar_tela("inicio")

    @passo("cards: virar e avaliar")
    def _():
        app.ir_para("cartas", animar=False)
        t = tela()
        t._virar()
        assert t.area_avaliacao.children, "a autoavaliação deveria aparecer"
        t._avaliar(True)
        assert t.aviso.text, "o efeito da avaliação deveria aparecer"

    @passo("prática: quiz completo")
    def _():
        app.ir_para("quiz", animar=False)   # nome antigo, mantido por compatibilidade
        t = tela()
        for _ in range(len(t.perguntas)):
            p = t.perguntas[t.indice]
            t.responder_quiz(p["resposta_correta"], p)
            t._avancar()
        assert t.acertos == len(t.perguntas)

    @passo("prática: caso clínico")
    def _():
        app.ir_para("pratica", modo="casos", animar=False)
        caso = app.casos[0]
        tela().abrir_caso(caso)
        tela().responder_caso(caso["resposta_correta"], caso)
        assert caso["id"] in app.casos_resolvidos

    @passo("tutor: pergunta respondida pela base")
    def _():
        app.ir_para("tutor", animar=False)
        antes = len(tela().conversa.children)
        tela()._perguntar("Troponina")
        assert len(tela().conversa.children) > antes, "a pergunta não entrou na conversa"

    @passo("painel reflete a sessão")
    def _():
        app.ir_para("inicio", animar=False)
        siglas = [m["sigla"] for m in app.marcadores]
        categorias = {m["sigla"]: m["categoria"] for m in app.marcadores}
        resumo = app.progresso.resumo(siglas, categorias)
        assert resumo["revisados_hoje"] >= 3, resumo["revisados_hoje"]

    def rodar(_dt):
        for nome, fn in passos:
            try:
                fn()
                print(f"ok     {nome}")
            except Exception as e:
                falhas.append(nome)
                print(f"FALHA  {nome}: {type(e).__name__}: {e}")
                traceback.print_exc()
        app.stop()

    # alguns segundos para o primeiro layout terminar
    Clock.schedule_once(rodar, 3)
    try:
        app.run()
    finally:
        if PROGRESSO.exists():
            PROGRESSO.unlink()
        if existia:
            shutil.copy(COPIA, PROGRESSO)

    print()
    print(f"{len(falhas)} falha(s): {falhas}" if falhas else "TODOS OS PASSOS PASSARAM")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
