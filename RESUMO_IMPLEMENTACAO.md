# 📱 BioquímicaEDU — IMPLEMENTAÇÃO COMPLETA v0.2

## ✅ O que foi entregue

### 1. **Versão Desktop COMPLETA** (`main.py`)
- ✅ 20 marcadores com interface Duolingo-style
- ✅ 50 flashcards integrados
- ✅ 12 quiz questions com feedback
- ✅ 5 casos clínicos simulados
- ✅ Suporte a vídeos YouTube + exemplos clínicos
- ✅ Sistema de pontos (XP + Streak)
- ✅ 100% privado (offline)

**Tela Inicial**: Caminho em zíper com botões circulares 3D
**Estudo**: Split-panel esquerda/direita + 3 abas (Info/Vídeos/Exemplos)
**Quiz**: Barra de progresso + múltipla escolha com cores
**Diagnóstico**: Análise de casos clínicos

### 2. **Versão Desktop + IA** (`main_enhanced.py`)
- ✅ Chat com tutor Ollama local
- ✅ Quiz dinâmico (gerado por IA)
- ✅ Diagnóstico socrático (feedback inteligente)
- ✅ Fallback offline quando Ollama indisponível
- ✅ 3 modelos suportados: mistral, phi, neural-chat

**Requisito**: Ollama instalado + modelo baixado
```bash
ollama pull mistral  # ~4.7 GB
```

### 3. **Versão Mobile COMPLETA** (`main_kivy_completo.py`)
- ✅ 5 modos totalmente implementados:
  - 📚 Estudo (com abas, vídeos, exemplos)
  - 🎴 Flashcards (50 cards flip, navegação)
  - 🧠 Quiz (10 perguntas dinâmicas, feedback)
  - 🩺 Diagnóstico (5 casos interativos)
  - 💬 Tutor IA (chat offline com pattern matching)

**Interface**: Touch-optimized (56px+ buttons, 480×960 portrait)
**Performance**: Sem dependência externa (funciona offline)
**Privacidade**: 100% local, sem dados na nuvem

---

## 📂 Estrutura de Arquivos

```
bioquimica_edu/
│
├── main.py                    ← Desktop puro (Tkinter)
├── main_enhanced.py           ← Desktop + IA (Tkinter + Ollama)
├── main_kivy_completo.py      ← Mobile completo (Kivy)
├── main_kivy.py              ← Mobile básico (estudos anteriores)
│
├── ollama_ia.py              ← Módulo IA compartilhado
│
├── data/
│   ├── marcadores.csv             (20 marcadores)
│   ├── flashcards.json            (50 perguntas/respostas)
│   ├── marcadores_extras.json     (vídeos + exemplos)
│   ├── quiz_perguntas.json        (12 questões)
│   └── casos_clinicos.json        (5 casos)
│
├── GUIA_IA.md                 ← Configurar Ollama
├── GUIA_MOBILE.md             ← Compilar APK/iOS
├── ROADMAP_MELHORIAS.md       ← Futuras versões
└── requirements.txt           ← Dependências
```

---

## 🚀 COMO USAR

### **Opção A: Desktop Puro** (SEM internet)
```bash
python main.py
```
- Nenhuma dependência externa
- Rápido: inicia em <1s
- Funciona offline 100%
- Sem IA (mas tem quiz e cases)

### **Opção B: Desktop + Tutor IA** (requer Ollama)
```bash
# Pré-requisito: Ollama instalado
ollama pull mistral

# Depois:
python main_enhanced.py
```
- Chat conversacional sobre marcadores
- Quiz gerado dinamicamente por IA
- Diagnóstico com feedback socrático
- PODE RODAR OFFLINE após modelo baixado

### **Opção C: Mobile** (Android/iOS)
```bash
# Teste no PC/Mac:
python main_kivy_completo.py

# Compilar APK (Android):
pip install buildozer cython
buildozer android debug

# iOS (Mac only):
pip install kivy-ios
toolchain create BioquimicaEDU .
```

---

## 🎯 Características por Versão

