# Versão Android (APK)

O APK é gerado pelo GitHub Actions ([.github/workflows/android.yml](../.github/workflows/android.yml)),
num computador Linux do GitHub, porque o Buildozer não roda no Windows.
Cada geração leva de 30 a 40 minutos (a primeira, um pouco mais).

## 1. Chave de assinatura e segredos (uma vez só)

```bash
python empacotamento/criar_chave_android.py
```

O script:

- cria a chave em `OneDrive\Documentos\BioquimicaEDU-chave-android`, ou
  reaproveita a que já existir;
- guarda no GitHub, com o seu login do `gh`, os segredos
  `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_SENHA` e
  `FIREBASE_CONFIG_JSON`, além da variável `TUTOR_SERVIDOR`;
- mostra o SHA-1 da chave.

Nenhum segredo aparece na tela.

**Guarde essa pasta.** Ela é a única cópia da chave. Sem ela, versões novas
não instalam por cima da anterior, e o login com Google precisaria ser
reconfigurado.

## 2. Registrar o app Android no Firebase (uma vez só)

O login com Google no celular só funciona se o Firebase conhecer o pacote
`br.unicid.bioquimicaedu` e o SHA-1 da chave. Isso cria, no projeto
`bioquimicaedu-cf2b2`, um app Android e o cliente OAuth correspondente.

## 3. Gerar o APK

No GitHub, abra a aba **Actions**, escolha **APK Android** e clique em **Run workflow**.
Também roda sozinho quando sai uma versão nova (tag `v*`).

O APK fica em **Artifacts** no fim da execução (`BioquimicaEDU-Android`).

Antes disso, o workflow roda `empacotamento/conferir_apk.py`, que falha se
faltar alguma biblioteca do login com Google ou se o pacote levar a chave do
Gemini ou dados pessoais. Para conferir um APK baixado:

```bash
python empacotamento/conferir_apk.py BioquimicaEDU-Android.apk
```

## 4. Publicar

O APK vai para os Releases do repositório do site, com o nome
`BioquimicaEDU-Android.apk`. No `config.js` do site, use `android.publicado: true`.

## O que vai e o que não vai no APK

| Vai | Não vai |
|---|---|
| `config/firebase.json` (vem do segredo `FIREBASE_CONFIG_JSON`) | a chave do Gemini (`.env`) |
| `config/tutor_nuvem.json`, só o endereço do servidor do tutor | progresso, preferências e sessão de quem gerou o APK |
