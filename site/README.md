# Site do BioquímicaEDU

Página de apresentação e download do app. É um site estático (HTML, CSS e
um pouco de JavaScript), sem dependências externas: fontes e imagens estão
nesta pasta, e nada é carregado de outros servidores. A pasta pode ser
movida inteira para outro repositório.

```
index.html     a página
estilo.css     cores e fonte do app, tema claro e escuro
config.js      versão e links de download: o único arquivo a editar por versão
app.js         preenche os botões e destaca a versão do aparelho de quem visita
imagens/       logo e capturas de tela (WebP)
fontes/        Atkinson Hyperlegible (licença SIL OFL, em fontes/OFL.txt)
firebase.json  configuração do Firebase Hosting
```

## Ver no computador

Na pasta `site/`:

```bash
python -m http.server 8137
```

Depois abra http://localhost:8137.

## Publicar no Firebase Hosting (grátis)

O plano gratuito (Spark) permite 10 GB de armazenamento e 360 MB de
tráfego por dia, o que basta para o site, que tem menos de 1 MB. Os
arquivos de instalação **não** ficam aqui: ficam nas versões (Releases) do
GitHub, sem limite de downloads, e os botões apontam para lá.

1. Instale o Firebase CLI (precisa do Node.js):
   ```bash
   npm install -g firebase-tools
   ```
2. Entre com a sua conta Google. O navegador abre para você autorizar:
   ```bash
   firebase login
   ```
3. Na pasta `site/`, escolha o projeto do Firebase, o mesmo do login do
   app:
   ```bash
   firebase use --add
   ```
4. Publique:
   ```bash
   firebase deploy --only hosting
   ```
   O endereço aparece no fim, no formato `https://SEU-PROJETO.web.app`.

## Quando sair uma versão nova do app

1. Publique os arquivos `BioquimicaEDU-Windows.exe` e
   `BioquimicaEDU-Android.apk` numa versão do GitHub (Releases), com esses
   nomes exatos. Os links usam `releases/latest/download/`, então sempre
   apontam para a versão mais recente.
2. Em `config.js`, atualize `versao`, `dataVersao` e os tamanhos, e mude
   `publicado` para `true` nos botões disponíveis.
3. Se o servidor do tutor com IA já estiver no ar, mude `tutorComIA` para
   `true`.
4. Publique de novo (`firebase deploy --only hosting`).

As capturas de tela são refeitas, no repositório do app, por
`python criar_capturas_site.py`.

## Mover para outro repositório

Copie a pasta inteira. Se o repositório do app mudar de endereço, atualize
os links em `config.js` e no `index.html` (busque por `github.com`).
