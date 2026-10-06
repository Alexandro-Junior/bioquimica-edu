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

Tudo funciona offline. O progresso fica só no aparelho.

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

1. Gere o ícone e a tela de abertura (uma vez):
   ```bash
   python criar_assets_mobile.py
   ```
2. No Ubuntu/WSL, instale e compile:
   ```bash
   pip install --upgrade buildozer cython
   buildozer android debug
   ```
   A primeira compilação baixa o SDK e o NDK do Android e leva de 20 a 40 minutos.
3. Instale no celular (com a depuração USB ativada):
   ```bash
   adb install -r bin/bioquimicaedu-0.3-*-debug.apk
   ```

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
mobile/
  app.py                 navegação, transições e botão voltar
  tema.py                cores, tipografia e ícones
  componentes.py         cartões, botões, barras, anel de progresso...
  dados.py               leitura dos arquivos em data/
  telas/                 início, estudo, cards, prática, revisão, tutor
assets/                  ícone e tela de abertura (criar_assets_mobile.py)
data/                    conteúdo: marcadores, cards, quiz, casos, imagens
```

## Onde fica o progresso

- **No celular:** na pasta privada do app. Atualizar o APK não apaga o que
  o estudante já estudou, e o app não pede permissão de armazenamento.
- **No computador:** em `data/progresso.json`, compartilhado com a versão
  desktop (e fora do Git).

## Problemas comuns

- **"Kivy não encontrado"** — `pip install kivy --upgrade`
- **Buildozer reclama do SDK/API 36** — atualize: `pip install --upgrade buildozer python-for-android`, depois `buildozer android clean`
- **Ícone ou abertura faltando no build** — rode `python criar_assets_mobile.py`

---

BioquímicaEDU — UNICID, PIBIC/CNPq
Aluno: Alexandro de Araujo Junior · Orientador: Francisco de Assis Cavallaro
