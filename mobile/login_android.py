"""Login com Google no Android, pelo seletor de contas do sistema.

Usa o Credential Manager, a API atual do Android para "Fazer login com o
Google" (a antiga, GoogleSignInClient, foi descontinuada). O sistema mostra
as contas do aparelho; o app recebe só um token de identidade assinado pelo
Google, que autenticacao.Firebase troca por uma sessão.

Requisitos no buildozer.spec: androidx ligado e as bibliotecas
androidx.credentials e googleid (android.gradle_dependencies). No Google,
o app precisa estar registrado com o nome do pacote e a impressão digital
SHA-1 do certificado que assina o APK (docs/LOGIN_GOOGLE.md).
"""

import threading

from autenticacao import ErroLogin, LoginCancelado, conferir_token, criar_nonce

TIPO_TOKEN_GOOGLE = "com.google.android.libraries.identity.googleid.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL"
TEMPO_LIMITE = 180   # segundos para escolher a conta


class LoginAndroid:
    def __init__(self, cfg):
        self.cfg = cfg

    def __call__(self, cancelar=None):
        """Devolve (id_token, nonce_bruto). Bloqueia: rode fora da interface."""
        from android.runnable import run_on_ui_thread
        from jnius import PythonJavaClass, autoclass, cast, java_method

        nonce_bruto, nonce_hash = criar_nonce()
        pronto = threading.Event()
        resultado = {}

        class Retorno(PythonJavaClass):
            __javainterfaces__ = ["androidx/credentials/CredentialManagerCallback"]
            __javacontext__ = "app"

            @java_method("(Ljava/lang/Object;)V")
            def onResult(self, resposta):
                try:
                    credencial = cast("androidx.credentials.GetCredentialResponse",
                                      resposta).getCredential()
                    if credencial.getType() != TIPO_TOKEN_GOOGLE:
                        resultado["erro"] = ErroLogin("O Android não devolveu uma conta Google.")
                    else:
                        token = autoclass("com.google.android.libraries.identity.googleid."
                                          "GoogleIdTokenCredential").createFrom(
                            credencial.getData())
                        resultado["token"] = token.getIdToken()
                except Exception as erro:   # noqa: BLE001 (vem do Java)
                    resultado["erro"] = ErroLogin(f"Não foi possível ler a conta ({erro}).")
                pronto.set()

            @java_method("(Ljava/lang/Object;)V")
            def onError(self, excecao):
                nome = excecao.getClass().getSimpleName()
                if "Cancellation" in nome:
                    resultado["erro"] = LoginCancelado("Login cancelado.")
                elif "NoCredential" in nome:
                    resultado["erro"] = ErroLogin("Nenhuma conta Google neste aparelho. Adicione "
                                                  "uma em Configurações › Contas.")
                else:
                    resultado["erro"] = ErroLogin("Não foi possível entrar com o Google agora.")
                pronto.set()

        retorno = Retorno()   # referência viva até o fim: o Java só guarda um ponteiro
        sinal = autoclass("android.os.CancellationSignal")()

        @run_on_ui_thread
        def pedir():
            atividade = autoclass("org.kivy.android.PythonActivity").mActivity
            opcao = autoclass("com.google.android.libraries.identity.googleid."
                              "GetSignInWithGoogleOption$Builder")(self.cfg["webClientId"]) \
                .setNonce(nonce_hash).build()
            pedido = autoclass("androidx.credentials.GetCredentialRequest$Builder")() \
                .addCredentialOption(opcao).build()
            fabrica = autoclass("androidx.credentials.CredentialManager")
            try:
                gerenciador = fabrica.create(atividade)        # @JvmStatic
            except Exception:   # noqa: BLE001
                gerenciador = fabrica.Companion.create(atividade)
            executor = autoclass("androidx.core.content.ContextCompat").getMainExecutor(atividade)
            gerenciador.getCredentialAsync(atividade, pedido, sinal, executor, retorno)

        pedir()
        esperado = 0.0
        while not pronto.wait(0.3):
            esperado += 0.3
            if (cancelar is not None and cancelar.is_set()) or esperado > TEMPO_LIMITE:
                sinal.cancel()
                raise LoginCancelado("Login cancelado.")
        if "erro" in resultado:
            raise resultado["erro"]
        conferir_token(resultado["token"], self.cfg["webClientId"], nonce_hash)
        return resultado["token"], nonce_bruto
