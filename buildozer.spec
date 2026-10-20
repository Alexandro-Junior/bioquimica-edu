[app]

# (str) Título da aplicação
title = BioquímicaEDU

# (str) Nome do pacote (antes "bioquimiaedu", com erro de digitação)
package.name = bioquimicaedu

# (str) Domínio do pacote (notação reversa)
package.domain = br.unicid

# (str) Diretório raiz do projeto.
# O Android sempre executa main.py, que abre o app da pasta mobile/. No
# computador, o main.py abre o mesmo app; a versão antiga, em Tkinter, só
# com --classico.
source.dir = .

# (list) Extensões incluídas no APK
source.include_exts = py,png,json,csv,ttf

# (list) Pastas incluídas
source.include_patterns = data/*,data/images/*,mobile/*,assets/*

# (list) Pastas que não vão para o APK (relatório, documentação, testes)
source.exclude_dirs = .git,.claude,.buildozer,bin,__pycache__,.venv,venv,tests,relatorio,docs,android,servidor,empacotamento,firebase,dist,build

# (list) Arquivos só da versão desktop, geradores e dados locais do computador.
# .env guarda a chave do Gemini do computador: nunca vai para o APK.
source.exclude_patterns = main_enhanced.py,tela_painel.py,tela_revisao.py,painel_inicio.py,criar_imagens.py,criar_assets_mobile.py,criar_logo.py,criar_capturas_site.py,main_kivy_completo.py,ollama_ia.py,test_*.py,data/progresso.json,data/preferencias_mobile.json,data/sessao_google.dat,.env,data/*.tmp,data/progresso.ilegivel-*,config/firebase.exemplo.json

# (str) Versão da aplicação
version = 0.5

# (list) Requerimentos Python.
# matplotlib saiu: só serve para gerar as imagens no computador
# (criar_imagens.py) e deixava o APK muito maior.
# certifi: certificados para a conexão HTTPS do tutor com IA (o Python do
# Android não enxerga os do sistema).
requirements = python3,kivy==2.3.1,certifi

# (str) Tela de abertura e ícone — gere com: python criar_logo.py
presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png

# (str) Ícone adaptativo (Android 8+): sem ele, o sistema encaixa o ícone
# quadrado dentro de uma máscara e ele aparece "numa caixinha".
icon.adaptive_foreground.filename = %(source.dir)s/assets/icone_frente.png
icon.adaptive_background.filename = %(source.dir)s/assets/icone_fundo.png

# (str) Cor de fundo da abertura, igual ao fundo do app
android.presplash_color = #F6F4EF

# (str) Orientação
orientation = portrait

# (bool) Tela cheia
fullscreen = 0

# (list) Permissões Android.
# Só internet, usada pelo login com Google (opcional) e pelo tutor com IA.
# O estudo funciona offline, e o progresso fica na pasta privada do app,
# sem permissão de armazenamento.
android.permissions = INTERNET

# (bool / list) Login com Google pelo seletor de contas do Android
# (Credential Manager; mobile/login_android.py)
android.enable_androidx = True
# androidx.core vai explícita: só como dependência das outras, ficou fora do
# APK, e o login parava com ClassNotFoundException (ContextCompat).
# empacotamento/conferir_apk.py confere isso a cada APK gerado.
android.gradle_dependencies = androidx.core:core:1.13.1, androidx.credentials:credentials:1.3.0, androidx.credentials:credentials-play-services-auth:1.3.0, com.google.android.libraries.identity.googleid:googleid:1.1.1

# (str) Trecho extra do manifesto: declara a consulta ao serviço de voz
# (leitura em voz alta) e ao app VLibras (atalho para Libras), exigida a
# partir do Android 11. Não é permissão.
android.extra_manifest_xml = ./android/extra_manifest.xml

# (int) API alvo (targetSdkVersion).
# Desde 31/08/2026 o Google Play exige API 36 (Android 16) para apps novos.
# Se o python-for-android instalado ainda não suportar 36, atualize
# buildozer e python-for-android antes de compilar.
android.api = 36

# (int) API mínima (Android 5.0)
android.minapi = 21

# (list) Arquiteturas: só a de 64 bits, a dos celulares e tablets atuais e a
# que a Google Play exige. Com duas, o python-for-android recria o mesmo venv
# para a segunda e deixa o pip quebrado ("cannot import name
# BuildDependencyInstallError"), e o APK não sai.
android.archs = arm64-v8a

# (bool) Aceita a licença do SDK automaticamente
android.accept_sdk_license = True
# APK, e não AAB: o app é distribuído pelo site, fora da Google Play
android.release_artifact = apk

# (bool) Permite o backup do próprio Android (progresso e preferências vão
# para a conta Google do estudante, se ele tiver o backup ligado no
# aparelho). A sessão do login com Google fica fora do backup: é gravada
# na pasta "no backup" do aparelho (mobile/app.py, _pasta_sessao).
android.allow_backup = True

[buildozer]

# (int) Nível de log (0 = só erros, 1 = info, 2 = debug)
log_level = 2

# (int) Aviso ao rodar como root
warn_on_root = 1
