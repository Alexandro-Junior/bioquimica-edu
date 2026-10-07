#!/usr/bin/env python3
"""
Teste de fumaça da versão mobile: abre o app de verdade e usa cada tela.

Importar o módulo não basta — a versão mobile antiga importava sem erro
e mesmo assim fechava ao abrir. Este teste monta o app, passa pela
abertura e pela apresentação de primeiro acesso, navega por todas as
telas e exercita os fluxos principais (revisão, cards, quiz, caso
clínico, tutor, detalhe de marcador e o botão voltar) e os recursos de
acessibilidade (texto grande, alto contraste, modo foco, voz e Libras).

O progresso e as preferências do teste ficam numa pasta temporária
própria (BIOQ_PASTA_ALUNO): os arquivos reais do estudante nunca são
lidos, movidos nem gravados — nem se o teste for interrompido no meio.
A voz é substituída por uma falsa que só registra o texto, e o navegador
não é aberto de verdade.

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
PASTA_TESTE = Path(tempfile.mkdtemp(prefix="bioquimicaedu_teste_"))
os.environ["BIOQ_PASTA_ALUNO"] = str(PASTA_TESTE)   # antes de importar progresso
os.environ["BIOQ_SEM_VOZ"] = "1"   # nada de falar alto durante o teste


class VozFalsa:
    disponivel = True

    def __init__(self):
        self.falado = []

    def falar(self, texto, velocidade=1.0):
        self.falado.append(texto)

    def parar(self):
        pass


def procurar(widget, condicao):
    """Primeiro widget da árvore que satisfaz a condição."""
    if condicao(widget):
        return widget
    for filho in widget.children:
        achado = procurar(filho, condicao)
        if achado is not None:
            return achado
    return None


def main():
    from kivy.clock import Clock
    from mobile import app as modulo_app
    from mobile import tema
    from mobile.app import BioquimicaApp

    abertos = []
    modulo_app.webbrowser.open = lambda url: abertos.append(url)

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

    @passo("abertura leva à apresentação no primeiro acesso")
    def _():
        assert app.carregado, "o conteúdo deveria ter carregado na abertura"
        esperar_tela("boas_vindas")
        assert app.navegacao.opacity == 0, "a apresentação não mostra a barra de abas"
        for n in (2, 3):
            tela().preparar(passo=n)
        tela()._concluir()
        esperar_tela("inicio")
        assert app.prefs["boas_vindas_vista"], "a apresentação deveria ficar marcada como vista"
        app.voz = VozFalsa()

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
        assert len(t.fila) <= app.prefs["itens_por_sessao"]
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

    @passo("prática: caso clínico, resolvido e salvo")
    def _():
        from progresso import Progresso
        app.ir_para("pratica", modo="casos", animar=False)
        caso = app.casos[0]
        tela().abrir_caso(caso)
        tela().responder_caso(caso["resposta_correta"], caso)
        assert caso["id"] in app.casos_resolvidos
        # antes, os casos resolvidos sumiam ao fechar o app
        assert caso["id"] in Progresso().casos_resolvidos(), "o caso não foi salvo"

    @passo("tutor: pergunta respondida pela base")
    def _():
        app.ir_para("tutor", animar=False)
        antes = len(tela().conversa.children)
        tela()._perguntar("Troponina")
        assert len(tela().conversa.children) > antes, "a pergunta não entrou na conversa"

    @passo("tutor: modelo que falha cai para a base, com aviso")
    def _():
        from assistente import Assistente, BaseLocal

        class Quebrado:
            nome = "modelo de teste"

            def disponivel(self):
                return True

            def responder(self, pergunta, marcador):
                raise ConnectionError("sem rede")

        k = next(m for m in app.marcadores if m["sigla"] == "K")
        texto, fonte, aviso = Assistente([Quebrado(), BaseLocal(app.marcadores)]).responder(
            "potássio alto", k)
        assert fonte == "base do app" and "Potássio" in texto and aviso, (fonte, aviso)
        # "foi" contém "oi", mas não é cumprimento
        resposta = BaseLocal(app.marcadores).responder("o que foi isso?", None)
        assert "Olá" not in resposta, resposta

    @passo("tutor: resposta atrasada não invade a conversa remontada")
    def _():
        import threading
        from assistente import Assistente, BaseLocal

        liberar = threading.Event()

        class Lento:
            nome = "modelo lento"

            def disponivel(self):
                return True

            def responder(self, pergunta, marcador):
                liberar.wait(5)
                return "resposta atrasada"

        app.ir_para("tutor", animar=False)
        tela().assistente = Assistente([Lento(), BaseLocal(app.marcadores)])
        tela()._perguntar("Troponina")
        assert tela().ocupado, "a pergunta ao modelo não ficou pendente"
        conversa_antiga = tela().conversa
        linha = conversa_antiga.children[0]          # o indicador "digitando"
        digitando = linha.children[-1]

        tela().preparar()                            # troca de aba / de ajuste
        nova = tela().conversa
        antes = len(nova.children)
        tela()._entregar("resposta atrasada", "modelo lento", None,
                         conversa_antiga, linha, digitando)
        liberar.set()
        assert len(nova.children) == antes, "a resposta antiga entrou na conversa nova"
        assert not tela().ocupado, "a conversa nova ficou travada como ocupada"

    @passo("acessibilidade: texto grande, alto contraste e menos movimento")
    def _():
        app.ir_para("inicio", animar=False)
        app.ir_para("acessibilidade", animar=False)
        app.mudar_preferencia("escala_texto", 1.5)
        esperar_tela("acessibilidade")
        assert tema.escala() >= 1.5 - 1e-6, tema.escala()
        app.mudar_preferencia("tema", "alto_contraste")
        assert tuple(tema.COR["fundo"][:3]) == (1.0, 1.0, 1.0), tema.COR["fundo"]
        app.mudar_preferencia("movimento_reduzido", True)
        assert not tema.movimento()
        # todas as telas precisam montar com as três opções ligadas juntas
        for nome in ("inicio", "estudo", "cartas", "pratica", "tutor", "revisao"):
            app.ir_para(nome, animar=False)
            esperar_tela(nome)
        app.voltar()
        app.ir_para("detalhe", sigla="K", animar=False)
        app.voltar()
        for chave, valor in (("escala_texto", 1.0), ("tema", "padrao"),
                             ("movimento_reduzido", False)):
            app.mudar_preferencia(chave, valor)
        assert tema.escala() < 1.01 and tema.movimento()

    @passo("modo foco: o Início mostra só o essencial")
    def _():
        app.mudar_preferencia("modo_foco", True)
        app.ir_para("inicio", animar=False)
        botao = procurar(tela(), lambda w: getattr(w, "text", "") == "Ver meu progresso")
        assert botao is not None, "o modo foco deveria oferecer 'Ver meu progresso'"
        tela().preparar(expandido=True)
        assert procurar(tela(), lambda w: getattr(w, "text", "") == "Constância")
        app.mudar_preferencia("modo_foco", False)

    @passo("voz: o botão Ouvir lê a pergunta da revisão")
    def _():
        app.mudar_preferencia("leitura_voz", True)
        app.ir_para("revisao", animar=False)
        ouvir = procurar(tela(), lambda w: getattr(w, "descricao", "") == "Ler em voz alta")
        assert ouvir is not None, "com a voz ligada, a revisão deveria ter o botão Ouvir"
        ouvir.dispatch("on_release")
        assert app.voz.falado and "faixa de referência" in app.voz.falado[-1].lower()
        app.voltar()
        app.mudar_preferencia("leitura_voz", False)

    @passo("Libras: o texto vai para a área de transferência")
    def _():
        from kivy.core.clipboard import Clipboard
        app.abrir_libras("Potássio. Faixa de referência: 3,5 a 5 mEq/L.")
        assert Clipboard.paste().startswith("Potássio"), Clipboard.paste()
        assert abertos and "vlibras" in abertos[-1].lower(), abertos

    @passo("preferências corrompidas voltam ao padrão")
    def _():
        from mobile.preferencias import padrao, validar
        assert validar({"escala_texto": True, "tema": "<script>", "extra": 1}) == padrao()
        assert validar("lixo") == padrao()
        assert validar({"itens_por_sessao": 5})["itens_por_sessao"] == 5

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

    # Espera a abertura terminar. Um atraso fixo não serve: o relógio do
    # Kivy fica parado enquanto a janela é criada, e um agendamento feito
    # antes disso dispara logo no primeiro quadro, ainda na abertura.
    def aguardar(_dt, tentativas=[0]):
        tentativas[0] += 1
        pronto = app.carregado and app.gerenciador.has_screen("inicio")
        if pronto or tentativas[0] > 100:
            Clock.schedule_once(rodar, 0.5)   # meio segundo para o layout assentar
        else:
            Clock.schedule_once(aguardar, 0.2)

    Clock.schedule_once(aguardar, 0.2)
    try:
        app.run()
    finally:
        shutil.rmtree(PASTA_TESTE, ignore_errors=True)

    print()
    print(f"{len(falhas)} falha(s): {falhas}" if falhas else "TODOS OS PASSOS PASSARAM")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
