# BioquímicaEDU — Versão Mobile (Kivy)

## 📱 Características

✅ **Interface touch-optimized** — Botões grandes (56px+), scroll fluido
✅ **Responsivo** — Portrait e landscape
✅ **5 Modos de Estudo**:
   - 📚 Modo Estudo (20 marcadores + vídeos + exemplos)
   - 🎴 Flashcards (50 cards que viram)
   - 🎥 Vídeos integrados (abre YouTube)
   - 🧠 Quiz (teste seu conhecimento)
   - 🩺 Diagnóstico (casos clínicos)

✅ **Paleta Bioquímica** — Cores baseadas em reagentes
✅ **100% Privado** — Funciona offline

---

## 🚀 Como Usar (Emulador Local)

### Pré-requisitos
```bash
pip install kivy
pip install pillow  # Para imagens
```

### Executar no PC/Mac/Linux
```bash
cd caminho/para/bioquimica_edu
python main_kivy.py
```

Abre emulador **480×960** (mobile portrait)

---

## 📦 Compilar para Android (APK)

### 1. Instalar Buildozer
```bash
pip install buildozer cython
```

### 2. Baixar dependências (primeira vez)
```bash
# Windows (no WSL recomendado) ou Mac/Linux:
buildozer android debug
```

**Tempo**: ~20-30 min (primeira compilação)
**Requisitos**: JDK 11+, Android SDK (~2GB)

### 3. Instalar no Android
```bash
# Via USB (ativar "Modo Desenvolvedor" no Android)
adb install -r bin/bioquimiaedu-0.1-debug.apk

# Ou via emulador Android
emulator -avd <seu_emulador>
adb install bin/bioquimiaedu-0.1-debug.apk
```

---

## 🍎 Compilar para iOS (Mac)

### Pré-requisitos
- Mac com Xcode
- Python 3.9+
- Kivy iOS toolchain

### Instalação
```bash
pip install kivy-ios
toolchain create BioquimicaEDU .
toolchain build BioquimicaEDU
```

---

## 🎮 Como Usar no Mobile

### Tela Inicial
- **5 cards grandes** com opções
- Tap em um para entrar

### Modo Estudo (📚)
1. Tap em um marcador
2. **Abas**: Info | Vídeos | Exemplos
3. Info: Valores + interpretações
4. Vídeos: Tap em "▶ Assistir" → abre YouTube
5. Exemplos: Casos clínicos completos

### Flashcards (🎴)
1. Tap no card para virar
2. Lê pergunta ← clica → vê resposta
3. Botões: Anterior / Próximo
4. Progresso no topo

### Quiz (🧠)
1. 10 perguntas selecionadas aleatoriamente
2. Múltipla escolha com feedback instantâneo
3. Mostra explicação correta
4. Soma XP na pontuação (10 XP por acerto)
5. Resultado final em %

### Diagnóstico (🩺)
1. 5 casos clínicos reais
2. Tap em cada caso para ver detalhes
3. Analisa valores de exames (ALTO/BAIXO/NORMAL com cores)
4. Responda qual é o diagnóstico correto
5. Recebe 25 XP por acerto
6. Explicação e conduta terapêutica

### Tutor IA (💬)
1. Chat conversacional offline
2. Pergunta sobre qualquer marcador
3. Responde automaticamente com referências e interpretações
4. Não precisa de internet (fallback pattern matching)

---

## 📊 Estrutura de Arquivos

```
main_kivy.py          ← App Kivy (execute este)

data/
├── marcadores.csv
├── flashcards.json
├── marcadores_extras.json  (vídeos + exemplos)
└── casos_clinicos.json
```

---

## 🔧 Troubleshooting

### ❌ "Kivy não encontrado"
```bash
pip install kivy --upgrade
```

### ❌ Buildozer erro de SDK
```bash
# Instale manualmente:
# 1. Android Studio (https://developer.android.com)
# 2. SDK > SDK Manager > Android 11 (API 30+)
# 3. Configure variáveis de ambiente
```

### ❌ App trava ao abrir
- Certifique-se que `data/` está no mesmo diretório
- Verifique JSON files: `python -m json.tool data/*.json`

---

## 📱 Specs Recomendados

| Aspecto | Recomendado |
|---------|-------------|
| Android | 6.0+ (API 23) |
| iOS | 12+ |
| RAM | 2GB+ |
| Tela | 4.5" a 7" (portrait) |
| Orientação | Portrait + Landscape |

---

## 📊 Tamanho do APK

- **Base**: ~20-30MB
- **Com assets**: ~35-50MB
- **Comprimido (aab)**: ~15-25MB

---

## 🌐 Publicar na Play Store / App Store

### Google Play Store (Android)
1. Compilar release:
   ```bash
   buildozer android release
   ```
2. Assinar APK (keytool)
3. Fazer upload em Google Play Console

### Apple App Store (iOS)
1. Compilar com Xcode
2. Archive e validar
3. TestFlight para beta
4. Submit para aprovação

---

## ⚙️ Customizações

### Mudar tamanho de tela
Edit `main_kivy.py` linha 36:
```python
Window.size = (480, 960)  # Mudar para (1080, 1920) para tablets
```

### Mudar paleta de cores
Edit `COR` dictionary para suas cores

### Adicionar mais marcadores
Edit `data/marcadores.csv` + `data/marcadores_extras.json`

---

## 🚀 Próximas Versões

### v0.2
- ✅ Quiz funcional
- ✅ Diagnóstico completo
- ✅ Sistema de pontos

### v0.3
- ✅ Modo offline com cache
- ✅ Sincronização na nuvem
- ✅ Análise de progresso

### v1.0
- ✅ IA Tutor integrado
- ✅ Multi-idioma
- ✅ App Store + Play Store

---

## 📞 Suporte

**Instalação Kivy**:
- Docs: https://kivy.org/doc/stable/

**Buildozer**:
- Docs: https://buildozer.readthedocs.io/

**Problemas específicos**:
- GitHub: anthropics/claude-code/issues

---

## 📜 Licença

BioquímicaEDU — UNICID PIBIC/CNPq
Aluno: Alexandro de Araujo Junior
Orientador: Francisco de Assis Cavallaro

