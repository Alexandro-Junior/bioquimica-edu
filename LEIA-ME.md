# BioquímicaEDU 🧬
**Software Educacional Interativo — Bioquímica Clínica**  
PIBIC/CNPq · Universidade Cidade de São Paulo — UNICID  
Aluno: Alexandro de Araujo Junior | Orientador: Francisco de Assis Cavallaro

---

## 📋 O que é este software?

BioquímicaEDU é um software educacional interativo desenvolvido em Python para ajudar
estudantes da área da saúde a aprenderem os principais **marcadores bioquímicos clínicos**,
sua interpretação e correlação com doenças.

---

## 🚀 Como instalar e executar (Windows)

### Passo 1 — Instalar o Python

1. Acesse: https://www.python.org/downloads/
2. Baixe a versão mais recente (Python 3.10 ou superior)
3. Durante a instalação, **marque a opção**: ✅ "Add Python to PATH"
4. Clique em "Install Now"

### Passo 2 — Verificar instalação

Abra o **Prompt de Comando** (tecla Windows + R, digite `cmd`, Enter) e digite:
```
python --version
```
Deve aparecer algo como: `Python 3.11.x`

### Passo 3 — Instalar dependências

No Prompt de Comando, navegue até a pasta do projeto:
```
cd caminho\para\bioquimica_edu
```

O software usa apenas bibliotecas que já vêm com o Python (tkinter, json, csv).
**Nenhuma instalação adicional é necessária!**

### Passo 4 — Executar o software

```
python main.py
```

Ou simplesmente **dê duplo clique** no arquivo `main.py` (se o Python estiver configurado).

---

## 📁 Estrutura de arquivos

```
bioquimica_edu/
│
├── main.py                     # Arquivo principal (execute este)
│
└── data/
    ├── marcadores.csv          # Base de dados dos marcadores bioquímicos
    ├── casos_clinicos.json     # Casos clínicos para diagnóstico simulado
    └── quiz_perguntas.json     # Banco de questões do quiz
```

---

## 🎮 Funcionalidades

### 📚 Modo Estudo
- Explore todos os **20 marcadores bioquímicos** organizados por categoria
- Veja valores de referência, interpretações clínicas e doenças associadas
- Filtre por categoria (Hepático, Renal, Glicêmico, Lipídico, Eletrólito, Cardíaco)
- Busca por nome ou sigla do marcador

### 🧠 Quiz
- **12 questões** no banco de dados, embaralhadas a cada sessão
- Escolha quantas perguntas quer responder (5, 8, 10 ou 12)
- Feedback imediato com explicação detalhada em cada questão
- Resultado final com percentual de acertos

### 🩺 Diagnóstico Simulado
- **5 casos clínicos** completos com história do paciente
- Exames laboratoriais com indicação visual (ALTO / NORMAL / BAIXO)
- Escolha o diagnóstico entre 4 alternativas
- Explicação detalhada da correlação entre os exames e a doença

---

## 🔬 Marcadores incluídos

| Categoria    | Marcadores |
|-------------|-----------|
| Hepático    | ALT, AST, GGT, Bilirrubina Total |
| Renal       | Creatinina, Ureia, Ácido Úrico |
| Glicêmico   | Glicose em Jejum, HbA1c |
| Lipídico    | Colesterol Total, HDL, LDL, Triglicerídeos |
| Eletrólito  | Sódio (Na⁺), Potássio (K⁺), Cloro (Cl⁻), pH Sanguíneo |
| Cardíaco    | CK-MB, Troponina I, LDH |

---

## 🛠 Como adicionar novos conteúdos

### Novo marcador bioquímico
Abra `data/marcadores.csv` em qualquer editor de texto ou Excel e adicione uma nova linha
seguindo o mesmo padrão das linhas existentes.

### Nova questão de quiz
Abra `data/quiz_perguntas.json` e adicione um novo objeto seguindo o padrão:
```json
{
  "id": 13,
  "categoria": "Nome da Categoria",
  "pergunta": "Texto da pergunta?",
  "alternativas": ["Opção A", "Opção B", "Opção C", "Opção D"],
  "resposta_correta": 0,
  "explicacao": "Explicação detalhada da resposta correta."
}
```
> ⚠️ `resposta_correta` é o ÍNDICE (0=A, 1=B, 2=C, 3=D)

### Novo caso clínico
Abra `data/casos_clinicos.json` e adicione um novo objeto seguindo o padrão dos existentes.

---

## 📊 Tecnologias utilizadas

- **Python 3.x** — Linguagem principal
- **Tkinter** — Interface gráfica (incluso no Python)
- **JSON** — Armazenamento de casos clínicos e quiz
- **CSV** — Base de dados dos marcadores bioquímicos

---

## 📄 Referências

- MORAES, T. R.; FERNANDES, A. C. Integração entre disciplinas básicas da área da saúde. *Rev. Ensino Ciências Saúde*, v.7, n.2, 2019.
- PACHECO, R. D.; OLIVEIRA, M. A. Tecnologias digitais no ensino da bioquímica. *Rev. Educação em Ciências e Matemática*, v.10, n.3, 2021.
- RODRIGUES, C. A. et al. Desafios do ensino de bioquímica na formação em saúde. *Cadernos Educ. Tecnol. Sociedade*, v.11, n.1, 2018.
- SILVA, T. F.; SOARES, J. R.; COSTA, E. R. *Bioquímica clínica: fundamentos e aplicações*. São Paulo: Atheneu, 2020.
