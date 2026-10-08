# Tutor com IA (Gemini): como ligar

O tutor funciona sem nada disso: responde pela base do próprio app,
offline. Com o Gemini ligado, ele fica mais inteligente:

- explica com as próprias palavras, em vez de mostrar a ficha do marcador;
- responde perguntas gerais e comparações ("ALT ou AST: qual a diferença?");
- lembra as últimas mensagens, então dá para perguntar "e quando está baixo?";
- continua preso ao conteúdo conferido do app: recebe os 22 marcadores
  junto de cada pergunta, com a regra de não contradizê-los, não
  diagnosticar pacientes reais e ignorar pedidos para mudar essas regras.

Se o Gemini falhar (sem internet, limite gratuito atingido, pergunta
bloqueada), o app avisa o motivo e responde pela base. O estudante nunca
fica sem resposta.

> **Versão gratuita, para demonstração.** Na camada gratuita da API, o
> Google pode usar as perguntas para melhorar os produtos dele, inclusive
> com revisão humana. Por isso o tutor mostra um aviso para não digitar
> dados pessoais nem de pacientes. Os termos da API exigem 18 anos ou
> mais. Para um produto de verdade, use a camada paga, em que os dados não
> são usados para treinamento.

## Regra de segurança: a chave nunca fica no app

A chave do Gemini dá acesso à sua conta do Google. Ela **não** vai no
código, **não** vai para o GitHub e **não** vai no APK:

| Onde | De onde vem a chave |
|------|---------------------|
| Computador | arquivo `.env` na pasta do projeto, que o `.gitignore` já bloqueia |
| Celular | o app não tem chave: fala com um servidor intermediário seu, que guarda a chave como segredo |

Ninguém além de você deve digitar a chave. Não a cole em conversas, prints
ou e-mails.

## Parte 1 — Criar a chave (5 minutos)

1. Acesse https://aistudio.google.com/apikey e entre com sua conta Google.
2. Clique em **Create API key** (Criar chave de API) e aceite os termos.
3. Copie a chave. Ela começa com `AIza`.

## Parte 2 — Usar no computador

1. Na pasta do projeto (onde fica o `main.py`), crie um arquivo chamado
   exatamente `.env` (com o ponto, sem extensão) com uma linha:
   ```
   GEMINI_API_KEY=cole_sua_chave_aqui
   ```
2. Confira que o Git ignora o arquivo. O comando abaixo não pode listar `.env`:
   ```bash
   git status --short
   ```
3. Abra o app:
   ```bash
   python main.py
   ```
   O topo do Tutor deve mostrar **Com IA · Gemini**.

Para trocar o modelo, acrescente ao `.env` uma linha
`GEMINI_MODELO=nome-do-modelo` (o padrão é `gemini-3.8-flash`).

## Parte 3 — Usar no celular (opcional)

O celular precisa do servidor intermediário: um Cloudflare Worker, cujo
plano gratuito aguenta 100 mil pedidos por dia, bem mais do que uma
apresentação precisa.

1. Crie uma conta gratuita em https://dash.cloudflare.com.
2. Vá em **Workers & Pages › Create › Create Worker**, dê um nome
   (por exemplo `bioquimicaedu-tutor`) e clique em **Deploy**.
3. Clique em **Edit code**, apague o exemplo, cole todo o conteúdo de
   [`servidor/tutor_worker.js`](../servidor/tutor_worker.js) e clique em **Deploy**.
4. Em **Settings › Variables and Secrets › Add**, escolha o tipo
   **Secret**, nome `GEMINI_API_KEY`, e cole a chave.
5. Opcional: adicione outro segredo, `TOKEN_APP`, com uma senha qualquer
   inventada por você. Ela afasta o uso casual do endereço, mas não é uma
   proteção forte, porque também vai dentro do APK.
6. Copie o endereço do Worker (`https://bioquimicaedu-tutor.SEU-USUARIO.workers.dev`)
   e crie o arquivo `config/tutor_nuvem.json` no projeto:
   ```json
   {
     "servidor": "https://bioquimicaedu-tutor.SEU-USUARIO.workers.dev",
     "token_app": "a mesma senha do passo 5, ou apague esta linha"
   }
   ```
   Esse arquivo não tem nada secreto: só o endereço.
7. No `buildozer.spec`, troque `android.permissions =` por
   `android.permissions = INTERNET` e gere o APK de novo.

O servidor aceita só `https`, limita o tamanho das perguntas e usa as
mesmas regras do tutor do computador (um teste confere que as duas cópias
são iguais).

## Conferir se está tudo certo

```bash
python test_tutor.py
```

O teste simula o Google, sem rede e sem gastar cota: confere o que é
enviado, a leitura das respostas, os avisos de falha, o caminho do celular
e procura chaves esquecidas em arquivos do projeto.

## Se algo der errado

| O tutor mostra | Causa provável |
|----------------|----------------|
| "Responde pela base do app" no topo | o `.env` não foi encontrado ou está com outro nome (no Windows, cuidado com `.env.txt`) |
| "a chave de acesso não foi aceita" | chave copiada pela metade, ou apagada no AI Studio |
| "o limite gratuito de perguntas foi atingido por agora" | a camada gratuita limita perguntas por minuto e por dia; espere um pouco |
| "não foi possível conectar" | sem internet; no celular, falta a permissão `INTERNET` no APK |
| "o serviço respondeu com erro 404" | nome de modelo inválido em `GEMINI_MODELO` |
