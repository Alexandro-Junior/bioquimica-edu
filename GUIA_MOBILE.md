# BioquímicaEDU — Versão Mobile (Android e iOS)

Aplicativo em Python com [Kivy](https://kivy.org), com o mesmo motor de
estudo da versão desktop (repetição espaçada SM-2) e interface própria
para celular.

## O que o app tem

| Aba | O que faz |
|-----|-----------|
| **Início** | O que estudar hoje (revisões vencidas, erros do dia, conteúdo novo), estado da memória, pontos fracos, domínio por sistema, autoavaliação (confiança × acerto), constância e marcos |
| **Estudo** | 20 marcadores com busca e filtro por sistema; cada um tem visão geral, casos clínicos, imagens, fontes acadêmicas e vídeos |
| **Cards** | 52 cards que viram com animação; depois de virar, "Lembrei / Não lembrei" alimenta a revisão |
| **Prática** | Quiz (10 questões sorteadas de 12) e 15 casos clínicos com exames classificados em ALTO / BAIXO / NORMAL |
| **Tutor** | Conversa sobre os marcadores, respondida pela base do app (offline) |
| **Revisão** | Sessão guiada: pergunta → confiança → resposta → autoavaliação em 4 níveis, que reagenda o marcador |
| **Acessibilidade** | (ícone no topo do Início) tamanho do texto até 150%, alto contraste, leitura em voz alta com velocidade, modo foco, sessões curtas, reduzir animações e atalho para o VLibras |

Ao abrir, o app mostra a logo enquanto carrega; no primeiro acesso, uma
apresentação de três passos termina nos ajustes de acessibilidade.

Tudo funciona offline. O progresso e as preferências ficam só no aparelho.
Análise completa das decisões: [docs/ANALISE_EVOLUCAO.md](docs/ANALISE_EVOLUCAO.md).

## Testar no computador

```bash
pip install kivy pillow
python main_kivy_completo.py
```

Abre uma janela com formato de celular (400 × 840).
Teste automático, que abre o app e usa cada tela:

```bash
python test_kivy_completo.py
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

### Como o APK sabe abrir a versão mobile

O Android sempre executa `main.py`. As primeiras linhas do `main.py`
detectam o celular e abrem a versão mobile (pasta `mobile/`) **antes** de
importar o Tkinter, que não existe no Android. No computador, o mesmo
`main.py` continua abrindo a versão desktop.

### Publicação no Google Play

Desde 31/08/2026 o Google Play exige **API 36 (Android 16)** para apps
novos — já configurado no `buildozer.spec`. Para publicar, gere a versão
de release (`buildozer android release`) e assine com sua chave.

## Estrutura

```
main.py                  ponto de entrada (celular → mobile; PC → desktop)
main_kivy_completo.py    abre a versão mobile no computador
progresso.py             motor de repetição espaçada (compartilhado)
assistente.py            tutor com provedores trocáveis (base do app, Ollama)
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
android/extra_manifest.xml   consulta ao serviço de voz e ao VLibras
assets/                  logo, ícones e abertura (criar_logo.py)
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
