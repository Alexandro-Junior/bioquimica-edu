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
os.environ["BIOQ_SEM_NUVEM"] = "1"   # o tutor não chama o Gemini (test_tutor.py cobre)


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

    @passo("abertura leva à tela de acesso no primeiro uso")
    def _():
        assert app.carregado, "o conteúdo deveria ter carregado na abertura"
        esperar_tela("acesso")
        assert app.navegacao.opacity == 0, "a tela de acesso não mostra a barra de abas"
        assert app.acesso.precisa_escolher()
        # sem config/firebase.json (BIOQ_SEM_NUVEM), o Google aparece desligado
        assert tela().botao_google.disabled
        tela()._usar_sem_conta()
        esperar_tela("boas_vindas")

    @passo("tutorial: quatro passos, com pular, e não volta na próxima abertura")
    def _():
        assert procurar(tela(), lambda w: getattr(w, "text", "") == "Pular") is not None
        for n in (2, 3, 4):
            tela().preparar(passo=n)
        tela()._concluir()
        esperar_tela("inicio")
        assert app.prefs["boas_vindas_vista"], "o tutorial deveria ficar marcado como visto"
        assert app.prefs["modo_acesso"] == "sem_conta"
        assert app._destino_inicial() == "inicio", "a próxima abertura repetiria o fluxo"
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

    @passo("estudo: TFGe com calculadora, bicarbonato e bilirrubinas aprofundados")
    def _():
        app.ir_para("estudo", animar=False)
        t = tela()
        t._escolher("Renal")
        assert len(t.lista.children) == 4, "Renal: creatinina, ureia, ácido úrico e TFGe"
        app.ir_para("detalhe", sigla="TFGe", animar=False)
        t = tela()
        t.campo_creatinina.campo.text = "1,9"
        t.campo_idade.campo.text = "62"
        t.sexo_tfg = "M"
        assert t.calcular_tfg() == 39
        assert procurar(t.resultado_tfg, lambda w: "G3b" in getattr(w, "text", ""))
        assert procurar(t.resultado_tfg, lambda w: w.__class__.__name__ == "ReguaFaixas")
        t.campo_idade.campo.text = "15"
        assert t.calcular_tfg() is None, "menor de 18 anos deveria ser recusado"
        assert procurar(t.resultado_tfg, lambda w: "adultos" in getattr(w, "text", ""))
        app.voltar()
        for sigla, trecho in (("HCO3", "Ânion gap"), ("BT", "Bilirrubina direta e indireta")):
            app.ir_para("detalhe", sigla=sigla, animar=False)
            assert procurar(tela(), lambda w, x=trecho: getattr(w, "text", "") == x), sigla
            app.voltar()

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

    @passo("prática: jogo 'Alto, normal ou baixo?' completo, com dica e relógio")
    def _():
        from jogos import RODADAS, classificar
        from progresso import Progresso
        app.ir_para("jogos", animar=False)   # atalho do Início
        esperar_tela("pratica")
        t = tela()
        assert t.modo == "jogos"
        t.iniciar_faixas()
        siglas = {m["sigla"]: m for m in app.marcadores}
        tentativas_antes = {s: app.progresso.estado(s)["tentativas"] for s in siglas}
        for i in range(RODADAS):
            r = t.rodadas[t.rodada]
            m = siglas[r["sigla"]]
            certa = classificar(r["valor"], m["valor_ref_min"], m["valor_ref_max"])
            assert certa == r["classe"], (r, certa)
            if i == 0:
                t._mostrar_dica(m)
                assert t.usou_dica
            t.responder_faixas(certa)
            regua = procurar(t.col, lambda w: w.__class__.__name__ == "ReguaFaixas")
            assert regua is not None, "o retorno deveria mostrar a régua da faixa"
            t._avancar_faixas()
        assert t.acertos_jogo == RODADAS and t.melhor_sequencia == RODADAS
        assert t.pontos == 5 + sum(min(10 + 5 * (n - 1), 30) for n in range(2, RODADAS + 1))
        assert procurar(tela(), lambda w: getattr(w, "text", "") == "Jogar de novo")
        assert Progresso().recorde("faixas") == t.pontos, "o recorde não foi salvo"
        # a rodada com dica não conta para a revisão; as outras contam
        primeira = t.rodadas[0]["sigla"]
        contadas = [s for s in siglas
                    if app.progresso.estado(s)["tentativas"] > tentativas_antes[s]]
        assert primeira not in contadas and len(contadas) == RODADAS - 1, contadas

        # relógio ligado: o tempo esgotado conta como erro, sem ir para a revisão
        app.prefs.definir("relogio_jogo", True)
        try:
            t.iniciar_faixas()
            assert t.barra_tempo is not None and t._relogio is not None
            sigla = t.rodadas[0]["sigla"]
            antes = app.progresso.estado(sigla)["tentativas"]
            t._tique(100)
            assert t.respondido and t.sequencia == 0 and t.errados == [sigla]
            assert t._relogio is None
            assert app.progresso.estado(sigla)["tentativas"] == antes
            t._avancar_faixas()
            assert t._relogio is not None
            app.ir_para("inicio", animar=False)   # sair da aba para o relógio
            assert t._relogio is None, "o relógio continuou correndo fora da Prática"
        finally:
            app.prefs.definir("relogio_jogo", False)

    @passo("prática: jogo da memória completo")
    def _():
        from jogos import forma_par
        from progresso import Progresso
        app.ir_para("pratica", modo="jogos", animar=False)
        t = tela()
        t.iniciar_memoria()
        cartas = t.cartas
        # um erro de propósito: duas cartas que não formam par
        i = 0
        j = next(k for k in range(1, len(cartas)) if not forma_par(cartas[0], cartas[k]))
        t.virar_carta(i)
        t.virar_carta(j)
        assert t.travado and t.jogadas == 1
        t.virar_carta(next(k for k in range(len(cartas)) if k not in (i, j)))
        assert t.jogadas == 1, "com duas cartas viradas, a mesa deveria estar travada"
        t._parar_jogos()
        t._desvirar()
        assert not t.viradas and not t.travado
        feitos = set()
        for a in range(len(cartas)):
            if a in feitos:
                continue
            b = next(k for k in range(len(cartas)) if forma_par(cartas[a], cartas[k]))
            t.virar_carta(a)
            t.virar_carta(b)
            feitos |= {a, b}
            assert t.widgets_cartas[a].com_par and t.widgets_cartas[b].com_par
        assert len(t.encontradas) == len(cartas)
        assert t.jogadas == 1 + len(cartas) // 2
        t._parar_jogos()            # em vez de esperar o 1,2 s até o resultado
        t._resultado_memoria()
        assert procurar(tela(), lambda w: getattr(w, "text", "") == "Todos os pares!")
        assert Progresso().recorde("memoria") == t.jogadas

    @passo("tutor: pergunta respondida pela base")
    def _():
        app.ir_para("tutor", animar=False)
        antes = len(tela().conversa.children)
        tela()._perguntar("Troponina")
        assert len(tela().conversa.children) > antes, "a pergunta não entrou na conversa"
        assert not tela().assistente.provedores[0].disponivel(), \
            "com BIOQ_SEM_NUVEM o tutor não deveria chamar o Gemini"
        if not tela().com_ia:   # sem Ollama a resposta é imediata
            assert tela().historico[-2] == ("usuario", "Troponina"), tela().historico

    @passo("tutor: modelo que falha cai para a base, com aviso")
    def _():
        from assistente import Assistente, BaseLocal

        class Quebrado:
            nome = "modelo de teste"

            def disponivel(self):
                return True

            def responder(self, pergunta, marcador, historico=None):
                raise ConnectionError("sem rede")

        k = next(m for m in app.marcadores if m["sigla"] == "K")
        texto, fonte, aviso = Assistente([Quebrado(), BaseLocal(app.marcadores)]).responder(
            "potássio alto", k)
        assert fonte == "base do app" and "Potássio" in texto and aviso, (fonte, aviso)
        # "foi" contém "oi", mas não é cumprimento
        resposta = BaseLocal(app.marcadores).responder("o que foi isso?", None)
        assert "Olá" not in resposta, resposta

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
        for nome in ("inicio", "estudo", "cartas", "pratica", "tutor", "revisao", "conta",
                     "acesso", "boas_vindas"):
            app.ir_para(nome, animar=False)
            esperar_tela(nome)
        app.voltar()
        app.ir_para("detalhe", sigla="K", animar=False)
        app.voltar()
        app.ir_para("detalhe", sigla="TFGe", animar=False)   # calculadora com letra grande
        tela().campo_creatinina.campo.text = "1"
        tela().campo_idade.campo.text = "40"
        assert tela().calcular_tfg() is not None
        app.voltar()
        # os jogos também, com relógio, régua e cartas
        app.prefs.definir("relogio_jogo", True)
        app.ir_para("jogos", animar=False)
        tela().iniciar_faixas()
        tela().responder_faixas("alto")
        tela().iniciar_memoria()
        tela().virar_carta(0)
        app.prefs.definir("relogio_jogo", False)
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
        assert abertos and abertos[-1].startswith("https://bioquimicaedu.web.app/libras#t="), abertos
        from urllib.parse import unquote
        assert unquote(abertos[-1].split("#t=", 1)[1]).startswith("Potássio. Faixa"), abertos[-1]
        # texto longo: cortado numa frase inteira, para o endereço não ficar grande demais
        from mobile.app import LIMITE_LIBRAS, endereco_libras
        longo = endereco_libras("Frase de teste com conteúdo. " * 60)
        assert len(unquote(longo.split("#t=", 1)[1])) <= LIMITE_LIBRAS + 2, len(longo)

    @passo("tamanho da tela: barra no celular, menu lateral no tablet/PC, sessão preservada")
    def _():
        from kivy.base import EventLoop
        from kivy.core.window import Window
        from mobile.componentes import BarraNavegacao, TrilhoNavegacao

        def redimensionar(tamanho):
            # o novo tamanho só vale depois que a janela processa o evento
            alvo_px = None
            Window.size = tamanho
            for _ in range(30):
                EventLoop.idle()
                if alvo_px == tuple(Window.size):
                    break
                alvo_px = tuple(Window.size)
            app._reavaliar_formato(0)

        original = tuple(Window.size)
        app.ir_para("inicio", animar=False)
        app.ir_para("revisao", animar=False)
        t = tela()
        t._definir_confianca(3)
        t._revelar()
        # celular, tablet em pé, computador — como girar o tablet no meio da revisão
        for largura, altura, trilho in ((400, 840, False), (720, 1000, True), (1180, 760, True)):
            redimensionar((largura, altura))
            assert app.trilho is trilho, (largura, Window.size, app.trilho)
            assert isinstance(app.navegacao, TrilhoNavegacao if trilho else BarraNavegacao)
            assert tela() is t and t.revelado, "a revisão em andamento se perdeu"
        redimensionar(original)
        app.voltar()
        esperar_tela("inicio")
        assert app.navegacao.opacity == 1, "a navegação deveria voltar visível"

    @passo("conta: Google (simulado) em outro aparelho pula o tutorial já visto; sair volta ao acesso")
    def _():
        import threading
        import time as relogio

        import autenticacao as A
        from kivy.base import EventLoop
        from mobile.conta import Acesso
        from mobile.preferencias import Preferencias

        nuvem = {"uid-9": {"tutorial_visto": True}}   # visto no celular, dias atrás

        class NuvemFalsa:
            def entrar(self, _token, _nonce):
                return A.Sessao("uid-9", "ana@exemplo.com", "Ana Souza", "renova",
                                token_acesso="acesso", expira_em=relogio.time() + 3600)

            def renovar(self, sessao):
                return sessao

            def ler_aluno(self, sessao):
                return dict(nuvem.get(sessao.uid, {}))

            def marcar_tutorial(self, sessao):
                nuvem.setdefault(sessao.uid, {})["tutorial_visto"] = True

        cfg = {"apiKey": "k", "projectId": "p", "webClientId": "w.apps.googleusercontent.com",
               "desktopClientId": "d.apps.googleusercontent.com", "desktopClientSecret": "s"}
        computador = PASTA_TESTE / "outro_aparelho"   # aparelho novo: nada salvo nele
        original = app.acesso
        app.acesso = Acesso(Preferencias(computador / "preferencias_mobile.json"), computador,
                            cfg=cfg, obter_token=lambda _c=None: ("token", "nonce"),
                            firebase=NuvemFalsa())
        app.acesso.em_segundo_plano = lambda fn: fn()
        try:
            app.ir_para("acesso", animar=False)
            assert not tela().botao_google.disabled, "com configuração, o Google fica ativo"
            evento = threading.Event()
            tela().cancelar = evento
            tela()._login(evento)            # o que a thread faria
            for _ in range(10):
                EventLoop.idle()             # entrega o resultado à tela, como o Clock faria
            esperar_tela("inicio")           # tutorial visto na conta: pula direto
            assert app.acesso.conectado and (computador / "sessao_google.dat").exists()

            app.ir_para("conta", animar=False)
            assert procurar(tela(), lambda w: getattr(w, "text", "") == "Ana Souza")
            tela()._confirmar()
            tela()._sair()
            esperar_tela("acesso")
            assert not app.acesso.conectado and not (computador / "sessao_google.dat").exists()
            assert app.progresso.estado(app.marcadores[0]["sigla"]) is not None
        finally:
            app.acesso = original
            app.ir_para("inicio", animar=False)

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
