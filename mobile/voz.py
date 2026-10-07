"""Leitura em voz alta (síntese de fala do próprio sistema).

Por que existe: o Kivy desenha a interface por conta própria e não a
expõe aos leitores de tela (TalkBack, NVDA). Para quem tem baixa visão ou
dificuldade de leitura, o app então lê ele mesmo os textos de estudo —
pergunta, resposta, interpretação, respostas do tutor.

Cada plataforma usa a voz que já tem instalada; nada é enviado para a
internet e nenhuma dependência nova entra no pacote:

- Android: android.speech.tts.TextToSpeech, via pyjnius (que já vem com
  o python-for-android). O manifesto declara a consulta ao serviço de
  voz, exigida a partir do Android 11.
- Windows: SAPI, via pywin32 se estiver instalado; sem ele, a voz do
  System.Speech pelo PowerShell, que vem com o próprio Windows.
- macOS: comando `say`; Linux: `espeak-ng` ou `espeak`, se houver.

Sem voz disponível, `disponivel` fica False e a interface esconde os
botões de ouvir em vez de oferecer algo que não funciona.
"""

import os
import shutil
import subprocess
import threading

from kivy.utils import platform


class _Nenhuma:
    disponivel = False

    def falar(self, texto, velocidade=1.0):
        pass

    def parar(self):
        pass


class _Android:
    def __init__(self):
        from jnius import PythonJavaClass, autoclass, java_method

        self._TTS = autoclass("android.speech.tts.TextToSpeech")
        Locale = autoclass("java.util.Locale")
        atividade = autoclass("org.kivy.android.PythonActivity").mActivity
        self.disponivel = False
        voz = self

        class AoIniciar(PythonJavaClass):
            __javainterfaces__ = ["android/speech/tts/TextToSpeech$OnInitListener"]
            __javacontext__ = "app"

            @java_method("(I)V")
            def onInit(self, status):
                if status == 0:  # TextToSpeech.SUCCESS
                    voz._tts.setLanguage(Locale("pt", "BR"))
                    voz.disponivel = True

        # a referência ao ouvinte precisa sobreviver, senão o Java chama um
        # objeto já recolhido pelo coletor de lixo
        self._ouvinte = AoIniciar()
        self._tts = self._TTS(atividade, self._ouvinte)

    def falar(self, texto, velocidade=1.0):
        if not self.disponivel:
            return
        self._tts.setSpeechRate(float(velocidade))
        self._tts.speak(texto, self._TTS.QUEUE_FLUSH, None, "bioquimicaedu")

    def parar(self):
        if self.disponivel:
            self._tts.stop()


class _Windows:
    def __init__(self):
        import win32com.client  # noqa: F401  (pywin32; ausente = sem voz)

        self._win32com = win32com.client
        self._voz = self._win32com.Dispatch("SAPI.SpVoice")
        # prefere uma voz em português, se o Windows tiver alguma
        for i in range(self._voz.GetVoices().Count):
            v = self._voz.GetVoices().Item(i)
            if "portug" in v.GetDescription().lower() or "brazil" in v.GetDescription().lower():
                self._voz.Voice = v
                break
        self.disponivel = True

    def falar(self, texto, velocidade=1.0):
        # SAPI vai de -10 a 10; 1,25× ≈ +3, 0,8× ≈ -3
        self._voz.Rate = max(-10, min(10, round((velocidade - 1.0) * 12)))
        self._voz.Speak(texto, 1 | 2)  # assíncrono | interrompe a fala anterior

    def parar(self):
        self._voz.Speak("", 1 | 2)


class _PowerShell:
    """Voz do Windows sem dependências: System.Speech, chamado pelo PowerShell.

    O texto vai pela entrada padrão, nunca na linha de comando: assim não
    há aspas para escapar nem como um texto virar comando.
    """

    ROTEIRO = ("[Console]::InputEncoding=[Text.Encoding]::UTF8;"
               "Add-Type -AssemblyName System.Speech;"
               "$v=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
               "$pt=$v.GetInstalledVoices()|Where-Object{$_.VoiceInfo.Culture.Name -like 'pt*'}"
               "|Select-Object -First 1;"
               "if($pt){$v.SelectVoice($pt.VoiceInfo.Name)};"
               "$v.Rate={taxa};$v.Speak([Console]::In.ReadToEnd())")

    def __init__(self):
        self.programa = shutil.which("powershell") or shutil.which("pwsh")
        if not self.programa:
            raise RuntimeError("PowerShell não encontrado")
        self._processo = None
        self._trava = threading.Lock()
        self.disponivel = True

    def falar(self, texto, velocidade=1.0):
        self.parar()
        taxa = max(-10, min(10, round((velocidade - 1.0) * 12)))
        with self._trava:
            self._processo = subprocess.Popen(
                [self.programa, "-NoProfile", "-NonInteractive", "-Command",
                 self.ROTEIRO.replace("{taxa}", str(taxa))],
                stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            self._processo.stdin.write(texto.encode("utf-8"))
            self._processo.stdin.close()

    def parar(self):
        with self._trava:
            if self._processo and self._processo.poll() is None:
                self._processo.terminate()
            self._processo = None


class _Comando:
    """`say` no macOS, `espeak-ng`/`espeak` no Linux."""

    def __init__(self, programa, argumentos_velocidade):
        self.programa = programa
        self.argumentos_velocidade = argumentos_velocidade
        self._processo = None
        self._trava = threading.Lock()
        self.disponivel = True

    def falar(self, texto, velocidade=1.0):
        self.parar()
        with self._trava:
            self._processo = subprocess.Popen(
                [self.programa, *self.argumentos_velocidade(velocidade), texto],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def parar(self):
        with self._trava:
            if self._processo and self._processo.poll() is None:
                self._processo.terminate()
            self._processo = None


def criar_voz():
    """Escolhe a voz da plataforma; nunca levanta exceção."""
    if os.environ.get("BIOQ_SEM_VOZ"):
        return _Nenhuma()
    try:
        if platform == "android":
            return _Android()
        if platform == "win":
            try:
                return _Windows()
            except Exception:
                return _PowerShell()   # Windows sem pywin32
        if platform == "macosx" and shutil.which("say"):
            return _Comando("say", lambda v: ["-r", str(round(180 * v))])
        for programa in ("espeak-ng", "espeak"):
            if shutil.which(programa):
                return _Comando(programa, lambda v: ["-v", "pt-br", "-s", str(round(160 * v))])
    except Exception as e:
        print(f"[voz] leitura em voz alta indisponível ({type(e).__name__}: {e})")
    return _Nenhuma()
