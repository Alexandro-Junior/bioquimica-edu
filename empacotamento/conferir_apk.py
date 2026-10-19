"""Confere um APK antes de ele ir para alguém testar.

    python empacotamento/conferir_apk.py caminho/do/app.apk

Falha (código 1) se:
- faltar alguma classe Java de que o login com Google depende. Uma biblioteca
  pode ficar fora do pacote e só ser notada no celular, com
  ClassNotFoundException (aconteceu com androidx.core);
- o pacote levar a chave do Gemini (.env) ou dados de quem o gerou
  (progresso, preferências, sessão).

Lê o classes*.dex direto, sem ferramentas do Android: o nome de uma classe pode
aparecer no dex só como referência, então só conta a classe que está definida.
"""

import io
import struct
import sys
import tarfile
import zipfile

CLASSES_DO_LOGIN = (
    "androidx.core.content.ContextCompat",
    "androidx.credentials.CredentialManager",
    "androidx.credentials.CredentialManagerCallback",
    "androidx.credentials.GetCredentialRequest$Builder",
    "androidx.credentials.playservices.CredentialProviderPlayServicesImpl",
    "com.google.android.libraries.identity.googleid.GetSignInWithGoogleOption$Builder",
    "com.google.android.libraries.identity.googleid.GoogleIdTokenCredential",
    "org.kivy.android.PythonActivity",
)
ARQUIVOS_PROIBIDOS = (".env", "progresso.json", "preferencias_mobile.json", "preferencias.json",
                      "sessao_google.dat")


def classes_definidas(dex):
    """Nomes (com pontos) das classes definidas num arquivo .dex."""
    def u32(posicao):
        return struct.unpack_from("<I", dex, posicao)[0]

    def texto(indice):
        posicao = u32(u32(0x3C) + 4 * indice)
        while dex[posicao] & 0x80:   # pula o tamanho (ULEB128)
            posicao += 1
        fim = dex.index(b"\0", posicao + 1)
        return dex[posicao + 1:fim].decode("utf-8", "replace")

    tipos, definicoes = u32(0x44), u32(0x64)
    nomes = set()
    for i in range(u32(0x60)):
        descritor = texto(u32(tipos + 4 * u32(definicoes + 32 * i)))
        nomes.add(descritor[1:-1].replace("/", "."))
    return nomes


def conferir(caminho):
    problemas = []
    with zipfile.ZipFile(caminho) as apk:
        definidas = set()
        for nome in apk.namelist():
            if nome.startswith("classes") and nome.endswith(".dex"):
                definidas |= classes_definidas(apk.read(nome))
        for classe in CLASSES_DO_LOGIN:
            if classe not in definidas:
                problemas.append(f"classe ausente: {classe}")
        internos = apk.namelist()
        if "assets/private.tar" in internos:
            with tarfile.open(fileobj=io.BytesIO(apk.read("assets/private.tar"))) as tar:
                internos += tar.getnames()
        for nome in internos:
            if nome.rsplit("/", 1)[-1] in ARQUIVOS_PROIBIDOS:
                problemas.append(f"arquivo que não pode ir no APK: {nome}")
    return len(definidas), problemas


def main():
    total, problemas = conferir(sys.argv[1])
    print(f"{total} classes Java no APK")
    for problema in problemas:
        print(f"ERRO: {problema}")
    if problemas:
        sys.exit(1)
    print("APK conferido: login com Google completo, sem chave nem dados pessoais")


if __name__ == "__main__":
    main()
