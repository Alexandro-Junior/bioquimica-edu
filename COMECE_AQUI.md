# 🚀 BioquímicaEDU — COMECE AQUI

## Você está pronto!

3 versões funcionando:
- ✅ **Desktop puro** (`main.py`)
- ✅ **Desktop + IA** (`main_enhanced.py`)  
- ✅ **Mobile** (`main_kivy_completo.py`)

---

## 5 Minutos para Começar

### Opção 1️⃣: Desktop (mais rápido)
```bash
python main.py
```
- Inicia em < 1 segundo
- 20 marcadores + flashcards + quiz + casos
- Sem dependências externas
- 100% offline

### Opção 2️⃣: Desktop + Tutor IA (melhor)
```bash
# Pré-requisito único:
ollama pull mistral

# Depois:
python main_enhanced.py
```
- Tutor IA conversacional
- Quiz dinâmico gerado por IA
- Diagnóstico com feedback inteligente
- Pode rodar offline após modelo baixado

### Opção 3️⃣: Mobile (experimental)
```bash
python main_kivy_completo.py
```
- Interface touch-friendly (480×960)
- Mesmos 5 modos: Estudo/Flashcards/Quiz/Diagnóstico/Tutor
- Funciona online/offline
- Pronto para compilar Android APK

---

## Tudo Pronto?

```bash
# Validar setup
python test_simple.py
```

Saída esperada:
```
[1] Verificando imports...
    OK: Kivy
    OK: main_kivy_completo.py
[2] Verificando arquivos de dados...
    OK: marcadores.csv (20 itens)
    OK: flashcards.json (52 itens)
    OK: quiz_perguntas.json (12 itens)
    OK: casos_clinicos.json (5 itens)
[3] Verificando classes...
    OK: Todas as classes importam
[4] Testando app initialization...
    OK: App criada
[RESULTADO] SUCESSO!
```

---

## 📁 Estrutura

```
bioquimica_edu/
├── main.py                 ← Desktop puro
├── main_enhanced.py        ← Desktop + IA Ollama
├── main_kivy_completo.py   ← Mobile (Kivy)
├── ollama_ia.py            ← Módulo IA compartilhado
├── test_simple.py          ← Validação
│
├── data/
│   ├── marcadores.csv         (20 biomarcadores)
│   ├── flashcards.json        (50 perguntas/respostas)
│   ├── marcadores_extras.json (vídeos + exemplos)
│   ├── quiz_perguntas.json    (12 questões)
│   └── casos_clinicos.json    (5 casos)
│
└── docs/
    ├── GUIA_IA.md        (como usar Ollama)
    ├── GUIA_MOBILE.md    (como compilar Android/iOS)
    ├── RESUMO_IMPLEMENTACAO.md  (features completas)
    └── ROADMAP_MELHORIAS.md     (v0.3, v1.0, v2.0)
```

---

## 🎯 O que você tem

### 📚 Modo Estudo
- 20 marcadores bioquímicos
- Interpretações clínicas
- Vídeos YouTube integrados
- Exemplos com casos clínicos

### 🎴 Flashcards
- 50 cards para memorização
- Tap para virar (pergunta/resposta)
- Sistema de navegação

### 🧠 Quiz
- 12 perguntas pré-feitas
- Feedback instantâneo
- Explicações clínicas
- Dinâmicas via IA (versão enhanced)

### 🩺 Diagnóstico
- 5 casos clínicos reais
- Análise de exames
- Diagnóstico diferencial
- Conduta terapêutica

### 💬 Tutor IA (Desktop Enhanced + Mobile)
- Chat conversacional
- Pergunta sobre qualquer marcador
- Offline com fallback inteligente
- Recomendações personalizadas

---

## ⚙️ Dependências

### Mínimas
```bash
pip install kivy pillow requests
```

### Para IA (opcional)
```bash
pip install ollama
ollama pull mistral  # ~4.7 GB
```

### Para compilar APK
```bash
pip install buildozer cython
```

---

## 🎨 Cores (Reagentes Bioquímicos)

| Cor | Uso | Reagente |
|-----|-----|----------|
| 🟢 Verde | Botões, positivo | Fehling |
| 🔴 Vermelho | Alerta, crítico | Heme |
| 🟠 Âmbar | Atenção, aviso | Bile |
| 🔵 Azul | Informação, link | Cobalto |
| 🟣 Roxo | Destaque, premium | Biuret |

---

## 📊 Dados Inclusos

✅ 20 Marcadores (ALT, AST, Glicose, Creatinina, K+, Troponina...)
✅ 50 Flashcards
✅ 12 Quiz Questions  
✅ 5 Casos Clínicos Reais
✅ 16 Vídeos YouTube
✅ 20+ Exemplos com Diagnóstico & Conduta

---

## 🚀 Próximas Versões

**v0.3**: Gamification (badges, achievements)
**v1.0**: Play Store + App Store
**v2.0**: 50+ marcadores, IA adaptativa

---

## 📞 Suporte

Problemas? Verificar:

1. **Kivy não encontrado**
   ```bash
   pip install kivy --upgrade
   ```

2. **Ollama não funciona**
   - Baixar em https://ollama.com
   - `ollama pull mistral`

3. **Dados não carregam**
   - Verificar `data/` existe no mesmo diretório
   - Validar JSONs: `python -m json.tool data/*.json`

4. **APK muito grande**
   - Ver seção "Buildozer" em GUIA_MOBILE.md

---

## ✨ Você está pronto!

Escolha uma versão e comece:

```bash
# Rápido & simples
python main.py

# Com tutor IA (melhor!)
python main_enhanced.py

# Mobile
python main_kivy_completo.py
```

**Bom estudo! 📚**

---

*BioquímicaEDU — UNICID PIBIC/CNPq*  
*Desenvolvido com Claude (Anthropic)*
