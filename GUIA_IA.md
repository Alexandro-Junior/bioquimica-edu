# BioquímicaEDU Enhanced — Guia IA + Chat Integrado

## 🚀 Como Começar (3 passos)

### 1️⃣ Instalar Ollama

Ollama é um pequeno programa que roda modelos de IA localmente, **100% privado**, **grátis**.

1. Acesse: https://ollama.com
2. Baixe para seu sistema (Windows/Mac/Linux)
3. Instale e abra

### 2️⃣ Baixar Modelo (primeira vez)

Abra terminal/prompt e execute:

```bash
ollama pull mistral
```

Isso baixa o modelo **Mistral 7B** (~4GB, ~3-5 minutos)

**Alternativas (menores/mais rápidos)**:
```bash
ollama pull phi           # 2.6GB - mais rápido
ollama pull neural-chat   # 4.8GB - melhor conversas
```

### 3️⃣ Executar App

Terminal 1 — Inicia Ollama (deixa rodando):
```bash
ollama serve
```

Terminal 2 — Executa BioquímicaEDU:
```bash
cd caminho/para/bioquimica_edu
pip install -r requirements.txt
python main_enhanced.py
```

✅ **Pronto!** App abre com chat e quiz dinâmico funcionando.

---

## 💬 Recursos Novos

### 1. Chat Integrado no Estudo
- Selecione um marcador (ex: ALT)
- Painel de chat aparece à direita
- Faça perguntas: "Por que ALT ↑?", "Diferencie de AST"
- IA responde em tempo real

**Exemplo**:
```
👤 Você: O que causa ALT elevada?

🤖 IA: Alanina aminotransferase (ALT) é uma enzima encontrada principalmente 
no fígado. Quando está elevada pode indicar:
- Hepatite viral
- Cirrose
- Esteatose hepática
- Hepatotoxicidade por medicamentos
...
```

### 2. Quiz Dinâmico (Infinito)
- Não são as 12 perguntas fixas
- **Cada pergunta é gerada pela IA** baseada nos marcadores
- Você pode fazer quantos quizzes quiser
- Perguntas diferentes a cada vez

**Exemplo**:
```
🧠 Pergunta gerada pela IA:
"Um paciente com icterícia apresenta AST=45, ALT=120, Bilirrubina Total=3.2.
Qual é a alteração primária?"

A) Colestase
B) Lesão hepatocelular ← Correto
C) Hemólise
D) Desconjugação
```

### 3. Discussão de Casos (em breve)
- Escolha um diagnóstico
- IA questiona sua lógica
- Feedback socrático

---

## ⚙️ Configuração Avançada

### Trocar Modelo
Edite `ollama_ia.py` linha 37:

```python
ia = OllamaIA(model="phi")  # Troca para Phi (mais rápido)
```

Modelos disponíveis:
- `mistral` (recomendado) — Bom balanço qualidade/velocidade
- `phi` — Muito rápido, respostas mais curtas
- `neural-chat` — Melhor para conversas
- `llama2` — Mais robusto, mais lento

### Aumentar Velocidade
Se ficar lento, adicione GPU:
```bash
# NVIDIA
ollama serve --gpu all

# AMD
ollama serve --gpu radeon
```

### Usar Porta Diferente
Se `11434` está em uso, edite `ollama_ia.py`:

```python
ia = OllamaIA(base_url="http://localhost:12345")
```

E inicie Ollama:
```bash
OLLAMA_HOST=0.0.0.0:12345 ollama serve
```

---

## 🔒 Privacidade

✅ **100% Privado**:
- Tudo roda **localmente** no seu PC/celular
- Nada é enviado para nuvem
- Nenhum dado externo
- Compliant com LGPD/GDPR

---

## ❓ Troubleshooting

### ❌ "Ollama não conectado"

1. Verifique se Ollama está rodando:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   Deve retornar JSON, não erro.

2. Se erro, reinicie Ollama:
   ```bash
   ollama serve
   ```

3. Se ainda não funcionar, verifique porta:
   ```bash
   netstat -an | grep 11434  # Windows
   lsof -i :11434            # Mac/Linux
   ```

### ❌ App muito lento

- Use modelo mais rápido (`phi`)
- Ative GPU se tiver (NVIDIA/AMD)
- Feche outros programas pesados
- Aumente RAM alocada para Ollama

### ❌ Respostas ruins/curtas

- Troque modelo: `neural-chat` é melhor para conversas
- Aumente `temperature` em `ollama_ia.py` (mais criativo, 0-1)

---

## 📊 Performance Esperada

| Métrica | Esperado |
|---------|----------|
| Carregamento app | ~1s |
| Resposta chat | 2-5s (Mistral) / 1-2s (Phi) |
| Gerar pergunta quiz | 3-8s |
| Discussão caso | 4-10s |

**Depende do modelo + CPU/GPU do seu PC**

---

## 🎯 Exemplos de Perguntas

### Sobre um Marcador
```
"O que causa ALT elevada?"
"Diferencie ALT de AST"
"Como ALT relaciona com outros marcadores?"
"Me dê um caso clínico com ALT ↑"
"Qual é o mecanismo de lesão hepática?"
```

### Quiz Dinâmico
```
"Teste-me com 10 perguntas sobre Renal"
"Quiz difícil sobre Lipídico"
"Perguntas tipo ENEM sobre marcadores"
```

### Discussão de Caso
```
"Paciente com Creatinina ↑, qual o diagnóstico?"
"Analise este caso de cirrose"
"Que exames correlacionam com Cardíaco?"
```

---

## 🚀 Próximas Melhorias

- [ ] Salvar chat em arquivo
- [ ] Histórico de perguntas
- [ ] Análise de progresso
- [ ] Modo offline com cache
- [ ] Integrar no mobile (Kivy)
- [ ] Múltiplos modelos simultâneos
- [ ] Temas claro/escuro
- [ ] Seleção de dificuldade (quiz)

---

## 📞 Suporte

**Para erros ou sugestões**:
1. Verifique se Ollama está rodando: `ollama serve`
2. Veja o console do app (erros aparecem lá)
3. Tente com modelo `phi` (mais estável)
4. Se persistir, reporte com:
   - Versão Ollama: `ollama -v`
   - Modelo usado
   - Erro exato

---

## 📜 Licença

BioquímicaEDU + IA  
Universidade Cidade de São Paulo — UNICID — PIBIC/CNPq  
Aluno: Alexandro de Araujo Junior  
Orientador: Francisco de Assis Cavallaro
