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

# (list) Pastas que não vão para o APK (relatório, documentação, testes)
source.exclude_dirs = .git,.claude,.buildozer,bin,__pycache__,.venv,venv,tests,relatorio,docs,android

# (list) Arquivos só da versão desktop, geradores e dados locais do computador
source.exclude_patterns = main_enhanced.py,tela_painel.py,tela_revisao.py,painel_inicio.py,criar_imagens.py,criar_assets_mobile.py,criar_logo.py,ollama_ia.py,test_*.py,data/progresso.json,data/preferencias_mobile.json

# (str) Versão da aplicação
version = 0.4

# (list) Requerimentos Python.
# matplotlib saiu: só serve para gerar as imagens no computador
# (criar_imagens.py) e deixava o APK muito maior.
requirements = python3,kivy==2.3.1

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
# Nenhuma: o app funciona offline e guarda o progresso na pasta privada do
# próprio app, então não precisa de internet nem de acesso ao armazenamento.
android.permissions =

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

# (list) Arquiteturas: celulares atuais e antigos
android.archs = arm64-v8a, armeabi-v7a

# (bool) Aceita a licença do SDK automaticamente
android.accept_sdk_license = True

# (bool) Permite o backup do próprio Android (progresso e preferências vão
# para a conta Google do estudante, se ele tiver o backup ligado no
# aparelho). Não há senha nem token no app; se um dia houver login, os
# tokens devem ser excluídos do backup (android.backup_rules).
android.allow_backup = True

[buildozer]

# (int) Nível de log (0 = só erros, 1 = info, 2 = debug)
log_level = 2

# (int) Aviso ao rodar como root
warn_on_root = 1
