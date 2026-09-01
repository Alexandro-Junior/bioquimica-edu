[app]

# (str) Título da aplicação
title = BioquímicaEDU

# (str) Nome do pacote
package.name = bioquimiaedu

# (str) Domínio do pacote (reverse notation)
package.domain = br.unicid

# (source.dir) Diretório raiz do projeto
source.dir = .

# (source.include_exts) Extensões de arquivo a incluir
source.include_exts = py,png,jpg,kv,atlas,json,csv

# (source.include_patterns) Padrões de arquivo/pasta
source.include_patterns = data/*

# (source.exclude_exts) Extensões a excluir
source.exclude_exts = spec

# (source.exclude_patterns) Padrões a excluir
source.exclude_patterns = tests/*,bin/*

# (version) Versão da aplicação
version = 0.1

# (str) Arquivo de entrada (o que será executado)
presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Ícone da aplicação
icon.filename = %(source.dir)s/assets/icon.png

# (str) Orientação: portrait, landscape, ou user
orientation = portrait

# (bool) Modo fullscreen
fullscreen = 0

# (string) Requerimentos Python
requirements = python3,kivy,matplotlib

# (str) Permissões Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (list) Recursos Android
android.features =

# (int) API target
android.api = 32

# (int) API mínima
android.minapi = 21

# (str) Android NDK
android.ndk = 25b

# (bool) Usar legacy build tools
android.skip_update = False

# (str) Gradle dependencies
android.gradle_dependencies =

# (list) Java classes para adicionar ao APK
android.add_src =

# (str) OUYA console category
android.ouya.category = GAME

# (str) Firewall - modo de firewall
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Tempo limite de compilação em segundos
warn_on_root = 1
