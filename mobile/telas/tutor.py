"""Tutor: conversa sobre marcadores, em balões.

Quem responde é decidido em assistente.py: no celular, sempre a base do
próprio app, offline; no computador, um modelo local (Ollama) quando há
um instalado, com a base como reserva. A tela só mostra a conversa, o
estado ("pensando…") e, quando a resposta veio da reserva, avisa por quê.
"""

import threading

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from assistente import Assistente, BaseLocal, ModeloLocal
from mobile import componentes as C
from mobile.tema import COR, dpt
from mobile.telas.base import TelaBase

SUGESTOES = ["O que é ALT?", "Potássio alto", "Troponina", "HbA1c", "Creatinina"]


class TelaTutor(TelaBase):

    def montar(self, **_):
        app = self.app
        self.marcadores = app.marcadores
        self.assistente = Assistente([ModeloLocal(app.ia), BaseLocal(self.marcadores)])
        self.ocupado = False

        raiz = BoxLayout(orientation="vertical")
        topo = BoxLayout(size_hint_y=None, height=max(dp(74), dpt(62)),
                         padding=(dp(16), dp(12), dp(16), dp(8)), spacing=dp(12))
        topo.add_widget(C.SeloIcone("tutor", cor_fundo=COR["acento"],
                                    cor_icone=COR["branco"], tamanho=dp(46),
                                    pos_hint={"center_y": 0.5}))
        textos = BoxLayout(orientation="vertical")
        textos.add_widget(C.rotulo("Tutor", "20sp", COR["tinta"], negrito=True,
                                   vertical="bottom"))
        modelo = self.assistente.provedores[0]
        estado = (f"Com {modelo.nome}" if modelo.disponivel()
                  else "Sem internet · responde pela base do app")
        textos.add_widget(C.rotulo(estado, "13sp", COR["tinta3"], vertical="top"))
        topo.add_widget(textos)
        raiz.add_widget(topo)

        scroll, self.conversa = C.coluna_rolavel(padding=(dp(14), dp(6), dp(14), dp(12)),
                                                 spacing=dp(10))
        self.scroll = scroll
        raiz.add_widget(scroll)

        altura_chip = max(dp(44), dpt(38))
        faixa, linha = C.faixa_rolavel(altura_chip + dp(8), spacing=dp(8),
                                       padding=(dp(14), dp(4)))
        for sugestao in SUGESTOES:
            chip = C.Chip(sugestao)
            chip.bind(on_release=lambda _c, s=sugestao: self._perguntar(s))
            linha.add_widget(chip)
        raiz.add_widget(faixa)

        caixa = C.CampoTexto(dica="Pergunte sobre um marcador")
        entrada = BoxLayout(size_hint_y=None, height=caixa.height + dp(20),
                            padding=(dp(12), dp(8), dp(12), dp(12)), spacing=dp(8))
        self.campo = caixa.campo
        self.campo.bind(on_text_validate=lambda *_: self._enviar())
        entrada.add_widget(caixa)
        enviar = C.BotaoIcone("seta", cor=COR["acento"], cor_icone=COR["branco"],
                              tamanho=dp(52), pos_hint={"center_y": 0.5},
                              descricao="Enviar pergunta")
        enviar.bind(on_release=lambda *_: self._enviar())
        entrada.add_widget(enviar)
        raiz.add_widget(entrada)

        self.add_widget(raiz)
        exemplos = ", ".join(m["sigla"] for m in self.marcadores[:5])
        self._balao("Olá! Pergunte sobre qualquer marcador e eu explico a faixa de "
                    "referência e o que significa estar alto ou baixo.\n\n"
                    f"Experimente: {exemplos}…", do_usuario=False, acoes=False)

    # ── conversa ────────────────────────────────────────────────────
    def _rolar_para_o_fim(self):
        Clock.schedule_once(lambda _dt: setattr(self.scroll, "scroll_y", 0), 0.06)

    def _balao(self, texto, do_usuario, acoes=True):
        largura_max = Window.width * 0.82
        rotulo = Label(text=texto, font_size="15sp", line_height=1.18,
                       color=COR["branco"] if do_usuario else COR["tinta"],
                       halign="left", valign="top")
        # mede a largura natural primeiro: com text_size fixo a textura ocupa
        # a largura inteira e todo balão sairia largo, até "Oi"
        rotulo.texture_update()
        if rotulo.texture_size[0] > largura_max - dp(30):
            rotulo.text_size = (largura_max - dp(30), None)
            rotulo.texture_update()
        largura = min(largura_max, rotulo.texture_size[0] + dp(30))
        altura = rotulo.texture_size[1] + dp(24)
        rotulo.size_hint = (None, None)
        rotulo.size = (largura - dp(30), altura - dp(24))
        rotulo.text_size = rotulo.size

        balao = C.Superficie(size_hint=(None, None), size=(largura, altura),
                             padding=(dp(15), dp(12)), raio=dp(18),
                             cor_fundo=COR["acento"] if do_usuario else COR["superficie"],
                             elevacao=0 if do_usuario else 1)
        balao.add_widget(rotulo)
        linha = BoxLayout(size_hint_y=None, height=altura)
        if do_usuario:
            linha.add_widget(Widget())
            linha.add_widget(balao)
        else:
            linha.add_widget(balao)
            linha.add_widget(Widget())
        self.conversa.add_widget(linha)
        C.aparecer([balao], atraso=0.0, passo=0.0)

        if acoes and not do_usuario:
            libras = None
            if self.app.prefs["atalho_libras"]:
                libras = C.Botao("Libras", variante="neutro", icone="libras",
                                 height=dp(44), tamanho_fonte="14sp",
                                 size_hint_x=None, width=dpt(112))
                libras.bind(on_release=lambda *_: self.app.abrir_libras(texto))
            barra = C.linha_acoes(C.botao_ouvir(self.app, lambda: texto), libras)
            if barra is not None:
                self.conversa.add_widget(barra)
        self._rolar_para_o_fim()
        return balao

    def _perguntar(self, texto):
        self.campo.text = texto
        self._enviar()

    def _enviar(self):
        pergunta = self.campo.text.strip()
        if not pergunta or self.ocupado:
            return
        self.campo.text = ""
        self._balao(pergunta, do_usuario=True)
        marcador = self._identificar_marcador(pergunta)

        if self.assistente.provedores[0].disponivel() and marcador is not None:
            # o modelo pode levar alguns segundos: indicador e thread separada
            self.ocupado = True
            self.digitando = C.Digitando()
            linha = BoxLayout(size_hint_y=None, height=self.digitando.height)
            linha.add_widget(self.digitando)
            linha.add_widget(Widget())
            self.conversa.add_widget(linha)
            self.linha_digitando = linha
            self._rolar_para_o_fim()
            threading.Thread(target=self._responder_em_segundo_plano,
                             args=(pergunta, marcador), daemon=True).start()
        else:
            texto, _fonte, _aviso = self.assistente.responder(pergunta, marcador)
            Clock.schedule_once(lambda _dt: self._balao(texto, do_usuario=False), 0.2)

    def _responder_em_segundo_plano(self, pergunta, marcador):
        texto, fonte, aviso = self.assistente.responder(pergunta, marcador)
        Clock.schedule_once(lambda _dt: self._entregar(texto, fonte, aviso), 0)

    def _entregar(self, texto, fonte, aviso):
        self.ocupado = False
        self.digitando.parar()
        self.conversa.remove_widget(self.linha_digitando)
        if aviso:
            self.conversa.add_widget(C.Aviso(aviso, tipo="atencao"))
        self._balao(texto, do_usuario=False)

    def _identificar_marcador(self, pergunta):
        """Usa o mesmo vínculo do motor: evita que "na" vire sódio."""
        from progresso import marcadores_no_texto
        siglas = [m["sigla"] for m in self.marcadores]
        nomes = {m["sigla"]: m["nome"] for m in self.marcadores}
        achados = marcadores_no_texto(pergunta, siglas, nomes)
        if not achados:
            return None
        return next(m for m in self.marcadores if m["sigla"] == achados[0])
