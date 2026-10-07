"""Tela Conta: com quem o app está conectado, rever a apresentação e sair.

Aberta pelo ícone de pessoa no topo do Início. Sair da conta pede
confirmação e deixa claro que o progresso de estudo continua no aparelho.
"""

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from mobile import componentes as C
from mobile.tema import COR
from mobile.telas.acesso import BotaoGoogle
from mobile.telas.base import TelaBase


class TelaConta(TelaBase):

    LARGURA_MAXIMA = 640   # dp, em tablet e computador

    def montar(self, **_):
        acesso = self.app.acesso
        raiz = BoxLayout(orientation="vertical")
        raiz.add_widget(C.Cabecalho("Conta", ao_voltar=self.app.voltar,
                                    subtitulo="Acesso e apresentação"))
        scroll, col = C.coluna_rolavel(spacing=dp(14))

        quem = C.Cartao(spacing=dp(12))
        linha = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(14))
        linha.add_widget(C.SeloIcone("pessoa", cor_fundo=COR["acento_suave"],
                                     cor_icone=COR["acento_escuro"], tamanho=dp(52),
                                     pos_hint={"center_y": 0.5}))
        textos = BoxLayout(orientation="vertical")
        if acesso.conectado:
            nome = acesso.sessao.nome or "Conta Google"
            textos.add_widget(C.rotulo(nome, "17sp", COR["tinta"], negrito=True, vertical="bottom"))
            textos.add_widget(C.rotulo(acesso.sessao.email, "13.5sp", COR["tinta2"], vertical="top"))
        else:
            textos.add_widget(C.rotulo("Usando sem conta", "17sp", COR["tinta"], negrito=True,
                                       vertical="bottom"))
            textos.add_widget(C.rotulo("Tudo fica salvo neste aparelho", "13.5sp", COR["tinta2"],
                                       vertical="top"))
        linha.add_widget(textos)
        quem.add_widget(linha)
        if acesso.conectado:
            quem.add_widget(C.Texto(
                text="Você entrou com o Google. A apresentação que você já viu fica "
                     "registrada na sua conta e vale em qualquer aparelho.", estilo="apoio"))
        else:
            quem.add_widget(C.Texto(
                text="Entre com o Google para o app lembrar de você no computador, no "
                     "tablet e no celular. Nada do que você já estudou se perde.",
                estilo="apoio"))
            entrar = BotaoGoogle()
            entrar.disabled = not acesso.google_disponivel()
            entrar.bind(on_release=lambda *_: self.app.ir_para("acesso"))
            quem.add_widget(entrar)
        col.add_widget(quem)

        if acesso.sessao_encerrada:
            col.add_widget(C.Aviso("Sua sessão do Google expirou. Entre de novo para "
                                   "continuar com a conta.", tipo="atencao"))

        estudo = C.Cartao(spacing=dp(10))
        estudo.add_widget(C.Texto(text="Seu progresso de estudo", estilo="subtitulo"))
        estudo.add_widget(C.Texto(
            text="Revisões, cards, quiz e casos ficam guardados neste aparelho e não são "
                 "apagados ao entrar ou sair de uma conta.", estilo="apoio"))
        col.add_widget(estudo)

        rever = C.Botao("Rever a apresentação", variante="neutro", icone="info")
        rever.bind(on_release=lambda *_: self.app.ir_para("boas_vindas"))
        col.add_widget(rever)

        self.area_sair = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        self.area_sair.bind(minimum_height=self.area_sair.setter("height"))
        col.add_widget(self.area_sair)
        if acesso.conectado:
            self._botao_sair()

        raiz.add_widget(scroll)
        self.add_widget(raiz)

    def _botao_sair(self):
        self.area_sair.clear_widgets()
        sair = C.Botao("Sair da conta", variante="fantasma", icone="sair")
        sair.bind(on_release=lambda *_: self._confirmar())
        self.area_sair.add_widget(sair)

    def _confirmar(self):
        self.area_sair.clear_widgets()
        self.area_sair.add_widget(C.Aviso(
            "Sair da conta neste aparelho? Seu progresso de estudo continua aqui, e você "
            "pode entrar de novo quando quiser.", tipo="atencao"))
        botoes = BoxLayout(size_hint_y=None, height=max(dp(52), C.dpt(46)), spacing=dp(10))
        cancelar = C.Botao("Cancelar", variante="neutro")
        cancelar.bind(on_release=lambda *_: self._botao_sair())
        confirmar = C.Botao("Sair", variante="perigo", icone="sair")
        confirmar.bind(on_release=lambda *_: self._sair())
        botoes.add_widget(cancelar)
        botoes.add_widget(confirmar)
        self.area_sair.add_widget(botoes)

    def _sair(self):
        self.app.acesso.sair()
        self.app.historico.clear()
        self.app.ir_para("acesso")
        self.app.mostrar_mensagem("Você saiu da conta. Seu progresso continua neste aparelho.",
                                  "info")
