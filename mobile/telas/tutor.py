"""Tutor: conversa sobre marcadores, em balões.

No celular o tutor responde sempre pela base do app, offline. No
computador, se houver um Ollama local com modelo instalado, a pergunta
vai para ele; se não houver, ou se falhar, volta para a base.
"""

import threading

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from mobile import componentes as C
from mobile.dados import formatar_numero
from mobile.tema import COR
from mobile.telas.base import TelaBase

SUGESTOES = ["O que é ALT?", "Potássio alto", "Troponina", "HbA1c", "Creatinina"]


class TelaTutor(TelaBase):

    def montar(self, **_):
        app = self.app
        self.marcadores = app.marcadores

        raiz = BoxLayout(orientation="vertical")
        topo = BoxLayout(size_hint_y=None, height=dp(74),
                         padding=(dp(16), dp(14), dp(16), dp(10)), spacing=dp(12))
        topo.add_widget(C.SeloIcone("frasco", cor_fundo=COR["acento"],
                                    cor_icone=COR["branco"], tamanho=dp(46),
                                    pos_hint={"center_y": 0.5}))
        textos = BoxLayout(orientation="vertical")
        textos.add_widget(C.rotulo("Tutor", "20sp", COR["tinta"], negrito=True,
                                   vertical="bottom"))
        estado = ("Ollama local conectado" if app.ia is not None
                  else "Offline · responde pela base do app")
        textos.add_widget(C.rotulo(estado, "12.5sp", COR["tinta3"], vertical="top"))
        topo.add_widget(textos)
        raiz.add_widget(topo)

        scroll, self.conversa = C.coluna_rolavel(padding=(dp(14), dp(6), dp(14), dp(12)),
                                                 spacing=dp(10))
        self.scroll = scroll
        raiz.add_widget(scroll)

        faixa, linha = C.faixa_rolavel(dp(46), spacing=dp(8), padding=(dp(14), dp(4)))
        for sugestao in SUGESTOES:
            chip = C.Chip(sugestao)
            chip.bind(on_release=lambda _c, s=sugestao: self._perguntar(s))
            linha.add_widget(chip)
        raiz.add_widget(faixa)

        entrada = BoxLayout(size_hint_y=None, height=dp(70),
                            padding=(dp(12), dp(8), dp(12), dp(12)), spacing=dp(8))
        caixa = C.CampoTexto(dica="Pergunte sobre um marcador")
        self.campo = caixa.campo
        self.campo.bind(on_text_validate=lambda *_: self._enviar())
        entrada.add_widget(caixa)
        enviar = C.BotaoIcone("seta", cor=COR["acento"], cor_icone=COR["branco"],
                              tamanho=dp(50), pos_hint={"center_y": 0.5})
        enviar.bind(on_release=lambda *_: self._enviar())
        entrada.add_widget(enviar)
        raiz.add_widget(entrada)

        self.add_widget(raiz)
        exemplos = ", ".join(m["sigla"] for m in self.marcadores[:5])
        self._balao("Olá! Pergunte sobre qualquer marcador e eu explico a faixa de "
                    "referência e o que significa estar alto ou baixo.\n\n"
                    f"Experimente: {exemplos}…", do_usuario=False)

    # ── conversa ────────────────────────────────────────────────────
    def _balao(self, texto, do_usuario):
        largura_max = Window.width * 0.8
        rotulo = Label(text=texto, font_size="14.5sp", line_height=1.15,
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
                             padding=(dp(15), dp(12)), raio=dp(20),
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
        Clock.schedule_once(lambda _dt: setattr(self.scroll, "scroll_y", 0), 0.06)
        return balao

    def _perguntar(self, texto):
        self.campo.text = texto
        self._enviar()

    def _enviar(self):
        pergunta = self.campo.text.strip()
        if not pergunta:
            return
        self.campo.text = ""
        self._balao(pergunta, do_usuario=True)

        marcador = self._identificar_marcador(pergunta)
        if self.app.ia is not None and marcador is not None:
            self._balao("Consultando o tutor local…", do_usuario=False)
            threading.Thread(target=self._perguntar_ia, args=(marcador, pergunta),
                             daemon=True).start()
        else:
            Clock.schedule_once(lambda _dt: self._balao(
                self._resposta_local(pergunta, marcador), do_usuario=False), 0.25)

    def _perguntar_ia(self, marcador, pergunta):
        """Consulta o Ollama em segundo plano; volta para a base se falhar."""
        try:
            resposta = self.app.ia.chat_marcador(marcador["nome"], pergunta)
        except Exception as e:
            resposta = ""
            print(f"[tutor] falha na consulta: {type(e).__name__}: {e}")

        if not self._resposta_util(resposta):
            self.app.ia = None  # não insiste nas próximas perguntas
            resposta = ("O tutor local não está disponível (confira se o modelo foi "
                        "baixado com 'ollama pull mistral'). Respondendo pela base "
                        "do app:\n\n" + self._resumo(marcador))
        Clock.schedule_once(lambda _dt: self._balao(resposta, do_usuario=False), 0)

    @staticmethod
    def _resposta_util(texto):
        """Falso para resposta vazia ou para as mensagens de falha do módulo
        de IA ("❌ Erro ...", "❌ Ollama não está rodando..."), que não podem
        aparecer no balão como se fossem a explicação do tutor."""
        if not texto or not texto.strip():
            return False
        inicio = texto.strip().lstrip("❌⚠️ ").lower()
        return not (texto.strip().startswith("❌")
                    or inicio.startswith(("erro", "error", "[erro")))

    def _identificar_marcador(self, pergunta):
        """Usa o mesmo vínculo do motor: evita que "na" vire sódio."""
        from progresso import marcadores_no_texto
        siglas = [m["sigla"] for m in self.marcadores]
        nomes = {m["sigla"]: m["nome"] for m in self.marcadores}
        achados = marcadores_no_texto(pergunta, siglas, nomes)
        if not achados:
            return None
        return next(m for m in self.marcadores if m["sigla"] == achados[0])

    @staticmethod
    def _resumo(m):
        def associado(chave):
            texto = (m.get(chave) or "").strip()
            return "" if not texto or texto == "—" else f"\nAssociado a: {texto}"

        faixa = f"{formatar_numero(m['valor_ref_min'])} – {formatar_numero(m['valor_ref_max'])}"
        return (f"{m['nome']} ({m['sigla']})\n"
                f"Referência: {faixa} {m['unidade']}\n\n"
                f"Elevado: {m.get('interpretacao_alta', '—')}"
                f"{associado('doencas_associadas_alta')}\n\n"
                f"Baixo: {m.get('interpretacao_baixa', '—')}"
                f"{associado('doencas_associadas_baixa')}")

    def _resposta_local(self, pergunta, marcador):
        if marcador is not None:
            return self._resumo(marcador)
        texto = pergunta.lower()
        if any(p in texto for p in ("oi", "olá", "ola", "bom dia", "boa tarde", "boa noite")):
            return "Olá! Digite o nome ou a sigla de um marcador para começar."
        if "obrigad" in texto:
            return "De nada. Bons estudos!"
        if any(p in texto for p in ("ajuda", "como funciona", "o que você faz")):
            return ("Digite a sigla ou o nome de um marcador — por exemplo ALT, "
                    "Glicose ou Potássio — e eu mostro a faixa de referência e o que "
                    "significa estar alto ou baixo.")
        disponiveis = ", ".join(m["sigla"] for m in self.marcadores)
        return f"Não encontrei esse marcador na base.\n\nDisponíveis: {disponiveis}"
