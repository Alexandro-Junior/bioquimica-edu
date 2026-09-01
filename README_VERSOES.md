# BioquímicaEDU — Versões Desktop e Mobile

## Dois aplicativos, uma data

Este projeto inclui **duas versões do mesmo software educacional**, com mesmos dados e lógica, mas interfaces otimizadas para cada plataforma.

---

## 🖥️ VERSÃO DESKTOP (Tkinter)

### Arquivo: `main.py`

### Como executar:
```bash
python main.py
```

### Requisitos:
- Python 3.9+
- Tkinter (incluído no Python)
- **Sem dependências externas**

### Características:
- ✅ Resolução: 1100×720px (ou maior)
- ✅ Interface com cards Duolingo-like
- ✅ Nós circulares de lição no caminho inicial
- ✅ Botões 3D com sombra
- ✅ Barra de progresso arredondada com reflexo
- ✅ Rodapé com instituição
- ✅ Gamificação em sessão (XP + streak)
- ✅ Suporta 20 marcadores, 12 perguntas, 5 casos clínicos

### Plataformas:
- Windows ✅
- macOS ✅
- Linux ✅

### Vantagens:
- Execução imediata (sem instalação extra)
- Resolução alta, mais informação visível
- Gráficos e ícones nítidos
- Excelente para apresentações/laboratório

### Desvantagens:
- Não toca (Desktop apenas)
- Foco mouse, não touch-friendly

---

## 📱 VERSÃO MOBILE (Kivy)

### Arquivo: `main_mobile.py`

### Como executar (emulador local):
```bash
pip install kivy
python main_mobile.py
```

### Compilar para Android:
```bash
pip install buildozer
buildozer android debug
# Gera: bin/bioquimiaedu-0.1-debug.apk
```

### Compilar para iOS:
```bash
pip install kivy-ios
# (Requer Mac + Xcode)
```

### Características:
- ✅ Resolução: 480×960px (portrait)
- ✅ Interface touch-optimized
- ✅ Botões grandes (56px altura)
- ✅ Scroll nativo e fluido
- ✅ Cards verticais (sem caminho zigue-zague)
- ✅ Popups para detalhe de marcadores
- ✅ Mesma paleta de cores (reagentes)
- ✅ Gamificação mantida (XP + streak)

### Plataformas:
- Android 5.0+ ✅
- iOS 11+ ✅
- Windows/Mac/Linux (emulador) ✅

### Vantagens:
- Toque nativo e responsivo
- Portabilidade (leva na mochila)
- App store ready
- Performance otimizada para mobile

### Desvantagens:
- Requer Kivy (instalação adicional)
- Build Android requer JDK + SDK (~2GB)
- Menos informação por tela (portrait)

---

## 📊 Comparação Lado a Lado

| Aspecto | Desktop (Tkinter) | Mobile (Kivy) |
|---|---|---|
| **Arquivo** | `main.py` | `main_mobile.py` |
| **Resolução** | 1100×720 | 480×960 |
| **Orientação** | Qualquer | Portrait |
| **Instalação** | Apenas Python | Python + Kivy |
| **Build Android** | ❌ Não | ✅ Sim (Buildozer) |
| **Build iOS** | ❌ Não | ✅ Sim (Kivy-iOS) |
| **Toque** | ❌ Não | ✅ Sim |
| **Mouse hover** | ✅ Sim | ❌ Não |
| **Botões 3D** | ✅ Sim (Canvas) | ⚠️ 2D flat |
| **Dados** | 20 marc., 12 quiz, 5 casos | Idênticos |
| **Cores** | Paleta bioquímica | Mesma paleta |
| **XP/Streak** | ✅ Em sessão | ✅ Em sessão |

---

## 🚀 Qual usar?

### Use **Desktop** se:
- Instalar em **laboratório/sala de aula** (PC compartilhado)
- Quer **resolução alta** (mais conteúdo visível)
- Não precisa de portabilidade
- Quer **executar hoje** (sem compilação)

### Use **Mobile** se:
- Alunos vão usar no **smartphone pessoal**
- Quer **app na Google Play ou App Store**
- Prefere **UX touch-friendly**
- Vai usar em **qualquer lugar** (on-the-go)

### Ideal: **Ambas!**
- Laboratório: Desktop
- Estudo individual: Mobile
- Mesmos dados, mesma lógica educacional

---

## 📁 Estrutura do Projeto

```
bioquimica_edu/
│
├── main.py                      # Desktop (Tkinter) ⭐
├── main_mobile.py               # Mobile (Kivy) 📱
│
├── data/
│   ├── marcadores.csv           # 20 marcadores bioquímicos
│   ├── quiz_perguntas.json      # 12 perguntas
│   └── casos_clinicos.json      # 5 casos clínicos
│
├── LEIA-ME.md                   # Instruções gerais
├── INSTALAR_MOBILE.md           # Setup Android/iOS
├── README_VERSOES.md            # Este arquivo
├── buildozer.spec               # Config para build Android
│
└── assets/                      # (Criar para mobile)
    ├── icon.png                 # Ícone da app
    └── presplash.png            # Splash screen
```

---

## 🔄 Sincronização de Dados

Ambas as versões **usam os mesmos arquivos JSON/CSV** em `data/`:
- Atualize `marcadores.csv` → ambas refletem
- Atualize `quiz_perguntas.json` → ambas refletem
- Atualize `casos_clinicos.json` → ambas refletem

**Não há duplicação de dados.** Edite uma vez, rode em qualquer plataforma.

---

## 📝 Próximos Passos

1. **Desktop**: ✅ Pronto para uso
2. **Mobile (emulador)**: 
   ```bash
   pip install kivy
   python main_mobile.py
   ```
3. **Mobile (Android APK)**:
   ```bash
   pip install buildozer
   buildozer android debug
   ```
4. **Mobile (iOS)**:
   - Requer Mac + Xcode + Kivy-iOS

---

## 🐛 Problemas Conhecidos

### Desktop (Tkinter)
- Em Windows 11 com escala 150%, botões podem parecer pequenos
  - **Solução**: Ajuste a janela manualmente

### Mobile (Kivy)
- Buildozer requer ~2GB disco (JDK + SDK)
  - **Solução**: Use Kivy Cloud online
- App pode travar se `data/` não estiver no mesmo dir
  - **Solução**: `cp -r data main_mobile.py /seu/diretorio/`

---

## 📞 Suporte

Versão Desktop: Compatível com Python 3.9+, Tkinter nativo
Versão Mobile: Compatível com Kivy 2.0+

Para erros específicos:
- Desktop: Abra issue com erro Tkinter
- Mobile: Cite versão Kivy (`kivy --version`)

---

## 📜 Licença & Créditos

- **Projeto**: BioquímicaEDU
- **Instituição**: Universidade Cidade de São Paulo (UNICID) — PIBIC/CNPq
- **Aluno**: Alexandro de Araujo Junior
- **Orientador**: Francisco de Assis Cavallaro
- **Tecnologias**: Python, Tkinter (Desktop), Kivy (Mobile)
- **Paleta**: Cores baseadas em reagentes bioquímicos (Fehling, heme, bile, fenolftaleína, biureto)
