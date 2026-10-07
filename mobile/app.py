"""Aplicativo mobile do BioquímicaEDU: abertura, dados, ajustes e navegação.

Sequência de abertura:
  1. o Android mostra a imagem de abertura (presplash) enquanto o Python
     inicia — é a mesma logo, no mesmo fundo, então a troca não pisca;
  2. a tela de abertura do app aplica as preferências de leitura e
     carrega conteúdo, progresso e voz, sem travar a animação da logo;
  3. no primeiro acesso, segue para a apresentação (com os ajustes de
     acessibilidade); nos demais, direto para o Início.

Navegação em dois níveis, como nos apps de estudo atuais:
- abas na barra inferior (Início, Estudo, Cards, Prática, Tutor), trocadas
  com um esmaecer rápido, porque são lugares paralelos;
- telas empilhadas (detalhe, revisão, acessibilidade), que entram
  deslizando da direita e escondem a barra, porque são um aprofundamento
  com começo e fim. O botão voltar do Android desfaz a pilha.

Mudar um ajuste de leitura (tema, tamanho do texto, animações) reconstrói
a interface inteira na hora: as telas já se montam a cada visita, então
reconstruir custa pouco e garante que nada fique com a aparência antiga.
"""

import time
import webbrowser
from pathlib import Path

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import (FadeTransition, NoTransition, ScreenManager,
                                    SlideTransition)
from kivy.utils import platform

from mobile import dados, tema
from mobile.componentes import Aviso, BarraNavegacao
from mobile.preferencias import Preferencias
from mobile.tema import COR
from mobile.telas.abertura import TelaAbertura
from mobile.telas.acessibilidade import TelaAcessibilidade
from mobile.telas.boas_vindas import TelaBoasVindas
from mobile.telas.cartas import TelaCartas
from mobile.telas.estudo import TelaDetalhe, TelaEstudo
from mobile.telas.inicio import TelaInicio
from mobile.telas.pratica import TelaPratica
from mobile.telas.revisao import TelaRevisao
from mobile.telas.tutor import TelaTutor

NO_CELULAR = platform in ("android", "ios")

if not NO_CELULAR:
    # no computador, janela no formato de um celular atual
    Window.size = (400, 840)
# o teclado empurra a tela em vez de cobrir o campo de digitação
Window.softinput_mode = "below_target"

# Telas de aprofundamento: sem barra inferior e com voltar
EMPILHADAS = {"detalhe", "revisao", "acessibilidade"}
# Telas sem barra inferior e sem pilha
SEM_BARRA = EMPILHADAS | {"boas_vindas"}

ABA_DA_TELA = {
    "inicio": "inicio", "estudo": "estudo", "detalhe": "estudo",
    "cartas": "cartas", "pratica": "pratica", "tutor": "tutor",
    "revisao": "inicio", "acessibilidade": "inicio",
}

# Nomes da versão anterior, mantidos para quem ainda chama ir_para com eles
APELIDOS = {
    "flashcards":  ("cartas", {}),
    "quiz":        ("pratica", {"modo": "quiz", "iniciar": True}),
    "diagnostico": ("pratica", {"modo": "casos"}),
}

VLIBRAS_ANDROID = "com.lavid.vlibrasdroid"
VLIBRAS_PAGINA = "https://www.gov.br/governodigital/pt-br/acessibilidade-e-usuario/vlibras"

TEMPO_MINIMO_ABERTURA = 0.7   # segundos: a logo aparece sem atrasar quem já carregou


