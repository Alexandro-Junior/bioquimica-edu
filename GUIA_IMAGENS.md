# 📊 Sistema de Imagens — BioquímicaEDU

## Como funciona

O app agora suporta **5 abas por marcador**:
1. ℹ️ **Info** — Valores e interpretações
2. 🎥 **Vídeos** — Links do YouTube
3. 📋 **Exemplos** — Casos clínicos
4. 📊 **Imagens** — Diagramas e gráficos
5. 💬 **Tutor IA** — Chat (modo Tutor)

## Estrutura

```
data/
├── marcadores_imagens.json    ← Referências às imagens
└── images/                    ← Pasta com imagens
    ├── alt_localizacao.png
    ├── alt_padrao.png
    ├── ast_distribuicao.png
    ├── creatinina_metabolismo.png
    └── ... (mais imagens)
```

## Adicionar imagens

### Passo 1: Criar imagens
Crie ou baixe imagens em **PNG** ou **JPG**:
- Tamanho recomendado: 400×300px
- Qualidade: 72 dpi (web)
- Nomes: `marcador_descricao.png`

Exemplos de imagens úteis:
- **Estruturas químicas** (moléculas)
- **Gráficos de valores normais** (curvas)
- **Anatomia** (localização no corpo)
- **Ciclos metabólicos** (vias bioquímicas)
- **Padrões de laboratório** (tabelas)

### Passo 2: Adicionar ao JSON

Edit `data/marcadores_imagens.json`:

```json
{
  "marcadores_imagens": [
    {
      "sigla": "ALT",
      "imagens": [
        {
          "titulo": "Localização da ALT",
          "descricao": "A ALT está presente principalmente no...",
          "arquivo": "alt_localizacao.png"
        },
        {
          "titulo": "Padrão de elevação",
          "descricao": "Hepatite viral mostra pico...",
          "arquivo": "alt_padrao.png"
        }
      ]
    }
  ]
}
```

### Passo 3: Salvar imagem

Copie a imagem para:
```
data/images/alt_localizacao.png
data/images/alt_padrao.png
```

### Passo 4: Pronto!

Abra o app → Estudo → Clique em marcador → Aba **Imagens**

## Exemplo: Adicionar diagrama de Glicose

1. **Criar imagem**: `glicose_homeostase.png`
2. **Edit** `marcadores_imagens.json`:
```json
{
  "sigla": "Glicose",
  "imagens": [
    {
      "titulo": "Homeostase da glicose",
      "descricao": "Insulina promove captação de glicose...",
      "arquivo": "glicose_homeostase.png"
    }
  ]
}
```
3. **Salvar**: `data/images/glicose_homeostase.png`

## Fontes de imagens

### Gratuitas (Creative Commons)
- **BioRender** (www.biorender.com) — Diagramas biológicos
- **Wikimedia Commons** — Imagens científicas
- **PubMed Central** — Figuras de artigos
- **OpenStax Biology** — Anatomia e fisiologia

### Criadoras localmente
- **Python PIL/Matplotlib** — Gráficos
- **Graphviz** — Diagramas
- **Draw.io** — Flowcharts
- **Inkscape** — Vetores

## Se imagem não aparecer

**Sintomas**:
- Aba mostra: `[Arquivo: alt_localizacao.png]`
- Não aparece na aba Imagens

**Solução**:
1. Verifique se arquivo existe: `data/images/alt_localizacao.png`
2. Verifique nome no JSON (case-sensitive!)
3. Tente outro formato (JPG em vez de PNG)
4. Verifique tamanho (não muito grande)

## Otimizar imagens

Para web (reduzir tamanho):

### ImageMagick (terminal)
```bash
mogrify -resize 400x300 -quality 80 *.png
```

### Python
```python
from PIL import Image
img = Image.open("alt_localizacao.png")
img.thumbnail((400, 300))
img.save("alt_localizacao.png", "PNG", optimize=True)
```

### Online
- **TinyPNG**: tinypng.com
- **Optimizilla**: optimizilla.com

## Marcadores com imagens

Já configurados (adicione arquivos):
- ALT (2 imagens)
- AST (2 imagens)
- Creatinina (2 imagens)
- Glicose (2 imagens)
- Colesterol (2 imagens)
- Potássio (2 imagens)
- Troponina (2 imagens)
- Bilirrubina (2 imagens)

Total: **8 marcadores × 2 imagens = 16 imagens**

## Próximos passos

### v0.3
- [ ] Suporte a PDF (baixar diagrama completo)
- [ ] Galeria de imagens (swipe entre imagens)
- [ ] Zoom touch (pinch-to-zoom)
- [ ] Anotações sobre imagens

### v1.0
- [ ] Banco de imagens online (sincronizar)
- [ ] Upload de imagens pelo app
- [ ] Seção "Minha Galeria"
- [ ] Compartilhamento de imagens

---

## Exemplo pronto

Veja `data/marcadores_imagens.json` para estrutura completa.

Basta adicionar as imagens em `data/images/` e elas aparecerão automaticamente! 🎨
