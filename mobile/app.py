"""Aplicativo mobile do BioquímicaEDU: abertura, dados, ajustes e navegação.

Sequência de abertura:
  1. o Android mostra a imagem de abertura (presplash) enquanto o Python
     inicia — é a mesma logo, no mesmo fundo, então a troca não pisca;
  2. a tela de abertura do app (logo e nome) aplica as preferências de
     leitura e carrega conteúdo, progresso e voz, sem travar a animação;
  3. tela de acesso, se o estudante ainda não escolheu: entrar com o
     Google ou usar sem conta (a escolha fica salva; mobile/conta.py);
  4. apresentação (tutorial) só se ainda não foi vista — no aparelho ou,
     com conta, em qualquer aparelho; depois, o Início.

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

import threading
import time
import webbrowser
from pathlib import Path

from kivy.config import Config
from kivy.utils import platform

NO_CELULAR = platform in ("android", "ios")
if not NO_CELULAR:
    # tamanho mínimo da janela antes de ela existir: definido depois, um
    # valor por vez, o Kivy avisa que falta o outro
    Config.set("graphics", "minimum_width", "360")
    Config.set("graphics", "minimum_height", "560")

from kivy.animation import Animation  # noqa: E402  (depois da configuração)
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import (FadeTransition, NoTransition, ScreenManager,
                                    SlideTransition)

from mobile import dados, tema
from mobile.componentes import Aviso, BarraNavegacao, TrilhoNavegacao
from mobile.preferencias import Preferencias
from mobile.tema import COR
from mobile.telas.abertura import TelaAbertura
from mobile.telas.acesso import TelaAcesso
from mobile.telas.acessibilidade import TelaAcessibilidade
from mobile.telas.boas_vindas import TelaBoasVindas
from mobile.telas.cartas import TelaCartas
from mobile.telas.estudo import TelaDetalhe, TelaEstudo
from mobile.telas.inicio import TelaInicio
from mobile.telas.minha_conta import TelaConta
from mobile.telas.pratica import TelaPratica
from mobile.telas.revisao import TelaRevisao
from mobile.telas.tutor import TelaTutor

def _encaixar_na_tela(largura, altura):
    """Tamanho e posição da janela dentro da área livre da tela do Windows
    (sem a barra de tarefas), em dp. Num notebook de 1366 × 768, ou numa
    tela Full HD com escala de 125%, a janela padrão passaria da borda de
    baixo e esconderia os botões do rodapé."""
    try:
        import ctypes
        from ctypes import wintypes

        from kivy.metrics import Metrics
        area = wintypes.RECT()
        if not ctypes.windll.user32.SystemParametersInfoW(0x30, 0, ctypes.byref(area), 0):
            return largura, altura, None   # 0x30 = SPI_GETWORKAREA
    except (AttributeError, OSError, ImportError):
        return largura, altura, None
    escala = Metrics.density or 1
    livre_l = (area.right - area.left) / escala
    livre_a = (area.bottom - area.top) / escala
    titulo = 32   # barra de título do Windows, fora da área do app
    largura = max(360, int(min(largura, livre_l - 32)))
    altura = max(560, int(min(altura, livre_a - titulo - 16)))
    esquerda = area.left / escala + (livre_l - largura) / 2
    topo = area.top / escala + titulo + max(0, (livre_a - titulo - altura) / 2)
    return largura, altura, (esquerda, topo)


if not NO_CELULAR:
    import os
    import sys
    if "--celular" in sys.argv or os.environ.get("BIOQ_JANELA") == "celular":
        tamanho = (400, 840)   # para testar o formato de celular no computador
    else:
        tamanho = (1180, 760)
    posicao = None
    if sys.platform == "win32":
        *tamanho, posicao = _encaixar_na_tela(*tamanho)
    Window.size = tuple(tamanho)
    if posicao is not None:
        Window.left, Window.top = posicao
    if not Window.minimum_width:   # janela criada antes deste módulo (testes)
        Window.minimum_width, Window.minimum_height = 360, 560
# o teclado empurra a tela em vez de cobrir o campo de digitação
Window.softinput_mode = "below_target"

# Telas de aprofundamento: sem barra inferior e com voltar
EMPILHADAS = {"detalhe", "revisao", "acessibilidade", "conta"}
# Telas sem barra inferior e sem pilha (o fluxo de entrada)
SEM_BARRA = EMPILHADAS | {"boas_vindas", "acesso"}

ABA_DA_TELA = {
    "inicio": "inicio", "estudo": "estudo", "detalhe": "estudo",
    "cartas": "cartas", "pratica": "pratica", "tutor": "tutor",
    "revisao": "inicio", "acessibilidade": "inicio", "conta": "inicio",
}

# Nomes da versão anterior, mantidos para quem ainda chama ir_para com eles
APELIDOS = {
    "flashcards":  ("cartas", {}),
    "quiz":        ("pratica", {"modo": "quiz", "iniciar": True}),
    "diagnostico": ("pratica", {"modo": "casos"}),
}

VLIBRAS_ANDROID = "com.lavid.vlibrasdroid"
VLIBRAS_PAGINA = "https://www.gov.br/governodigital/pt-br/acessibilidade-e-usuario/vlibras"

TEMPO_MINIMO_ABERTURA = 1.0   # segundos: a logo e o nome são vistos, sem atrasar ninguém
ESPERA_MAXIMA_NUVEM = 3.0     # segundos que a abertura espera a conta responder


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
        "acesso": TelaAcesso,
        "conta": TelaConta,
    }

    def build(self):
        self._liberar_rotacao_no_tablet()
        self.prefs = Preferencias(self._arquivo("preferencias.json",
                                                "preferencias_mobile.json"))
        self._aplicar_tema()
        self.carregado = False
        self.voz = None
        self.historico = []

        self.raiz = FloatLayout()
        self.camada = BoxLayout(orientation="vertical")
        self.raiz.add_widget(self.camada)
        self.navegacao = None      # criada depois de carregar (_montar_navegacao)
        self.trilho = False

        # 1. só a abertura; o resto é montado depois de carregar
        self.gerenciador = ScreenManager(transition=NoTransition())
        abertura = TelaAbertura(self, name="abertura")
        self.gerenciador.add_widget(abertura)
        self.camada.add_widget(self.gerenciador)
        abertura.preparar()

        Window.bind(on_keyboard=self._tecla)
        Window.bind(on_resize=self._ao_redimensionar)
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
            from mobile.conta import Acesso
            self.acesso = Acesso(self.prefs, self._pasta_sessao())
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
        self._conferir_conta()

    # ── fluxo de entrada ────────────────────────────────────────────
    def _conferir_conta(self):
        """Com conta, confere a sessão e o tutorial na nuvem, numa thread.

        Se a cópia local ainda não sabe se o tutorial foi visto (ele pode ter
        sido feito em outro aparelho), a abertura espera a resposta por até
        ESPERA_MAXIMA_NUVEM segundos; sem internet, segue com a cópia local.
        """
        if not self.acesso.conectado:
            self._agendar_saida()
            return
        esperar = self.acesso.precisa_confirmar_na_nuvem()
        sincronizando = threading.Thread(target=self.acesso.sincronizar, daemon=True)
        sincronizando.start()
        limite = time.monotonic() + ESPERA_MAXIMA_NUVEM

        def acompanhar(_dt):
            if sincronizando.is_alive():
                if esperar and time.monotonic() > limite:
                    self._agendar_saida()
                    return Clock.schedule_once(lambda _d: self._avisar_sessao(sincronizando), 1)
                return Clock.schedule_once(acompanhar, 0.1)
            if esperar:
                self._agendar_saida()
            self._avisar_sessao(sincronizando)

        if not esperar:
            self._agendar_saida()
        Clock.schedule_once(acompanhar, 0.1)

    def _avisar_sessao(self, sincronizando):
        """Se a nuvem disser que a sessão não vale mais, avisa sem tirar o
        estudante do que está fazendo; na próxima abertura, ele escolhe de novo."""
        if sincronizando.is_alive():
            Clock.schedule_once(lambda _d: self._avisar_sessao(sincronizando), 1)
        elif self.acesso.sessao_encerrada and getattr(self, "navegacao", None) is not None:
            self.mostrar_mensagem("Sua sessão do Google expirou. Entre de novo em Conta.",
                                  "atencao", duracao=6)

    def _destino_inicial(self):
        """Abertura → acesso (se preciso) → tutorial (só se não visto) → Início."""
        if self.acesso.precisa_escolher():
            return "acesso"
        return "inicio" if self.acesso.tutorial_visto() else "boas_vindas"

    def _agendar_saida(self):
        if getattr(self, "_saida_agendada", False):
            return
        self._saida_agendada = True
        destino = self._destino_inicial()
        espera = max(0.0, TEMPO_MINIMO_ABERTURA - (time.monotonic() - self._inicio_abertura))
        Clock.schedule_once(lambda _dt: self._sair_da_abertura(destino), espera)

    def seguir_apos_acesso(self):
        """Depois de escolher como entrar: tutorial no primeiro acesso, senão o Início."""
        self.historico.clear()
        self.ir_para("inicio" if self.acesso.tutorial_visto() else "boas_vindas")

    def _sair_da_abertura(self, destino):
        self._montar_interface()
        self.ir_para(destino, animar=False)
        if tema.movimento():
            self.camada.opacity = 0
            Animation(opacity=1, duration=0.22, t="out_quad").start(self.camada)

    def _montar_interface(self):
        self.gerenciador = ScreenManager(transition=NoTransition())
        for nome, Classe in self.TELAS.items():
            self.gerenciador.add_widget(Classe(self, name=nome))
        self._montar_navegacao()

    def _montar_navegacao(self):
        """Barra de abas embaixo (celular) ou trilho lateral (tablet, computador)."""
        self.formato = tema.formato()
        self.trilho = self.formato != "compacto"
        self.camada.clear_widgets()
        if self.trilho:
            self.camada.orientation = "horizontal"
            self.navegacao = TrilhoNavegacao(ao_escolher=self.ir_para)
            self.camada.add_widget(self.navegacao)
            self.camada.add_widget(self.gerenciador)
        else:
            self.camada.orientation = "vertical"
            self.navegacao = BarraNavegacao(ao_escolher=self.ir_para)
            self.camada.add_widget(self.gerenciador)
            self.camada.add_widget(self.navegacao)

    def _ao_redimensionar(self, *_):
        # arrastar a borda da janela gera dezenas de eventos: espera assentar
        if getattr(self, "_redimensionar", None) is not None:
            self._redimensionar.cancel()
        self._redimensionar = Clock.schedule_once(self._reavaliar_formato, 0.25)

    def _reavaliar_formato(self, _dt):
        """Girou o tablet ou redimensionou a janela: troca só a navegação.

        As telas continuam as mesmas, com o que o estudante estava fazendo
        (uma revisão no meio, um quiz respondido pela metade); a moldura de
        cada uma já se reacomoda à nova largura. Só o Início, que muda de uma
        para duas colunas e não guarda estado, é remontado.
        """
        # a janela muda de tamanho ao abrir, antes de a interface existir
        if getattr(self, "navegacao", None) is None or tema.formato() == self.formato:
            return
        atual = self.gerenciador.current
        self._montar_navegacao()
        self._ajustar_navegacao(atual)
        if atual == "inicio":
            tela = self.gerenciador.get_screen("inicio")
            tela.size = self.gerenciador.size
            tela.preparar(**tela.parametros)

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

    def _pasta_sessao(self):
        """Onde fica a sessão do Google (cifrada no Windows; ver autenticacao.Cofre).

        No Android, na pasta do app que o sistema deixa fora do backup: a
        sessão não deve ser restaurada em outro aparelho. No computador, ao
        lado do progresso (no executável, em %APPDATA%\\BioquimicaEDU)."""
        if platform == "android":
            try:
                from jnius import autoclass
                atividade = autoclass("org.kivy.android.PythonActivity").mActivity
                return Path(atividade.getNoBackupFilesDir().getAbsolutePath())
            except Exception as e:   # noqa: BLE001
                print(f"[conta] pasta sem backup indisponível ({e}); usando a do app")
        if NO_CELULAR:
            return Path(self.user_data_dir)
        from progresso import PASTA_ALUNO
        return PASTA_ALUNO

    @staticmethod
    def _liberar_rotacao_no_tablet():
        """O buildozer.spec trava o app em retrato, o certo para celular. Em
        tablet (menor lado com 600 dp ou mais), o app gira com o aparelho,
        respeitando a trava de rotação do sistema. Do Android 16 em diante o
        próprio sistema já ignora a trava em telas grandes; antes dele (um
        Galaxy Tab S4 vai até o Android 10), quem libera é o app."""
        if platform != "android" or min(Window.size) / dp(1) < 600:
            return
        try:
            from android.runnable import run_on_ui_thread
            from jnius import autoclass
        except ImportError:
            return

        @run_on_ui_thread
        def liberar():
            info = autoclass("android.content.pm.ActivityInfo")
            atividade = autoclass("org.kivy.android.PythonActivity").mActivity
            atividade.setRequestedOrientation(info.SCREEN_ORIENTATION_FULL_USER)

        try:
            liberar()
        except Exception as e:
            print(f"[tela] não foi possível liberar a rotação: {e}")

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
        tema.aplicar_ajustes(p["tema"], p["escala_texto"], p["movimento_reduzido"],
                             p["fonte_leitura"])
        Window.clearcolor = COR["fundo"]

    def mudar_preferencia(self, chave, valor):
        """Salva o ajuste e, se ele muda a aparência, reconstrói a interface."""
        self.prefs.definir(chave, valor)
        if chave in ("tema", "escala_texto", "movimento_reduzido", "fonte_leitura"):
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
        navegacao = getattr(self, "navegacao", None)
        visivel = navegacao is not None and navegacao.opacity
        base = navegacao.height if visivel and not self.trilho else 0
        lateral = navegacao.width if visivel and self.trilho else 0
        largura = min(Window.width - lateral - dp(32), dp(560))
        aviso = Aviso(texto, tipo=tipo, size_hint=(None, None), width=largura, elevacao=2)
        aviso.pos = (lateral + (Window.width - lateral - largura) / 2, base + dp(12))
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
        if self.trilho:
            self.navegacao.width = 0 if esconder else TrilhoNavegacao.largura()
        else:
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
        if atual not in ("inicio", "boas_vindas", "acesso"):
            self.ir_para("inicio")
            return True
        return False  # no início (e no fluxo de entrada), voltar fecha o app

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
