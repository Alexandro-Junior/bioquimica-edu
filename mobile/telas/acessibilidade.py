"""Acessibilidade: ajustes de leitura, voz, foco e Libras.

Cada ajuste responde a uma necessidade concreta, e a tela diz qual:
- tamanho do texto e alto contraste — baixa visão;
- leitura em voz alta, com velocidade — baixa visão e dificuldade de
  leitura (o Kivy não é lido por leitores de tela, então o app lê);
- modo foco e sessões curtas — TDAH e dificuldade de concentração;
- reduzir animações — sensibilidade a movimento e distração;
- atalho para o VLibras — pessoas surdas usuárias de Libras.

Os ajustes valem na hora e ficam só neste aparelho.
"""

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from mobile import componentes as C
from mobile.preferencias import ESCALAS_TEXTO, TAMANHOS_SESSAO, VELOCIDADES_VOZ
from mobile.tema import COR
from mobile.telas.base import TelaBase


def secao(titulo, descricao=None):
    caixa = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4),
                      padding=(dp(2), dp(10), 0, dp(2)))
    caixa.bind(minimum_height=caixa.setter("height"))
    caixa.add_widget(C.Texto(text=titulo.upper(), estilo="secao"))
    if descricao:
        caixa.add_widget(C.Texto(text=descricao, estilo="apoio"))
    return caixa


def ajustes_leitura(app, cartao):
    """Tamanho do texto e contraste (também usados na apresentação)."""
    prefs = app.prefs
    cartao.add_widget(C.Texto(text="Tamanho do texto", estilo="corpo", bold=True))
    cartao.add_widget(C.Segmentado(
        ESCALAS_TEXTO, prefs["escala_texto"],
        lambda v: app.mudar_preferencia("escala_texto", v)))
    cartao.add_widget(C.Texto(text="Exemplo: Potássio, referência 3,5 – 5 mEq/L.",
                              estilo="apoio"))
    cartao.add_widget(C.Divisor())
    cartao.add_widget(C.Alternador(
        "Alto contraste", "Preto no branco, com contornos bem marcados.",
        ativo=prefs["tema"] == "alto_contraste", icone="contraste",
        ao_mudar=lambda v: app.mudar_preferencia(
            "tema", "alto_contraste" if v else "padrao")))
    cartao.add_widget(C.Divisor())
    cartao.add_widget(C.Alternador(
        "Fonte para leitura facilitada",
        "Atkinson Hyperlegible, feita para baixa visão: letras que não se "
        "confundem, como I, l e 1 ou O e 0.",
        ativo=prefs["fonte_leitura"] == "hiperlegivel", icone="texto",
        ao_mudar=lambda v: app.mudar_preferencia(
            "fonte_leitura", "hiperlegivel" if v else "padrao")))


def ajustes_voz(app, cartao):
    prefs = app.prefs
    disponivel = app.voz is not None and app.voz.disponivel
    alternador = C.Alternador(
        "Leitura em voz alta",
        "Mostra o botão Ouvir nas perguntas, respostas e no tutor.",
        ativo=prefs["leitura_voz"] and disponivel, icone="voz",
        ao_mudar=lambda v: (app.mudar_preferencia("leitura_voz", v),
                            app.tela_atual().preparar(**app.tela_atual().parametros)))
    alternador.disabled = not disponivel
    cartao.add_widget(alternador)
    if not disponivel:
        cartao.add_widget(C.Aviso(
            "Este aparelho não tem uma voz de leitura instalada. No Android, "
            "instale ou ative a voz em Configurações › Acessibilidade › "
            "Saída de texto para voz.", tipo="atencao"))
        return
    if prefs["leitura_voz"]:
        cartao.add_widget(C.Texto(text="Velocidade da voz", estilo="corpo", bold=True))
        cartao.add_widget(C.Segmentado(
            VELOCIDADES_VOZ, prefs["velocidade_voz"],
            lambda v: app.mudar_preferencia("velocidade_voz", v)))
        testar = C.Botao("Testar a voz", variante="neutro", icone="voz", height=dp(46),
                         tamanho_fonte="14sp")
        testar.bind(on_release=lambda *_: app.falar(
            "Potássio. Faixa de referência: três vírgula cinco a cinco miliequivalentes "
            "por litro."))
        cartao.add_widget(testar)


