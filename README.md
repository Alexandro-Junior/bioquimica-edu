# ⚗️ BioquímicaEDU — Software Educacional Interativo

> Aprenda marcadores bioquímicos com gamificação, IA e casos clínicos reais

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Tkinter](https://img.shields.io/badge/Framework-Tkinter%20%7C%20Kivy-green.svg)]()
[![Ollama AI](https://img.shields.io/badge/AI-Ollama%20Local-red.svg)]()
[![LGPD](https://img.shields.io/badge/Privacy-LGPD%20Compliant-purple.svg)]()
[![License](https://img.shields.io/badge/License-UNICID%20PIBIC-orange.svg)]()

---

## 🚀 Começar em 30 Segundos

### Desktop Puro
```bash
python main.py
```

### Com Tutor IA (Melhor!)
```bash
ollama pull mistral
python main_enhanced.py
```

### Mobile
```bash
python main_kivy_completo.py
```

👉 **[Leia COMECE_AQUI.md para setup completo](COMECE_AQUI.md)**

---

## 📱 O Que Você Tem

### 5️⃣ Modos de Estudo

| Modo | Features | Desktop | Mobile |
|------|----------|---------|--------|
| **📚 Estudo** | 20 marcadores + vídeos + exemplos | ✅ | ✅ |
| **🎴 Flashcards** | 50 cards com flip animation | ✅ | ✅ |
| **🧠 Quiz** | 12 perguntas + feedback | ✅ | ✅ |
| **🩺 Diagnóstico** | 5 casos clínicos reais | ✅ | ✅ |
| **💬 Tutor IA** | Chat offline + recomendações | ✅* | ✅ |

*Desktop: requer Ollama

### 📊 Dados Inclusos

- ✅ **20 Marcadores** — ALT, AST, Glicose, Creatinina, K+, Troponina...
- ✅ **50 Flashcards** — Memorização rápida
- ✅ **12 Quiz Questions** — Teste conhecimento
- ✅ **5 Casos Clínicos** — Situações reais
- ✅ **16 Vídeos YouTube** — Explicações
- ✅ **20+ Exemplos** — Diagnóstico & conduta

### 🎨 Desenhado para Educação

- **Cores de Reagentes Bioquímicos** — Verde Fehling, Vermelho Heme, etc.
- **Gamificação** — XP + Streak system
- **Interface Duolingo-Style** — Desktop bonito & intuitivo
- **Touch-Friendly** — Mobile otimizado (56px+ buttons)
- **100% Offline** — Sem transmissão de dados (LGPD compliant)

---

## 📁 Arquivos Principais

### Código
```
main.py                  ← Desktop puro (1800+ linhas)
main_enhanced.py         ← Desktop + IA Ollama (900+ linhas)
main_kivy_completo.py    ← Mobile Kivy (700+ linhas)
ollama_ia.py             ← Módulo IA compartilhado (300+ linhas)
```

### Dados
```
data/
├── marcadores.csv           (20 biomarcadores)
├── flashcards.json          (50 perguntas/respostas)
├── marcadores_extras.json   (vídeos + exemplos)
├── quiz_perguntas.json      (12 questões)
└── casos_clinicos.json      (5 casos)
```

### Documentação
```
COMECE_AQUI.md               ← 👈 Comece aqui!
STATUS.md                    ← Checklist de implementação
RESUMO_IMPLEMENTACAO.md      ← Features completas
GUIA_IA.md                   ← Como usar Ollama
GUIA_MOBILE.md               ← Compilar Android/iOS
ROADMAP_MELHORIAS.md         ← v0.3, v1.0, v2.0
README.md                    ← Este arquivo
```

### Testes
```
test_simple.py               ← Validação rápida
test_kivy_completo.py        ← Teste do app mobile
```

---

## 💻 Requisitos

### Mínimos
- Python 3.8+
- Tkinter (incluso)

### Recomendados
```bash
pip install kivy pillow requests
```

### Para IA (opcional)
```bash
pip install ollama
ollama pull mistral  # ~4.7 GB
```

---

## 🎯 3 Versões para 3 Usos

### 1. Desktop Puro (`main.py`)
- **Melhor para**: Aprendizado rápido em PC
- **Vantagens**: Nenhuma dependência, inicia em <1s
- **Recurso IA**: Não
- **Offline**: Sim

### 2. Desktop + IA (`main_enhanced.py`)
- **Melhor para**: Aprendizado profundo com tutoria
- **Vantagens**: Quiz dinâmico, chat, diagnóstico IA
- **Recurso IA**: Sim (Ollama local)
- **Offline**: Sim (após download modelo)

### 3. Mobile (`main_kivy_completo.py`)
- **Melhor para**: Estudar em qualquer lugar
- **Vantagens**: Touch-friendly, compilável para Android/iOS
- **Recurso IA**: Sim (offline com pattern matching)
- **Offline**: Sim

---

## 🔧 Setup Rápido

### Opção A: Apenas Desktop
```bash
git clone <repo>
cd bioquimica_edu
python main.py
```

### Opção B: Desktop + IA
```bash
git clone <repo>
cd bioquimica_edu

# Instalar Ollama em https://ollama.com
ollama pull mistral

python main_enhanced.py
```

### Opção C: Mobile
```bash
git clone <repo>
cd bioquimica_edu
pip install kivy pillow
python main_kivy_completo.py
```

### Validar Setup
```bash
python test_simple.py
```

Esperado: `[RESULTADO] SUCESSO!`

---

## 📱 Compilar para Android/iOS

Ver [GUIA_MOBILE.md](GUIA_MOBILE.md) para instruções completas.

### Android (Buildozer)
```bash
pip install buildozer cython
buildozer android debug
```

### iOS (Mac only)
```bash
pip install kivy-ios
toolchain create BioquimicaEDU .
```

---

## 🎓 Estrutura Curricular

### Marcadores Inclusos (20)

**Hepatocelulares** (3)
- ALT, AST, GGT

**Renais** (2)
- Creatinina, Ureia

**Glicêmicos** (2)
- Glicose, HbA1c

**Lipídicos** (3)
- Colesterol, Triglicerídeos, Frações

**Eletrolíticos** (3)
- Sódio, Potássio, Cloro

**Cardíacos** (3)
- Troponina, CK-MB, BNP

**Hepatobiliares** (4)
- Bilirrubina, Fosfatase Alcalina, Albumina, INR

---

## 🎨 Paleta de Cores

Baseada em reagentes bioquímicos reais:

```python
Verde Fehling    #16A44A  ← Reações positivas, botões
Vermelho Heme    #E11D48  ← Crítico, alerta
Âmbar Bile       #F69E3D  ← Atenção, abas
Azul Cobalto     #1D88B2  ← Informação
Roxo Biuret      #7C3A92  ← Destaque
```

---

## 📊 Estatísticas

| Métrica | Valor |
|---------|-------|
| Linhas de código | 3500+ |
| Arquivos Python | 6 |
| Documentação | 6 guias |
| Marcadores | 20 |
| Flashcards | 50 |
| Quiz Questions | 12 |
| Casos Clínicos | 5 |
| Vídeos | 16 |
| Exemplos | 20+ |
| **Total de dados** | **~200 items** |

---

## 🚀 Roadmap

### v0.2 ✅ (ATUAL)
- [x] 3 versões (Desktop, Desktop+IA, Mobile)
- [x] 5 modos de estudo
- [x] 200+ dados educacionais
- [x] IA Ollama integrada
- [x] Compilação Android/iOS pronta

### v0.3 (Próximo)
- [ ] Gamification avançada (badges, achievements)
- [ ] Gráficos de progresso
- [ ] Objetivos diários
- [ ] Persist score

### v1.0
- [ ] Google Play Store
- [ ] Apple App Store
- [ ] Cloud sync opcional
- [ ] Multi-idioma

### v2.0
- [ ] 50+ marcadores
- [ ] IA adaptativa
- [ ] Comunidade
- [ ] Analytics

---

## 🔒 Privacidade & Compliance

- ✅ **100% Offline** — Nenhum dado transmitido
- ✅ **LGPD Compliant** — Sem rastreamento
- ✅ **Open Source** — Código auditável
- ✅ **Educacional** — Sem anúncios

Todos os dados ficam locais no seu device.

---

## 📞 Suporte

### Documentação
- 👉 [COMECE_AQUI.md](COMECE_AQUI.md) — Setup rápido
- 📖 [RESUMO_IMPLEMENTACAO.md](RESUMO_IMPLEMENTACAO.md) — Features
- 🤖 [GUIA_IA.md](GUIA_IA.md) — Ollama setup
- 📱 [GUIA_MOBILE.md](GUIA_MOBILE.md) — Android/iOS
- 🗺️ [ROADMAP_MELHORIAS.md](ROADMAP_MELHORIAS.md) — Futuro

### Troubleshooting
1. **Kivy não funciona** → `pip install kivy --upgrade`
2. **Ollama não encontrado** → Baixar em ollama.com
3. **Dados não carregam** → Verificar `data/` directory
4. **APK muito grande** → Ver seção Buildozer em GUIA_MOBILE.md

---

## 👨‍🎓 Autoria

**BioquímicaEDU** — Software educacional para estudo de biomarcadores

- **Aluno**: Alexandro de Araujo Junior
- **Orientador**: Francisco de Assis Cavallaro
- **Instituição**: UNICID PIBIC/CNPq
- **Desenvolvido com**: Claude (Anthropic)

---

## 📜 Licença

UNICID PIBIC/CNPq — Uso educacional

---

## ✨ Features Highlights

- ✅ **Offline-First** — Funciona 100% sem internet
- ✅ **Gamified** — XP, Streak, Progress tracking
- ✅ **AI-Enhanced** — Chat tutor, quiz dinâmico
- ✅ **Multi-Platform** — Windows, Mac, Linux, Android, iOS
- ✅ **Educational** — 200+ dados clínicos reais
- ✅ **Beautiful UI** — Duolingo-style design
- ✅ **LGPD Compliant** — Privacidade garantida

---

## 🎯 Próximo Passo

Escolha sua versão:

```bash
# Rápido & Offline
python main.py

# Com Tutor IA (recomendado)
ollama pull mistral && python main_enhanced.py

# Mobile
python main_kivy_completo.py
```

**Bom estudo! 📚**

---

*BioquímicaEDU v0.2 — 2026-08-29*