class BioquimicaApp(App):
    title = "BioquímicaEDU"
    icon = str(Path(__file__).resolve().parent.parent / "assets" / "icon.png")

    TELAS = {
        "inicio": TelaInicio,
        "estudo": TelaEstudo,
        "detalhe": TelaDetalhe,
        "cartas": TelaCartas,
        "pratica": TelaPratica,
        "revisao": TelaRevisao,
        "tutor": TelaTutor,
        "acessibilidade": TelaAcessibilidade,
        "boas_vindas": TelaBoasVindas,
    }

    def build(self):
        self.prefs = Preferencias(self._arquivo("preferencias.json",
                                                "preferencias_mobile.json"))
        self._aplicar_tema()
        self.carregado = False
        self.voz = None
        self.historico = []

        self.raiz = FloatLayout()
        self.camada = BoxLayout(orientation="vertical")
        self.raiz.add_widget(self.camada)

        # 1. só a abertura; o resto é montado depois de carregar
        self.gerenciador = ScreenManager(transition=NoTransition())
        abertura = TelaAbertura(self, name="abertura")
        self.gerenciador.add_widget(abertura)
        self.camada.add_widget(self.gerenciador)
        abertura.preparar()

        Window.bind(on_keyboard=self._tecla)
        self._inicio_abertura = time.monotonic()
        # um quadro de folga para a logo ser desenhada antes do trabalho pesado
        Clock.schedule_once(lambda _dt: self._carregar(), 0.05)
        return self.raiz

    # ── abertura ────────────────────────────────────────────────────
    def _carregar(self):
        """Carrega tudo que as telas precisam; em falha, mostra o motivo."""
        from progresso import Progresso

        try:
            self.marcadores = dados.carregar_marcadores()
            if not self.marcadores:
                raise RuntimeError("o arquivo de marcadores está vazio ou ilegível")
            self.flashcards = dados.carregar_flashcards()
            self.extras = dados.carregar_extras()
            self.imagens = dados.carregar_imagens()
            self.quiz = dados.carregar_quiz()
            self.casos = dados.carregar_casos()
            self.progresso = Progresso(self._arquivo("progresso.json", None))
            self.casos_resolvidos = self.progresso.casos_resolvidos()
        except Exception as e:
            print(f"[abertura] falha ao carregar: {type(e).__name__}: {e}")
            self.gerenciador.get_screen("abertura").mostrar_erro(
                "Não foi possível abrir o conteúdo de estudo.",
                ao_tentar=self._carregar)
            return

        self.ultimo_quiz = None
        self.ia = self._iniciar_ia()
        from mobile.voz import criar_voz
        self.voz = criar_voz()
        self.carregado = True

        destino = "inicio" if self.prefs["boas_vindas_vista"] else "boas_vindas"
        espera = max(0.0, TEMPO_MINIMO_ABERTURA - (time.monotonic() - self._inicio_abertura))
        Clock.schedule_once(lambda _dt: self._sair_da_abertura(destino), espera)

    def _sair_da_abertura(self, destino):
        self._montar_interface()
        self.ir_para(destino, animar=False)
        if tema.movimento():
            self.camada.opacity = 0
            Animation(opacity=1, duration=0.22, t="out_quad").start(self.camada)

    def _montar_interface(self):
        self.camada.clear_widgets()
        self.gerenciador = ScreenManager(transition=NoTransition())
        for nome, Classe in self.TELAS.items():
            self.gerenciador.add_widget(Classe(self, name=nome))
        self.navegacao = BarraNavegacao(ao_escolher=self.ir_para)
        self.camada.add_widget(self.gerenciador)
        self.camada.add_widget(self.navegacao)

    # ── armazenamento ───────────────────────────────────────────────
    def _arquivo(self, nome_celular, nome_computador):
        """Onde cada arquivo do estudante fica.

        No celular, na pasta privada do app: fica fora do código, então uma
        atualização do APK não apaga o que o estudante já estudou, e o app
        não precisa de permissão de armazenamento. No computador, em data/
        (o progresso é compartilhado com a versão desktop).
        """
        if NO_CELULAR:
            return Path(self.user_data_dir) / nome_celular
        if nome_computador is None:
            return None  # Progresso usa data/progresso.json (ou BIOQ_PASTA_ALUNO)
        from progresso import PASTA_ALUNO
        return PASTA_ALUNO / nome_computador

    @staticmethod
    def _iniciar_ia():
        """Ollama só existe no computador; no celular o tutor é offline."""
        if NO_CELULAR:
            return None
        try:
            # o módulo já cria e testa uma instância ao ser importado
            from ollama_ia import ia
        except Exception as e:
            print(f"[tutor] Ollama indisponível ({type(e).__name__}); usando modo offline")
            return None
        return ia if getattr(ia, "disponivel", False) else None

    # ── preferências ────────────────────────────────────────────────
    def _aplicar_tema(self):
        p = self.prefs
        tema.aplicar_ajustes(p["tema"], p["escala_texto"], p["movimento_reduzido"])
        Window.clearcolor = COR["fundo"]

    def mudar_preferencia(self, chave, valor):
        """Salva o ajuste e, se ele muda a aparência, reconstrói a interface."""
        self.prefs.definir(chave, valor)
        if chave in ("tema", "escala_texto", "movimento_reduzido"):
            atual = self.gerenciador.current
            parametros = self.gerenciador.get_screen(atual).parametros
            self._aplicar_tema()
            self._montar_interface()
            self._mostrar(atual, parametros)
        if chave == "leitura_voz" and not valor:
            self.parar_fala()

    # ── voz e Libras ────────────────────────────────────────────────
    def voz_ligada(self):
        return bool(self.prefs["leitura_voz"] and self.voz is not None
                    and self.voz.disponivel)

    def falar(self, texto):
        if self.voz_ligada() and texto:
            self.voz.falar(texto, self.prefs["velocidade_voz"])

    def parar_fala(self):
        if self.voz is not None:
            self.voz.parar()

    def abrir_libras(self, texto):
        """Copia o texto e abre o VLibras, que o traduz para Libras.

        O VLibras (Governo Federal) não oferece integração direta para
        apps nativos; no celular, o caminho confiável é levar o texto pela
        área de transferência até o app dele.
        """
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(texto)
        if platform == "android":
            try:
                from jnius import autoclass
                atividade = autoclass("org.kivy.android.PythonActivity").mActivity
                intencao = atividade.getPackageManager().getLaunchIntentForPackage(VLIBRAS_ANDROID)
                if intencao is not None:
                    atividade.startActivity(intencao)
                    self.mostrar_mensagem("Texto copiado. No VLibras, cole o texto para "
                                          "ver a tradução em Libras.", "sucesso")
                    return
                webbrowser.open(f"market://details?id={VLIBRAS_ANDROID}")
                self.mostrar_mensagem("Texto copiado. Instale o VLibras e cole o texto "
                                      "nele para ver a tradução.", "info")
                return
            except Exception as e:
                print(f"[libras] não foi possível abrir o VLibras: {e}")
        webbrowser.open(VLIBRAS_PAGINA)
        self.mostrar_mensagem("Texto copiado. Abra o VLibras e cole o texto para ver a "
                              "tradução em Libras.", "info")

    # ── mensagens rápidas ───────────────────────────────────────────
    def mostrar_mensagem(self, texto, tipo="info", duracao=4.5):
        """Aviso temporário no rodapé, acima da barra de navegação."""
        base = (self.navegacao.height if getattr(self, "navegacao", None)
                and self.navegacao.opacity else 0)
        aviso = Aviso(texto, tipo=tipo, size_hint=(None, None),
                      width=Window.width - dp(32), elevacao=2)
        aviso.pos = (dp(16), base + dp(12))
        self.raiz.add_widget(aviso)

        def remover(_dt):
            if aviso.parent is None:
                return
            if tema.movimento():
                anim = Animation(opacity=0, duration=0.25)
                anim.bind(on_complete=lambda *_: self.raiz.remove_widget(aviso))
                anim.start(aviso)
            else:
                self.raiz.remove_widget(aviso)
        Clock.schedule_once(remover, duracao)
        return aviso

    # ── navegação ───────────────────────────────────────────────────
    def tela_atual(self):
        return self.gerenciador.current_screen

    def ir_para(self, destino, animar=True, foco=None, **parametros):
        if not self.carregado:
            return
        if destino in APELIDOS:
            destino, extras = APELIDOS[destino]
            parametros = {**extras, **parametros}
        if destino == "estudo" and foco:
            destino, parametros = "detalhe", {"sigla": foco}
        if not self.gerenciador.has_screen(destino):
            print(f"[navegação] tela desconhecida: {destino}")
            return

        self.parar_fala()
        atual = self.gerenciador.current
        if destino in EMPILHADAS:
            if atual != destino:
                self.historico.append(atual)
        else:
            self.historico.clear()

        self.gerenciador.transition = self._transicao(atual, destino, animar)
        self._mostrar(destino, parametros)

    def _no_tamanho_final(self, destino):
        """Mostra ou esconde a barra ANTES de montar a tela de destino.

        Ao contrário, a tela nascia com a altura de quando a barra estava
        escondida, encolhia logo depois e a rolagem saía do lugar (o Início
        aparecia deslocado ao sair da apresentação ou da revisão).
        """
        self._ajustar_navegacao(destino)
        self.camada.do_layout()
        tela = self.gerenciador.get_screen(destino)
        tela.size = self.gerenciador.size
        return tela

    def _mostrar(self, destino, parametros):
        tela = self._no_tamanho_final(destino)
        tela.preparar(**parametros)
        self.gerenciador.current = destino

    def voltar(self):
        self.parar_fala()
        anterior = self.historico.pop() if self.historico else "inicio"
        atual = self.gerenciador.current
        tela = self._no_tamanho_final(anterior)
        # o início precisa refletir o que acabou de mudar; as outras telas
        # voltam como estavam (busca, filtro e rolagem preservados)
        if anterior == "inicio" or not tela.children:
            tela.preparar(**tela.parametros)
        self.gerenciador.transition = (
            SlideTransition(direction="right", duration=0.26)
            if atual != anterior and tema.movimento() else NoTransition())
        self.gerenciador.current = anterior

    @staticmethod
    def _transicao(atual, destino, animar):
        if not animar or atual == destino or not tema.movimento():
            return NoTransition()
        if destino not in EMPILHADAS and atual not in EMPILHADAS \
                and (atual in SEM_BARRA) != (destino in SEM_BARRA):
            # o esmaecer guarda a tela no tamanho de antes enquanto anima;
            # quando a barra aparece ou some, a troca direta não desloca nada
            return NoTransition()
        if destino in EMPILHADAS:
            return SlideTransition(direction="left", duration=0.26)
        if atual in EMPILHADAS:
            return SlideTransition(direction="right", duration=0.26)
        return FadeTransition(duration=0.16)

    def _ajustar_navegacao(self, destino):
        esconder = destino in SEM_BARRA
        self.navegacao.height = 0 if esconder else BarraNavegacao.altura()
        self.navegacao.opacity = 0 if esconder else 1
        self.navegacao.disabled = esconder
        if not esconder:
            self.navegacao.selecionar(ABA_DA_TELA.get(destino, "inicio"))

    def _tecla(self, _janela, tecla, *_args):
        """Botão voltar do Android (e Esc no computador)."""
        if tecla != 27 or not self.carregado:
            return False
        atual = self.gerenciador.current
        if atual in EMPILHADAS:
            self.voltar()
            return True
        if atual not in ("inicio", "boas_vindas"):
            self.ir_para("inicio")
            return True
        return False  # no início, voltar fecha o app

    # ── motor de estudo ─────────────────────────────────────────────
    def alimentar_memoria(self, texto, acertou, peso):
        """Liga quiz e casos clínicos ao motor de repetição espaçada."""
        from progresso import marcadores_no_texto
        siglas = [m["sigla"] for m in self.marcadores]
        nomes = {m["sigla"]: m["nome"] for m in self.marcadores}
        alvos = marcadores_no_texto(texto, siglas, nomes)
        if alvos:
            self.progresso.registrar_atividade(alvos, acertou, peso=peso)
        return alvos

    def registrar_caso_resolvido(self, caso_id):
        self.casos_resolvidos.add(caso_id)
        self.progresso.marcar_caso_resolvido(caso_id)

    def on_pause(self):
        # Android: o app pode ir para segundo plano sem perder o estado
        self.parar_fala()
        return True
