# BioquímicaEDU — App para celular, tablet e computador

Aplicativo em Python com [Kivy](https://kivy.org), com o motor de estudo
por repetição espaçada (SM-2). É **um app só**, que se adapta à largura da
tela:

| Largura | Exemplo | Navegação | Conteúdo |
|---------|---------|-----------|----------|
| até 600 dp | celular | barra embaixo | uma coluna |
| 600 a 840 dp | tablet em pé | menu lateral | uma coluna; Estudo em 2 colunas |
| a partir de 840 dp | tablet deitado, computador | menu lateral | Início em 2 colunas; Estudo em 2 ou 3 |

As faixas seguem as classes de tamanho de janela do Material Design 3.
Textos longos (revisão, tutor, cards) ficam numa coluna central com
largura de leitura confortável, em vez de esticar até a borda.

## O que o app tem

| Aba | O que faz |
|-----|-----------|
| **Início** | O que estudar hoje (revisões vencidas, erros do dia, conteúdo novo), estado da memória, pontos fracos, domínio por sistema, autoavaliação (confiança × acerto), constância e marcos |
| **Estudo** | 20 marcadores com busca e filtro por sistema; cada um tem visão geral, casos clínicos, imagens, fontes acadêmicas e vídeos |
| **Cards** | 52 cards que viram com animação; depois de virar, "Lembrei / Não lembrei" alimenta a revisão |
| **Prática** | Quiz (10 questões sorteadas de 12), 15 casos clínicos com exames classificados em ALTO / BAIXO / NORMAL e dois jogos: "Alto, normal ou baixo?" (10 resultados de exame, com régua da faixa de referência, pontos, relógio opcional e recorde pessoal) e jogo da memória (marcador e sistema) |
| **Tutor** | Conversa sobre os marcadores. Offline, responde pela base do app; com o Gemini ligado ([docs/TUTOR_GEMINI.md](docs/TUTOR_GEMINI.md)), explica, compara e lembra a conversa |
| **Revisão** | Sessão guiada: pergunta → confiança → resposta → autoavaliação em 4 níveis; cada botão mostra quando o marcador volta (Difícil, Bom e Fácil levam a intervalos diferentes) |
| **Acessibilidade** | (ícone no topo do Início) tamanho do texto até 150%, alto contraste, fonte para leitura facilitada (Atkinson Hyperlegible), leitura em voz alta com velocidade, modo foco, sessões curtas, reduzir animações e atalho para o VLibras |

Ao abrir, o app mostra a logo e o nome enquanto carrega. Depois:

1. **Tela de acesso**, se o estudante ainda não escolheu: **Entrar com o
   Google** ou **Usar sem conta**. A escolha fica salva.
2. **Apresentação** de quatro passos, com "Pular", só se ainda não foi
   vista. Com conta Google, o registro de que já foi vista vale em
   qualquer aparelho.
3. **Início**. O ícone de pessoa no topo abre a tela **Conta**, para
   entrar, sair ou rever a apresentação.

O login é opcional e configurado em [docs/LOGIN_GOOGLE.md](docs/LOGIN_GOOGLE.md).
O estudo funciona offline; a internet só é usada pelo login e pelo tutor
com IA. O progresso de estudo fica no aparelho e não é apagado ao entrar
ou sair de uma conta.
Análise completa das decisões: [docs/ANALISE_EVOLUCAO.md](docs/ANALISE_EVOLUCAO.md).

## Usar no computador

```bash
pip install kivy pillow
python main.py
```

Abre o app numa janela de computador, com menu lateral. Ao estreitar a
janela, ele passa para o formato de celular sem perder a tela em que você
está. Outras formas de abrir:

```bash
python main.py --celular
```

```bash
python main.py --classico
```

A primeira abre direto no formato de celular (400 × 840); a segunda abre
a versão clássica em Tkinter, mantida para quem já a usava.

A leitura em voz alta no Windows usa a voz do sistema (SAPI); se o
`pywin32` não estiver instalado, o app usa o PowerShell, sem instalar nada.

Testes automáticos (abrem o app e usam cada tela, em formato de computador
e de celular, numa pasta temporária, sem tocar no seu progresso):

```bash
python test_kivy_completo.py
```

```bash
python test_tutor.py
```

```bash
python test_login.py
```

## Gerar o APK (Android)

O Buildozer só roda em **Linux** — no Windows, use o
[WSL](https://learn.microsoft.com/windows/wsl/install) (Ubuntu).

1. Gere ícone, ícone adaptativo e tela de abertura (uma vez):
   ```bash
   python criar_logo.py
   ```
2. No Ubuntu/WSL, instale e compile:
   ```bash
   pip install --upgrade buildozer cython
   buildozer android debug
   ```
   A primeira compilação baixa o SDK e o NDK do Android e leva de 20 a 40 minutos.
3. Instale no celular (com a depuração USB ativada):
   ```bash
   adb install -r bin/bioquimicaedu-0.4-*-debug.apk
   ```
4. No aparelho, confira o que o computador não consegue testar: a leitura em
   voz alta (Acessibilidade › Leitura em voz alta › Testar a voz), o atalho
   para o VLibras e o ícone na tela inicial.

### Tablet

O mesmo APK serve para tablet: com 600 dp ou mais de largura, o app troca
a barra de baixo pelo menu lateral e usa mais colunas. O `buildozer.spec`
pede orientação retrato, mas a partir do Android 16 o sistema ignora essa
restrição em telas grandes, então o app também foi preparado para o
tablet deitado.

### Como o APK sabe abrir o app

O Android sempre executa `main.py`. As primeiras linhas do `main.py` abrem
o app (pasta `mobile/`) **antes** de importar o Tkinter, que não existe no
Android. O Tkinter só é carregado com `--classico`, no computador.

### Publicação no Google Play

Desde 31/08/2026 o Google Play exige **API 36 (Android 16)** para apps
novos — já configurado no `buildozer.spec`. Para publicar, gere a versão
de release (`buildozer android release`) e assine com sua chave.

## Estrutura

```
main.py                  ponto de entrada (app; --celular; --classico)
main_kivy_completo.py    abre o app (atalho antigo, ainda funciona)
progresso.py             motor de repetição espaçada (compartilhado)
assistente.py            tutor com provedores trocáveis (Gemini, Ollama, base do app)
servidor/tutor_worker.js servidor intermediário do Gemini para o celular
mobile/
  app.py                 abertura, navegação, ajustes, voz e Libras
  tema.py                paletas acessíveis, escala de texto, movimento
  icones.py              ícones vetoriais (grade 24 × 24)
  componentes.py         cartões, botões, avisos, chaves, barras...
  preferencias.py        ajustes do estudante, validados
  voz.py                 leitura em voz alta com a voz do sistema
  dados.py               leitura dos arquivos em data/
  telas/                 abertura, apresentação, início, estudo, cards,
                         prática, revisão, tutor, acessibilidade
android/extra_manifest.xml   consulta ao serviço de voz e ao navegador
assets/                  logo, ícones e abertura (criar_logo.py)
assets/fontes/           Atkinson Hyperlegible (licença OFL, em OFL.txt)
data/                    conteúdo: marcadores, cards, quiz, casos, imagens
docs/                    análise das decisões e identidade visual
```

## Onde fica o progresso

- **No celular:** na pasta privada do app. Atualizar o APK não apaga o que
  o estudante já estudou, e o app não pede permissão de armazenamento.
- **No computador:** em `data/progresso.json`, compartilhado com a versão
  desktop, e as preferências em `data/preferencias_mobile.json` (ambos fora
  do Git). Os testes usam uma pasta temporária e nunca tocam nesses arquivos.

## Problemas comuns

- **"Kivy não encontrado"** — `pip install kivy --upgrade`
- **Buildozer reclama do SDK/API 36** — atualize: `pip install --upgrade buildozer python-for-android`, depois `buildozer android clean`
- **Ícone ou abertura faltando no build** — rode `python criar_logo.py`
- **"Leitura em voz alta" desabilitada** — o aparelho não tem voz instalada:
  Configurações › Acessibilidade › Saída de texto para voz

---

BioquímicaEDU — UNICID, PIBIC/CNPq
Aluno: Alexandro de Araujo Junior · Orientador: Francisco de Assis Cavallaro
