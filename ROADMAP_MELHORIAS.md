# BioquímicaEDU — Roadmap de Melhorias

## ✅ O QUE FOI IMPLEMENTADO (VERSÃO ENHANCED)

### 1. **Chat Integrado (Ollama Local)**
- ✅ Painel de chat lado a lado com marcador
- ✅ Perguntas sobre qualquer marcador
- ✅ IA responde em tempo real
- ✅ 100% privado (rodando localmente)
- ✅ Suporta múltiplos modelos (Mistral, Phi, Neural-Chat)

### 2. **Quiz Dinâmico (Gerado por IA)**
- ✅ Perguntas infinitas geradas pela IA
- ✅ Cada quiz é diferente
- ✅ Baseado em marcadores reais
- ✅ Feedback explicativo
- ✅ Progresso por sessão

### 3. **Discussão de Casos (Socrática)**
- 🔄 Em desenvolvimento
- Feedback personalizado da IA
- Análise de diagnóstico
- Questionamento educacional

---

## 📋 PRÓXIMAS FASES (Roadmap)

### FASE 2 — Gamificação & Progresso (1-2 semanas)
```
[ ] Salvar histórico de quizzes
[ ] Análise de desempenho por categoria
[ ] Badges/achievements educacionais
[ ] Tracking de XP persistente
[ ] Dashboard de progresso
```

### FASE 3 — Offline & Cache (1-2 semanas)
```
[ ] Cache de respostas frequentes
[ ] Modo offline com fallback
[ ] Sincronização quando online
[ ] Database local (SQLite)
[ ] Export de relatórios (PDF)
```

### FASE 4 — Integração Mobile (2-3 semanas)
```
[ ] Versão mobile (main_mobile.py) com chat
[ ] Compilação APK com Ollama integrado
[ ] Compilação iOS
[ ] Push notifications (estude hoje!)
[ ] Sincronização desktop ↔ mobile
```

### FASE 5 — IA Avançada (2-4 semanas)
```
[ ] Detecção automática de dificuldade
[ ] Questionário adaptativo
[ ] Agrupamento de conceitos relacionados
[ ] Simulação de prova (ENEM-style)
[ ] Correção automática de erros conceituais
```

### FASE 6 — Social & Colaborativo (3-4 semanas)
```
[ ] Compartilhamento de quiz com colegas
[ ] Discussões em grupo (moderado por IA)
[ ] Ranking de desempenho
[ ] Estude em grupo online
[ ] Perguntas frequentes da comunidade
```

### FASE 7 — Analytics & Insights (2-3 semanas)
```
[ ] Gráficos de evolução
[ ] Pontos fracos detectados
[ ] Sugestões de estudo personalizadas
[ ] Comparação com padrão nacional
[ ] Relatórios para professores
```

---

## 🎯 PRIORIDADES CURTAS

### Semana 1
- [ ] Discussão de casos funcional
- [ ] Salvar chat em arquivo
- [ ] Modo dark (tema escuro)
- [ ] Melhorar UX do chat

### Semana 2-3
- [ ] Histórico persistente de quiz
- [ ] Dashboard básico de progresso
- [ ] Integração mobile simples

### Semana 4+
- [ ] IA mais inteligente (prompt engineering)
- [ ] Suporte a múltiplos idiomas
- [ ] Offline mode

---

## 🔧 Técnico — O Que Falta

### Banco de Dados
```python
# Salvar progresso, histórico, etc
Database: SQLite3
Estrutura:
  - usuarios (id, nome)
  - quiz_historico (user_id, pergunta, resposta, correto, data)
  - chat_historico (user_id, marcador, pergunta, resposta, data)
  - badges (user_id, tipo, data_conquistada)
```

### Autenticação (Opcional)
```python
# Se for usar na universidade
- Login local (usuário + senha)
- LDAP com servidor UNICID
- Sincronização com SGA (sistema acadêmico)
```

### Analytics
```python
# Tracking de uso
- Tempo gasto por marcador
- Taxa de acerto por categoria
- Tópicos problemáticos
- Sugestões de foco
```

---

## 💡 Ideias Extras (Futuro)

- 🎮 Modo gamificado (RPG style)
- 📊 Análise preditiva (IA prevê o que você vai errar)
- 🎤 Modo voz (fale a pergunta, IA responde)
- 🌍 Integração com recursos externos (PubMed, UpToDate)
- 🧪 Simulador de exames de sangue interativo
- 🏥 Casos clínicos reais anonymizados
- 📱 App Apple Watch (progresso)
- 🤖 Tutoria síncrona (IA acompanha em tempo real)

---

## 📊 Estimativa de Esforço

| Feature | Horas | Complexidade |
|---------|-------|-------------|
| Discussão de casos | 2-3h | Média |
| Salvar/carregar histórico | 1-2h | Baixa |
| Dashboard progresso | 3-4h | Média |
| Mobile com IA | 6-8h | Alta |
| Offline mode | 4-5h | Alta |
| Analytics | 5-6h | Alta |
| Gamificação | 4-5h | Média |
| Multi-idioma | 2-3h | Baixa |

**Total para MVP completo**: ~30-40 horas

---

## 🚀 Como Contribuir

Se quiser implementar melhorias:

1. **Fork** o repositório
2. **Branch**: `git checkout -b feature/nova-funcao`
3. **Implementar** e testar
4. **Pull request** com descrição

### Guidelines
- Manter paleta de cores (bioquímica)
- Adicionar testes unitários
- Documentar no README
- Manter 100% privado (sem envios externos)

---

## 📅 Timeline Sugerido

```
Semana 1-2:    Discussão de casos + Histórico
Semana 3:      Dashboard progresso
Semana 4-5:    Mobile integrado
Semana 6-8:    Offline + Analytics
Semana 9+:     Gamificação + Social
```

---

## ✨ Visão Final

BioquímicaEDU evolui de um software educacional simples para uma **plataforma completa de aprendizagem adaptativa** com IA, suportando:

- 📚 20+ marcadores bioquímicos
- 🤖 IA local conversacional (100% privado)
- 📊 Analytics de progresso
- 📱 Desktop + Mobile
- 🌍 Possível integração institucional

Tudo **gratuito, open-source, e respeitando LGPD**.

---

**Status**: Em desenvolvimento ativo
**Versão atual**: 0.2.0 (Enhanced com IA)
**Próxima**: 0.3.0 (Casos + Histórico)
