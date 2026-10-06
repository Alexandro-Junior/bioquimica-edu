[app]

# (str) Título da aplicação
title = BioquímicaEDU

# (str) Nome do pacote (antes "bioquimiaedu", com erro de digitação)
package.name = bioquimicaedu

# (str) Domínio do pacote (notação reversa)
package.domain = br.unicid

# (str) Diretório raiz do projeto.
# O Android sempre executa main.py. O main.py detecta o celular e abre a
# versão mobile (pasta mobile/); no computador ele continua abrindo a
# versão desktop.
source.dir = .

# (list) Extensões incluídas no APK
source.include_exts = py,png,json,csv

# (list) Pastas incluídas
source.include_patterns = data/*,data/images/*,mobile/*,assets/*

# (list) Pastas que não vão para o APK
source.exclude_dirs = .git,.claude,.buildozer,bin,__pycache__,.venv,venv,tests

# (list) Arquivos só da versão desktop, geradores e dados locais
source.exclude_patterns = main_enhanced.py,tela_painel.py,tela_revisao.py,painel_inicio.py,criar_imagens.py,criar_assets_mobile.py,ollama_ia.py,test_*.py,data/progresso.json

# (str) Versão da aplicação
version = 0.3

# (list) Requerimentos Python.
# matplotlib saiu: só serve para gerar as imagens no computador
# (criar_imagens.py) e deixava o APK muito maior.
requirements = python3,kivy==2.3.1

# (str) Tela de abertura e ícone — gere com: python criar_assets_mobile.py
presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png

# (str) Cor de fundo da abertura, igual ao fundo do app
android.presplash_color = #F6F4EF

# (str) Orientação
orientation = portrait

# (bool) Tela cheia
fullscreen = 0

# (list) Permissões Android.
# Nenhuma: o app funciona offline e guarda o progresso na pasta privada do
# próprio app, então não precisa de internet nem de acesso ao armazenamento.
android.permissions =

# (int) API alvo (targetSdkVersion).
# Desde 31/08/2026 o Google Play exige API 36 (Android 16) para apps novos.
# Se o python-for-android instalado ainda não suportar 36, atualize
# buildozer e python-for-android antes de compilar.
android.api = 36

# (int) API mínima (Android 5.0)
android.minapi = 21

# (list) Arquiteturas: celulares atuais e antigos
android.archs = arm64-v8a, armeabi-v7a

# (bool) Aceita a licença do SDK automaticamente
android.accept_sdk_license = True

# (bool) Permite backup do Android (inclui o progresso do estudante)
android.allow_backup = True

[buildozer]

# (int) Nível de log (0 = só erros, 1 = info, 2 = debug)
log_level = 2

# (int) Aviso ao rodar como root
warn_on_root = 1