| Recurso | Desktop | Desktop+IA | Mobile |
|---------|---------|-----------|--------|
| 📚 Estudo | ✅ | ✅ | ✅ |
| 🎴 Flashcards | ✅ | ✅ | ✅ |
| 🧠 Quiz | ✅ | ✅ (dinâmico) | ✅ |
| 🩺 Diagnóstico | ✅ | ✅ (c/ feedback IA) | ✅ |
| 💬 Chat IA | ❌ | ✅ | ✅ (offline) |
| 🎥 Vídeos | ✅ | ✅ | ✅ |
| 📊 XP/Streak | ✅ | ✅ | ✅ |
| Offline | ✅ | ✅* | ✅ |
| Internet | ❌ | ❌* | ❌ |

*Desktop+IA funciona offline APÓS baixar modelo Ollama

---

## 🎨 Paleta de Cores (Reagentes Bioquímicos)

```python
Verde Fehling (primária):   #16A44A  - Botões, ações positivas
Vermelho Heme:             #E11D48  - Alerta, diagnósticos críticos
Âmbar Bile:                #F69E3D  - Atenção, abas secundárias
Azul Cobalto:              #1D88B2  - Informações, links
Roxo Biuret:               #7C3A92  - Destaque, premium
Cinza Texto:               #1F2B37  - Textos principais
```

---

## 📊 Dados Integrados

### **Marcadores** (20)
Hepatocelulares (ALT, AST, GGT) | Renais (Creatinina, Ureia) | Glicêmicos (Glicose, HbA1c) | Lipídicos (Colesterol, Triglicerídeos) | Eletrolíticos (Na, K, Cl) | Cardíacos (Troponina, CK-MB)

### **Flashcards** (50)
Definições, valores normais, interpretações, casos associados

### **Quiz** (12 + dinâmico)
Múltipla escolha com explicações clínicas detalhadas

### **Diagnóstico** (5)
1. Hepatite Viral A
2. Infarto do Miocárdio  
3. Insuficiência Renal Aguda
4. Diabetes Tipo 2 Descompensada
5. Hipercolesterolemia Familiar

### **Vídeos** (16)
YouTube embeds para 8 marcadores principais

### **Exemplos** (20+)
Casos clínicos com valores, diagnóstico e conduta terapêutica

---

## 🔧 Configuração & Troubleshooting

### Instalar Dependências
```bash
pip install kivy pillow requests
```

### Se Kivy não funciona
```bash
pip install kivy --upgrade --force-reinstall
```

### Rodar Teste de Validação
```bash
python test_kivy_completo.py
```

### Ollama não encontrado (Desktop+IA)
Solução: Baixar em https://ollama.com
```bash
ollama pull mistral
```

### APK muito grande
Remover assets desnecessários:
```bash
buildozer android debug -Wall  # Ver avisos
```

---

## ✨ Próximas Fases

### v0.3 (Gamification)
- 🏆 Badges & achievements
- 📈 Gráficos de progresso
- 🎯 Objetivos diários

### v1.0 (Publicação)
- 📱 Play Store (Android)
- 🍎 App Store (iOS)
- ☁️ Cloud sync opcional
- 🌐 Multi-idioma

### v2.0 (Expansão)
- 50+ marcadores
- Mais cases clínicos
- IA adaptativa (ajusta dificuldade)
- Comunidade & social

---

## 📚 Referências Técnicas

**Frameworks**:
- Tkinter (desktop nativo Windows/Mac/Linux)
- Kivy (mobile cross-platform, Python puro)

**Dados**:
- CSV: marcadores.csv (20 linhas)
- JSON: flashcards (50), quiz (12), cases (5)

**IA**:
- Ollama local (mistral, 7B parameters, 4.7GB)
- Fallback offline (pattern matching + responses.json)

**Privacidade**:
- 100% dados locais
- Zero transmissão externa
- LGPD compliant

---

## 🎓 Autoria

**BioquímicaEDU** — UNICID PIBIC/CNPq

Aluno: Alexandro de Araujo Junior  
Orientador: Francisco de Assis Cavallaro

Desenvolvido com Claude (Anthropic)
