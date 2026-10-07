# Login com Google: como configurar

O app já tem todo o fluxo pronto:

```
abertura (logo e nome) → tela de acesso → Entrar com o Google ou Usar sem conta
→ tutorial só se ainda não foi visto → Início
```

Falta ligar o app a um projeto do Firebase criado com a **sua** conta
Google. Isso só você pode fazer, porque exige entrar na sua conta.
Enquanto não estiver pronto, o botão do Google aparece desligado e o "Usar
sem conta" funciona normalmente.

> Não é preciso nada no Google AI Studio: ele serve só para a chave do
> Gemini (tutor com IA, em [TUTOR_GEMINI.md](TUTOR_GEMINI.md)).

## Como o login protege o estudante

- **Nenhuma senha passa pelo app.** No computador, o app abre o navegador
  na página do Google (OAuth 2.0 com PKCE, o método recomendado pelo
  Google para aplicativos instalados). No Android, aparece o seletor de
  contas do próprio sistema.
- O app recebe só **nome e e-mail**.
- A sessão fica **cifrada**: no Windows, com a proteção de dados do
  próprio Windows (só a sua conta do Windows consegue abrir); no Android,
  numa pasta do app que fica fora do backup. Sair da conta apaga a sessão.
- Na nuvem (Cloud Firestore), cada estudante lê e grava **só o próprio
  documento**, e só os campos que o app usa. As regras estão em
  [`firebase/firestore.rules`](../firebase/firestore.rules).
- **Sem conta**, nada sai do aparelho. Entrar ou sair de uma conta **não
  apaga o progresso**, que continua no aparelho.

## Parte 1 — Projeto no Firebase (uns 5 minutos)

1. Acesse https://console.firebase.google.com e clique em **Adicionar
   projeto** (ou **Criar um projeto**). Nome: `BioquimicaEDU`. O Google
   Analytics pode ficar desativado.
2. **Login com Google:** no menu, **Authentication › Vamos começar ›
   Método de login › Google**:
   - clique em **Ativar** e escolha o e-mail de suporte;
   - antes de salvar, abra **Configuração do SDK da Web** e copie o **ID do
     cliente da Web**: é o `webClientId`;
   - clique em **Salvar**.
3. **Banco de dados:** em **Firestore Database › Criar banco de dados**:
   - escolha **modo de produção**;
   - escolha o local `southamerica-east1 (São Paulo)`;
   - na aba **Regras**, apague o conteúdo e cole o de
     `firebase/firestore.rules`;
   - clique em **Publicar**.
4. **Dados do projeto:** na engrenagem, em **Configurações do projeto ›
   Geral**, copie:
   - o **ID do projeto**, que é o `projectId`;
   - a **Chave de API da Web**, que é a `apiKey`.

## Parte 2 — Credencial do app de computador (Google Cloud, uns 5 minutos)

1. Acesse https://console.cloud.google.com e, no topo, selecione o projeto
   **BioquimicaEDU**. É o mesmo do Firebase.
2. Em **Google Auth Platform** (em algumas contas aparece como **APIs e
   serviços › Tela de permissão OAuth**):
   - **Branding:** nome do app `BioquímicaEDU`, o seu e-mail de suporte e
     o de contato;
   - **Público:** tipo **Externo**. Depois clique em **Publicar app**,
     para o status ficar **Em produção**. Se ficar em teste, só os e-mails
     cadastrados como testadores conseguem entrar, e a sessão vence em 7
     dias. Como o app pede só nome e e-mail, o Google não exige
     verificação.
3. Em **Clientes** (ou **Credenciais › Criar credenciais › ID do cliente
   OAuth**):
   - tipo **App para computador** (Desktop app), nome
     `BioquímicaEDU computador`;
   - clique em **Criar** e copie o **ID do cliente** (`desktopClientId`) e
     a **Chave secreta do cliente** (`desktopClientSecret`).
4. Recomendado: em **APIs e serviços › Credenciais**:
   - abra a chave criada pelo Firebase (*Browser key*);
   - em **Restrições de API**, deixe só: Identity Toolkit API, Token
     Service API e Cloud Firestore API.

## Parte 3 — Colocar no app

1. Copie `config/firebase.exemplo.json` para `config/firebase.json`, na
   mesma pasta. Esse arquivo fica fora do Git.
2. Preencha os cinco valores copiados nas partes 1 e 2.
3. Abra o app:
   ```bash
   python main.py
   ```
4. Clique em **Entrar com o Google**. O navegador abre: escolha a conta.
   Quando aparecer "Pronto!", volte ao app.

Não me envie os valores nem cole a chave secreta no chat. Basta avisar que
o arquivo está pronto, que eu testo o fluxo. Quem escolhe a conta e digita
a senha é você, no navegador.

## Parte 4 — Android (quando formos gerar o APK)

O seletor de contas do Android só aceita apps registrados com o nome do
pacote e a impressão digital (SHA-1) do certificado que assina o APK:

1. Em **Configurações do projeto › Seus apps › Adicionar app › Android**:
   - nome do pacote `br.unicid.bioquimicaedu`;
   - a impressão digital SHA-1 que eu vou te passar quando criarmos a chave
     de assinatura do APK.
2. Não precisa baixar o `google-services.json`: o app usa o `webClientId`
   do `config/firebase.json`.

Guarde a chave de assinatura do APK com cuidado. Se ela se perder, é
preciso registrar uma nova impressão digital, e quem já instalou terá de
reinstalar o app.

## Se algo der errado

| Mensagem | O que fazer |
|----------|-------------|
| "O login com Google ainda não foi configurado nesta versão do app" | Falta o `config/firebase.json` (parte 3) ou algum valor está vazio. |
| "O login com Google ainda não foi ativado no Firebase" | Parte 1, passo 2. |
| O navegador mostra "Erro 400: redirect_uri_mismatch" | O cliente da parte 2 não é do tipo **App para computador**. |
| O navegador diz que o app está em teste ou não verificado | Parte 2, passo 2: publique o app (Em produção). |
| "O Google não confirmou a conta" | Em **Authentication › Google › Lista de permissões de IDs de clientes de projetos externos**, adicione o `desktopClientId`. |
| "Não foi possível ler os dados da conta" | O Firestore não foi criado ou as regras não foram publicadas (parte 1, passo 3). |

## Para conferir sem conta de verdade

```bash
python test_login.py
```

O teste simula o Google e o Firebase. Ele confere o PKCE, o estado e o
nonce do login pelo navegador (com um retorno real para 127.0.0.1), a
sessão cifrada, as regras de "tutorial visto" entre aparelhos, o envio
pendente sem internet e que sair da conta não apaga o progresso.
