"""Cria a chave de assinatura do APK (uma vez só) e guarda os segredos no GitHub.

    python empacotamento/criar_chave_android.py

O que faz, sem mostrar nenhum segredo na tela:
1. Cria a chave (.p12) e uma senha aleatória numa pasta sua, fora do
   projeto. Se a chave já existir, reaproveita: ela precisa ser sempre a
   mesma, porque o Firebase confere a "impressão digital" (SHA-1) dela no
   login com Google e o Android só atualiza um app assinado pela mesma chave.
2. Guarda no GitHub, com o seu login do `gh`, os segredos que o GitHub
   Actions usa para gerar o APK (.github/workflows/android.yml).
3. Mostra o SHA-1, que é público e vai para o Firebase.

GUARDE A PASTA DA CHAVE. Sem ela, nenhuma versão nova do app instala por
cima da anterior, e o login com Google precisaria ser reconfigurado.
"""

from __future__ import annotations

import base64
import datetime
import hashlib
import json
import secrets
import subprocess
import sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, pkcs12
from cryptography.x509.oid import NameOID

RAIZ = Path(__file__).resolve().parent.parent
REPOSITORIO = "Alexandro-Junior/bioquimica-edu"
APELIDO = b"bioquimicaedu"          # igual a P4A_RELEASE_KEYALIAS no workflow


def pasta_padrao() -> Path:
    for documentos in (Path.home() / "OneDrive" / "Documentos", Path.home() / "Documents"):
        if documentos.is_dir():
            return documentos / "BioquimicaEDU-chave-android"
    return Path.home() / "BioquimicaEDU-chave-android"


def criar_chave(pasta: Path) -> tuple[bytes, str]:
    senha = secrets.token_urlsafe(24)
    chave = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    nome = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "Alexandro de Araujo Junior"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "BioquimicaEDU"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "UNICID"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
    ])
    agora = datetime.datetime.now(datetime.timezone.utc)
    certificado = (x509.CertificateBuilder()
                   .subject_name(nome).issuer_name(nome)
                   .public_key(chave.public_key())
                   .serial_number(x509.random_serial_number())
                   .not_valid_before(agora - datetime.timedelta(days=1))
                   .not_valid_after(agora + datetime.timedelta(days=365 * 30))
                   .sign(chave, hashes.SHA256()))
    # PBES2 com AES-256 e MAC SHA-256: o formato que o Java 17 do GitHub lê
    cifra = (PrivateFormat.PKCS12.encryption_builder()
             .kdf_rounds(100000)
             .key_cert_algorithm(pkcs12.PBES.PBESv2SHA256AndAES256CBC)
             .hmac_hash(hashes.SHA256())
             .build(senha.encode()))
    p12 = pkcs12.serialize_key_and_certificates(APELIDO, chave, certificado, None, cifra)
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "bioquimicaedu-release.p12").write_bytes(p12)
    (pasta / "senha.txt").write_text(senha + "\n", encoding="utf-8")
    return p12, senha


def impressoes(p12: bytes, senha: str) -> tuple[str, str]:
    _chave, certificado, _outros = pkcs12.load_key_and_certificates(p12, senha.encode())
    der = certificado.public_bytes(Encoding.DER)

    def formatar(digest):
        return ":".join(f"{b:02X}" for b in digest)
    return formatar(hashlib.sha1(der).digest()), formatar(hashlib.sha256(der).digest())


def gh(*args, entrada: str | None = None) -> None:
    resultado = subprocess.run(["gh", *args, "--repo", REPOSITORIO], input=entrada,
                               capture_output=True, text=True)
    if resultado.returncode != 0:
        raise SystemExit(f"falhou: gh {' '.join(args[:3])}: {resultado.stderr.strip()}")


def main() -> None:
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else pasta_padrao()
    arquivo = pasta / "bioquimicaedu-release.p12"
    if arquivo.exists():
        p12 = arquivo.read_bytes()
        senha = (pasta / "senha.txt").read_text(encoding="utf-8").strip()
        print(f"Chave já existente, reaproveitada: {arquivo}")
    else:
        p12, senha = criar_chave(pasta)
        print(f"Chave criada: {arquivo}")
    sha1, sha256 = impressoes(p12, senha)
    (pasta / "LEIA-ME.txt").write_text(
        "Chave de assinatura do APK do BioquímicaEDU. NÃO APAGUE E NÃO COMPARTILHE.\n"
        "Sem ela, versões novas do app não instalam por cima da anterior.\n"
        "A senha está em senha.txt. O apelido (alias) da chave é: bioquimicaedu\n\n"
        f"SHA-1 (público, vai no Firebase): {sha1}\n"
        f"SHA-256 (público): {sha256}\n", encoding="utf-8")

    print("Guardando os segredos no GitHub (nada é mostrado na tela)...")
    gh("secret", "set", "ANDROID_KEYSTORE_BASE64", entrada=base64.b64encode(p12).decode())
    gh("secret", "set", "ANDROID_KEYSTORE_SENHA", entrada=senha)
    firebase = RAIZ / "config" / "firebase.json"
    if firebase.exists():
        gh("secret", "set", "FIREBASE_CONFIG_JSON", entrada=firebase.read_text(encoding="utf-8"))
        print("  login com Google: ok")
    else:
        print("  config/firebase.json não encontrado: o APK sairá sem login com Google")
    tutor = RAIZ / "config" / "tutor_nuvem.json"
    if tutor.exists():
        servidor = json.loads(tutor.read_text(encoding="utf-8")).get("servidor", "")
        if servidor:
            gh("variable", "set", "TUTOR_SERVIDOR", "--body", servidor)
            print("  tutor com IA: ok")
    print("  chave de assinatura: ok")
    print()
    print(f"SHA-1 da chave (pode me mandar, é público): {sha1}")
    print(f"Guarde a pasta {pasta}: ela é a única cópia da chave.")


if __name__ == "__main__":
    main()