def ajustes_foco(app, cartao):
    prefs = app.prefs
    cartao.add_widget(C.Alternador(
        "Modo foco",
        "O Início mostra só o que estudar agora. O resto do progresso fica a um toque.",
        ativo=prefs["modo_foco"], icone="foco",
        ao_mudar=lambda v: app.mudar_preferencia("modo_foco", v)))
    cartao.add_widget(C.Divisor())
    cartao.add_widget(C.Texto(text="Tamanho da sessão de revisão", estilo="corpo", bold=True))
    cartao.add_widget(C.Texto(text="Sessões curtas são mais fáceis de terminar sem "
                                   "perder a concentração.", estilo="apoio"))
    cartao.add_widget(C.Segmentado(
        TAMANHOS_SESSAO, prefs["itens_por_sessao"],
        lambda v: app.mudar_preferencia("itens_por_sessao", v)))
    cartao.add_widget(C.Divisor())
    cartao.add_widget(C.Alternador(
        "Reduzir animações", "Troca transições e efeitos por mudanças instantâneas.",
        ativo=prefs["movimento_reduzido"], icone="movimento",
        ao_mudar=lambda v: app.mudar_preferencia("movimento_reduzido", v)))


class TelaAcessibilidade(TelaBase):

    LARGURA_MAXIMA = 720   # dp, em tablet e computador

    def montar(self, **_):
        app = self.app
        raiz = BoxLayout(orientation="vertical")
        raiz.add_widget(C.Cabecalho("Acessibilidade", ao_voltar=app.voltar,
                                    subtitulo="Ajustes deste aparelho"))
        scroll, col = C.coluna_rolavel(padding=(dp(16), dp(2), dp(16), dp(28)),
                                       spacing=dp(10))

        col.add_widget(secao("Leitura", "Para enxergar melhor o conteúdo."))
        leitura = C.Cartao(spacing=dp(12))
        ajustes_leitura(app, leitura)
        col.add_widget(leitura)

        col.add_widget(secao("Ouvir o conteúdo",
                             "O app lê em voz alta com a voz do próprio aparelho, sem internet."))
        voz = C.Cartao(spacing=dp(12))
        ajustes_voz(app, voz)
        col.add_widget(voz)

        col.add_widget(secao("Atenção e foco", "Menos informação ao mesmo tempo."))
        foco = C.Cartao(spacing=dp(12))
        ajustes_foco(app, foco)
        col.add_widget(foco)

        col.add_widget(secao("Libras"))
        libras = C.Cartao(spacing=dp(12))
        libras.add_widget(C.Alternador(
            "Atalho para o VLibras",
            "Mostra o botão Libras no estudo e no tutor: ele abre o VLibras, do Governo "
            "Federal, no navegador, que traduz o texto para Libras com um avatar. Precisa "
            "de internet.",
            ativo=app.prefs["atalho_libras"], icone="libras",
            ao_mudar=lambda v: app.mudar_preferencia("atalho_libras", v)))
        col.add_widget(libras)

        col.add_widget(C.Aviso(
            "Leitores de tela como o TalkBack ainda não conseguem ler apps feitos com "
            "Kivy, a tecnologia deste app. Por isso a leitura em voz alta é feita "
            "pelo próprio app.", tipo="info", titulo="Sobre leitores de tela"))

        rever = C.Botao("Rever a apresentação", variante="neutro", icone="repetir")
        rever.bind(on_release=lambda *_: app.ir_para("boas_vindas", passo=1))
        col.add_widget(rever)
        col.add_widget(C.Texto(text="Seus ajustes e seu progresso ficam somente neste "
                                    "aparelho. O app não cria conta nem envia dados.",
                               estilo="micro", halign="center"))

        raiz.add_widget(scroll)
        self.add_widget(raiz)
        self.coluna = col
