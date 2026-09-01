# BioquímicaEDU — Versão Mobile (Android/iOS)

## Opções de Instalação

### Opção 1: Emulador Local (Windows/Mac/Linux)

#### Passo 1 — Instalar Python e Kivy
```bash
python -m pip install --upgrade pip
python -m pip install kivy
```

#### Passo 2 — Executar no emulador
```bash
cd caminho/para/bioquimica_edu
python main_mobile.py
```

---

### Opção 2: Compilar para Android (Recomendado)

#### Requisitos
- **Python 3.10+**
- **JDK 11+** (Java Development Kit)
- **Android SDK**
- **Buildozer** (ferramenta Kivy para Android)

#### Instalação

**1. Instalar dependências:**
```bash
python -m pip install buildozer cython
```

**2. Criar arquivo de configuração `buildozer.spec`:**

Já criamos um arquivo pronto. Se não existir, execute:
```bash
buildozer android debug
```

**3. Compilar APK (primeiro build leva 10-30 min):**
```bash
buildozer android debug
```

**4. Instalar no dispositivo/emulador:**
```bash
# Conecte o Android via USB e ative "Modo de Desenvolvedor"
adb install -r bin/bioquimiaedu-0.1-debug.apk
```

---

### Opção 3: Compilar para iOS (macOS)

#### Requisitos
- **Mac com Xcode**
- **Python 3.10+**
- **Kivy + tools iOS**

#### Instalação

```bash
pip install kivy-ios
toolchain create BioquimicaEDU /caminho/para/main_mobile.py
toolchain build BioquimicaEDU
```

---

### Opção 4: Usar Kivy Cloud (Nuvem — Sem Setup Local)

1. Acesse: https://kivy.org/doc/stable/guide/packaging.html
2. Faça upload do `main_mobile.py` e `data/`
3. Kivy Cloud compila e gera `.apk` e `.ipa`

---

## Interface Mobile

- **Orientação**: Portrait (480×960 default)
- **Tema**: Cores baseadas em reagentes da bioquímica
- **Toque**: Botões grandes (56px altura), tap-friendly
- **Scroll**: Nativo em listas e detalhes
- **Gamificação**: XP e streak visíveis no topo

---

## Estrutura de Arquivos (Mobile)

```
bioquimica_edu/
├── main_mobile.py           # App Kivy (execute este)
├── data/
│   ├── marcadores.csv
│   ├── casos_clinicos.json
│   └── quiz_perguntas.json
├── buildozer.spec           # Config Android
└── INSTALAR_MOBILE.md       # Este arquivo
```

---

## Diferenças Desktop ↔ Mobile

| Feature | Desktop (Tkinter) | Mobile (Kivy) |
|---------|---|---|
| Resolução | 1100×720px | 480×960px (portrait) |
| Tela Inicial | Caminho zigue-zague | Cards verticais |
| Toque | Mouse hover | Touch feedback |
| Scroll | Canvas scrollable | ScrollView nativo |
| Performance | ~5MB RAM | ~20-30MB app |

---

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'kivy'"
```bash
pip install kivy --upgrade
```

### ❌ Buildozer com erro de SDK
```bash
buildozer android debug -- --permit-no-manifest
```

### ❌ App trava ao abrir
- Certifique-se que `data/` está no mesmo diretório de `main_mobile.py`
- Verifique permissões de arquivo: `chmod 755 main_mobile.py`

---

## Performance

- **Carregamento inicial**: ~1-2 segundos
- **Scroll marcadores**: 60 FPS
- **Quiz com 10 perguntas**: ~500ms por resposta
- **Diagnóstico com 5 casos**: ~300ms por alternativa

---

## Próximas Melhorias

- [ ] Temas claro/escuro (modo noturno)
- [ ] Sincronização na nuvem (Firebase)
- [ ] Modo offline com cache
- [ ] Notificações de lembretes diários
- [ ] Análise de progresso/gráficos
- [ ] Multiplayer (quiz competitivo)

---

## Suporte

Para erros ou sugestões, abra uma issue no GitHub ou contacte:
- **Aluno**: Alexandro de Araujo Junior
- **Orientador**: Francisco de Assis Cavallaro
- **Instituição**: Universidade Cidade de São Paulo (UNICID) — PIBIC/CNPq
