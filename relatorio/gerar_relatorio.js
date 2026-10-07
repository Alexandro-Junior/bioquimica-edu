/*
 * Gera o relatório final PIBIC do BioquímicaEDU em .docx, nas normas ABNT
 * (NBR 10719 para a estrutura do relatório; NBR 14724 para a apresentação
 * gráfica; NBR 6023 para as referências; NBR 10520:2023 para as citações;
 * NBR 6024 e 6027 para numeração das seções e sumário; NBR 6028 para o resumo).
 *
 * Os números do software (conteúdo e linhas de código) vêm de
 * figuras/metricas.json, gerado por gerar_figuras.py — rode aquele antes.
 *
 * Trechos que dependem de dados que só o autor tem aparecem como
 * [PREENCHER: ...] ou [CONFIRMAR: ...], com realce amarelo.
 *
 * Uso:   npm install docx@9     (uma vez)
 *        node relatorio/gerar_relatorio.js
 * Saída: relatorio/Relatorio_Final_PIBIC_BioquimicaEDU.docx
 *
 * Depois de gerar, abra no Word e atualize os campos (Ctrl+A, F9) para
 * preencher sumário e listas — ou rode atualizar_campos.ps1.
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Header, AlignmentType, PageNumber,
  TableOfContents, HeadingLevel, Table, TableRow, TableCell, WidthType, BorderStyle,
  SequentialIdentifier, LevelFormat, TabStopType, VerticalAlignTable, VerticalAlignSection,
  SectionType,
} = require("docx");

const AQUI = __dirname;
const RAIZ = path.resolve(AQUI, "..");
const FIG = path.join(AQUI, "figuras");
const SAIDA = path.join(AQUI, "Relatorio_Final_PIBIC_BioquimicaEDU.docx");

const M = JSON.parse(fs.readFileSync(path.join(FIG, "metricas.json"), "utf8"));
const C = M.conteudo;
const fmt = (n) => n.toLocaleString("pt-BR");

// ════════════════════════════════════════════════════════════════════
// DADOS DO TRABALHO
// ════════════════════════════════════════════════════════════════════
const INSTITUICAO = "UNIVERSIDADE CIDADE DE SÃO PAULO";
const CURSO = "CURSO DE CIÊNCIA DA COMPUTAÇÃO";
const AUTOR = "ALEXANDRO DE ARAUJO JUNIOR";
const ORIENTADOR = "Prof. Francisco de Assis Cavallaro";
// título registrado do projeto PIBIC; o software se chama BioquímicaEDU
const TITULO = "DESENVOLVIMENTO DE SOFTWARE EDUCACIONAL PARA O ENSINO INTERATIVO DE BIOQUÍMICA CLÍNICA";
const SUBTITULO = "marcadores bioquímicos e sua correlação com doenças";
const LOCAL = "SÃO PAULO";
const ANO = "2026";
const ACESSO = "Acesso em: 6 out. 2026.";
const ACESSO_7 = "Acesso em: 7 out. 2026.";
const REPOSITORIO = "https://github.com/Alexandro-Junior/bioquimica-edu";

// ════════════════════════════════════════════════════════════════════
// MEDIDAS (DXA: 1 cm = 567)
// ════════════════════════════════════════════════════════════════════
const CM = 567;
const PAGINA = { largura: 11906, altura: 16838 };
const MARGEM = { topo: 3 * CM, esquerda: 3 * CM, base: 2 * CM, direita: 2 * CM };
const LARGURA_TEXTO = PAGINA.largura - MARGEM.esquerda - MARGEM.direita;  // 9072
const RECUO = Math.round(1.25 * CM);
const LINHA_15 = 360;
const LINHA_1 = 240;
const PX_POR_CM = 96 / 2.54;

// ════════════════════════════════════════════════════════════════════
// TEXTO COM MARCAÇÃO SIMPLES
//   **negrito**   ~itálico~   [[PREENCHER: ...]] realçado em amarelo
// ════════════════════════════════════════════════════════════════════
function runs(texto, base = {}) {
  const partes = texto.split(/(\*\*[^*]+\*\*|~[^~]+~|\[\[[^\]]+\]\])/g).filter(Boolean);
  return partes.map((p) => {
    if (p.startsWith("**")) return new TextRun({ ...base, text: p.slice(2, -2), bold: true });
    if (p.startsWith("~")) return new TextRun({ ...base, text: p.slice(1, -1), italics: true });
    if (p.startsWith("[[")) return new TextRun({ ...base, text: "[" + p.slice(2, -2) + "]", highlight: "yellow" });
    return new TextRun({ ...base, text: p });
  });
}

// parágrafo de texto: justificado, recuo de 1,25 cm, entrelinha 1,5
function p(texto, opc = {}) {
  return new Paragraph({
    alignment: opc.alinhamento ?? AlignmentType.JUSTIFIED,
    indent: opc.semRecuo ? undefined : { firstLine: RECUO },
    spacing: { line: opc.linha ?? LINHA_15, before: opc.antes ?? 0, after: opc.depois ?? 0 },
    keepNext: opc.manterComProximo,
    children: runs(texto, opc.run),
  });
}

const h1 = (t, opc = {}) => new Paragraph({
  heading: HeadingLevel.HEADING_1, alignment: opc.centro ? AlignmentType.CENTER : AlignmentType.LEFT,
  children: [new TextRun(t)],
});
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const h3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });

// título sem indicativo numérico dos elementos pré-textuais (fora do sumário)
const tituloPre = (t) => new Paragraph({ style: "TituloPre", children: [new TextRun(t)] });

// alíneas a), b), c)... cada lista recomeça em "a"
let instanciaLista = 0;
function alineas(itens) {
  instanciaLista += 1;
  const inst = instanciaLista;
  return itens.map((t) => new Paragraph({
    numbering: { reference: "alineas", level: 0, instance: inst },
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: LINHA_15 },
    children: runs(t),
  }));
}

// equação centralizada, numerada à direita
function equacao(texto, numero) {
  return new Paragraph({
    tabStops: [
      { type: TabStopType.CENTER, position: Math.round(LARGURA_TEXTO / 2) },
      { type: TabStopType.RIGHT, position: LARGURA_TEXTO },
    ],
    spacing: { line: LINHA_15, before: 120, after: 120 },
    children: [new TextRun("\t"), ...runs(texto), new TextRun(`\t(${numero})`)],
  });
}

// ════════════════════════════════════════════════════════════════════
// ILUSTRAÇÕES E TABELAS (legenda em cima, fonte embaixo)
// ════════════════════════════════════════════════════════════════════
function legenda(tipo, titulo) {
  return new Paragraph({
    style: "Legenda",
    keepNext: true,
    children: [new TextRun(`${tipo} `), new SequentialIdentifier(tipo), ...runs(` – ${titulo}`)],
  });
}
const fonte = (t, comNota = false) => new Paragraph({
  style: "FonteIlustracao", keepNext: comNota,
  spacing: comNota ? { after: 0 } : undefined,
  children: runs(`Fonte: ${t}`),
});
const nota = (t) => new Paragraph({ style: "FonteIlustracao", children: runs(`Nota: ${t}`) });

// Ordem das figuras no texto: as remissões ("Figura 3") saem daqui, e não
// de números digitados à mão que ficariam errados ao mover uma figura.
// A conversa real com o Gemini só existe depois que a chave é configurada
// (docs/TUTOR_GEMINI.md); até lá, o texto traz um [PREENCHER] no lugar dela.
const TEM_FIGURA_TUTOR = fs.existsSync(path.join(FIG, "evolucao_tutor.png"));
const ORDEM_FIGURAS = ["arquitetura", "sm2", "telas_inicio", "telas_revisao", "telas_pratica",
                       "desktop", "logo", "evolucao_formatos", "evolucao_acessibilidade",
                       "tutor_arquitetura", ...(TEM_FIGURA_TUTOR ? ["evolucao_tutor"] : [])];
const fig = (chave) => {
  const n = ORDEM_FIGURAS.indexOf(chave) + 1;
  if (!n) throw new Error(`figura desconhecida: ${chave}`);
  return n;
};

function tamanhoPng(arquivo) {
  const b = fs.readFileSync(arquivo);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), dados: b };
}

const figurasCriadas = [];
function figura(chave, arquivo, titulo, origem, opc = {}) {
  figurasCriadas.push(chave);
  if (figurasCriadas.length !== fig(chave)) {
    throw new Error(`figura ${chave} fora da ordem declarada em ORDEM_FIGURAS`);
  }
  const { w, h, dados } = tamanhoPng(arquivo);
  const largura = Math.round((opc.larguraCm ?? 16) * PX_POR_CM);
  const texto = titulo.replace(/~/g, "");
  return [
    legenda("Figura", titulo),
    new Paragraph({
      alignment: AlignmentType.CENTER, keepNext: true, spacing: { line: LINHA_1 },
      children: [new ImageRun({
        type: "png", data: dados,
        transformation: { width: largura, height: Math.round(largura * h / w) },
        altText: { title: texto, description: texto, name: path.basename(arquivo) },
      })],
    }),
    fonte(origem, Boolean(opc.nota)),
    ...(opc.nota ? [nota(opc.nota)] : []),
  ];
}

const FINO = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const GROSSO = { style: BorderStyle.SINGLE, size: 8, color: "000000" };
const NADA = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };

function celula(texto, largura, opc = {}) {
  return new TableCell({
    width: { size: largura, type: WidthType.DXA },
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    verticalAlign: VerticalAlignTable.CENTER,
    borders: opc.bordas,
    children: [new Paragraph({
      alignment: opc.alinhamento ?? AlignmentType.LEFT,
      spacing: { line: LINHA_1 },
      keepNext: true,   // mantém quadro, tabela e fonte na mesma página
      children: runs(texto, { size: 20, bold: opc.negrito }),
    })],
  });
}

// Quadro: todas as bordas (dados textuais)
function quadro(titulo, colunas, linhas, origem) {
  const larguras = colunas.map((c) => c.largura);
  const total = larguras.reduce((a, b) => a + b, 0);
  const bordas = { top: FINO, bottom: FINO, left: FINO, right: FINO };
  return [
    legenda("Quadro", titulo),
    new Table({
      width: { size: total, type: WidthType.DXA },
      columnWidths: larguras,
      alignment: AlignmentType.CENTER,
      rows: [
        new TableRow({
          tableHeader: true,
          children: colunas.map((c) => celula(c.titulo, c.largura, { negrito: true, bordas })),
        }),
        ...linhas.map((l) => new TableRow({
          cantSplit: true,
          children: l.map((t, i) => celula(t, larguras[i], { bordas })),
        })),
      ],
    }),
    fonte(origem),
  ];
}

// Tabela (IBGE): só traços horizontais no topo, sob o cabeçalho e na base
function tabela(titulo, colunas, linhas, origem) {
  const larguras = colunas.map((c) => c.largura);
  const total = larguras.reduce((a, b) => a + b, 0);
  const ultima = linhas.length - 1;
  const cab = { top: GROSSO, bottom: FINO, left: NADA, right: NADA };
  return [
    legenda("Tabela", titulo),
    new Table({
      width: { size: total, type: WidthType.DXA },
      columnWidths: larguras,
      alignment: AlignmentType.CENTER,
      rows: [
        new TableRow({
          tableHeader: true,
          children: colunas.map((c) => celula(c.titulo, c.largura, {
            negrito: true, bordas: cab, alinhamento: c.alinhamento,
          })),
        }),
        ...linhas.map((l, i) => new TableRow({
          cantSplit: true,
          children: l.map((t, j) => celula(t, larguras[j], {
            alinhamento: colunas[j].alinhamento,
            negrito: l.negrito,
            bordas: { top: l.negrito ? FINO : NADA, bottom: i === ultima ? GROSSO : NADA, left: NADA, right: NADA },
          })),
        })),
      ],
    }),
    fonte(origem),
  ];
}
function totalLinha(celulas) { celulas.negrito = true; return celulas; }

// ════════════════════════════════════════════════════════════════════
// REFERÊNCIAS
// ════════════════════════════════════════════════════════════════════
const NBK = (n) => `https://www.ncbi.nlm.nih.gov/books/${n}/`;
const statpearls = (autores, titulo, ano, nbk) =>
  `${autores} ${titulo}. In: STATPEARLS. Treasure Island, FL: StatPearls Publishing, ${ano}. Disponível em: ${NBK(nbk)}. ${ACESSO}`;
const clinicalMethods = (titulo, ano, nbk) =>
  `VROON, D. H.; ISRAILI, Z. ${titulo}. In: WALKER, H. K.; HALL, W. D.; HURST, J. W. (ed.). **Clinical methods**: the history, physical, and laboratory examinations. 3. ed. Boston: Butterworths, ${ano}. Disponível em: ${NBK(nbk)}. ${ACESSO}`;

// Citação de cada capítulo usado no Apêndice A, pela chave NBK
const CITACAO_NBK = {
  NBK203: "Vroon e Israili (1990a)", NBK425: "Vroon e Israili (1990b)",
  NBK459188: "Ibrahim e Jialal (2023)", NBK459218: "Leslie e Minter (2023)",
  NBK470202: "Baddam e Tubben (2025)", NBK470284: "Simon e Rout (2025)",
  NBK470290: "Kalakonda, Jenkins e John (2022)", NBK470386: "Rout e Afzal (2026)",
  NBK470561: "Huff, Boyd e Jialal (2023)", NBK482465: "Castro e Sharma (2025)",
  NBK482489: "Jogu, Zubair e Minter (2026)", NBK500010: "Venugopal, Anoruo e Jialal (2023)",
  NBK507805: "Zubair e Sharma (2026)", NBK507821: "Gounden, Bhatt e Jialal (2024)",
  NBK541119: "Melkonian, Asuka e Schury (2023)", NBK541123: "Shrimanker e Bhattarai (2023)",
  NBK544252: "Joseph e Samant (2023)", NBK545201: "Hantzidiamantis, Awosika e Lappin (2024)",
  NBK549816: "Eyth, Zubair e Naik (2025)", NBK557536: "Farhana e Lappin (2023)",
  NBK557591: "Kurapati e Zubair (2026)", NBK559278: "Moriles, Zubair e Azer (2024)",
  NBK560891: "Pappan, Awosika e Rehman (2024)",
};

const REFERENCIAS = [
  `ANDROID DEVELOPERS. **Behavior changes**: apps targeting Android 16 or higher. [S. l.], [2026a]. Disponível em: https://developer.android.com/about/versions/16/behavior-changes-16. ${ACESSO_7}`,
  `ANDROID DEVELOPERS. **Use window size classes**. [S. l.], [2026b]. Disponível em: https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes. ${ACESSO_7}`,
  `ANKI. Deck options. In: ANKI. **Anki manual**. [S. l.], [2026]. Disponível em: https://docs.ankiweb.net/deck-options.html. ${ACESSO_7}`,
  statpearls("BADDAM, S.; TUBBEN, R. E.", "Lactic acidosis", 2025, "NBK470202"),
  "BALCI, S.; SECAUR, J. M.; MORRIS, B. J. Comparing the effectiveness of badges and leaderboards on academic performance and motivation of students in fully versus partially gamified online physics classes. **Education and Information Technologies**, [s. l.], v. 27, n. 6, p. 8669-8704, 2022. DOI: https://doi.org/10.1007/s10639-022-10983-z.",
  `BRAILLE INSTITUTE. **Atkinson Hyperlegible font**. [S. l.], [2026]. Disponível em: https://www.brailleinstitute.org/freefont/. ${ACESSO_7}`,
  `BRASIL. Lei nº 13.146, de 6 de julho de 2015. Institui a Lei Brasileira de Inclusão da Pessoa com Deficiência (Estatuto da Pessoa com Deficiência). Brasília, DF: Presidência da República, 2015. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm. ${ACESSO_7}`,
  `BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Dispõe sobre a proteção de dados pessoais e altera a Lei nº 12.965, de 23 de abril de 2014 (Marco Civil da Internet). Brasília, DF: Presidência da República, 2018. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm. ${ACESSO}`,
  `BRASIL. Ministério da Gestão e da Inovação em Serviços Públicos. **VLibras**. Brasília, DF, [2026]. Disponível em: https://www.gov.br/governodigital/pt-br/acessibilidade-e-usuario/vlibras. ${ACESSO_7}`,
  statpearls("CASTRO, D.; SHARMA, S.", "Hypokalemia", 2025, "NBK482465"),
  "CEPEDA, N. J. et al. Distributed practice in verbal recall tasks: a review and quantitative synthesis. **Psychological Bulletin**, [s. l.], v. 132, n. 3, p. 354-380, maio 2006. DOI: https://doi.org/10.1037/0033-2909.132.3.354.",
  "CLEARY, T. J. et al. First-year medical students' calibration bias and accuracy across clinical reasoning activities. **Advances in Health Sciences Education**: theory and practice, [s. l.], v. 24, n. 4, p. 767-781, out. 2019. DOI: https://doi.org/10.1007/s10459-019-09897-2.",
  `CLOUDFLARE. Limits. In: CLOUDFLARE. **Cloudflare Workers docs**. [S. l.], [2026]. Disponível em: https://developers.cloudflare.com/workers/platform/limits/. ${ACESSO_7}`,
  "DECI, E. L.; KOESTNER, R.; RYAN, R. M. A meta-analytic review of experiments examining the effects of extrinsic rewards on intrinsic motivation. **Psychological Bulletin**, [s. l.], v. 125, n. 6, p. 627-668, nov. 1999. DOI: https://doi.org/10.1037/0033-2909.125.6.627.",
  "DENG, F.; GLUCKSTEIN, J. A.; LARSEN, D. P. Student-directed retrieval practice is a predictor of medical licensing examination performance. **Perspectives on Medical Education**, [s. l.], v. 4, n. 6, p. 308-313, dez. 2015. DOI: https://doi.org/10.1007/s40037-015-0220-x.",
  statpearls("EYTH, E.; ZUBAIR, M.; NAIK, R.", "Hemoglobin A1C", 2025, "NBK549816"),
  statpearls("FARHANA, A.; LAPPIN, S. L.", "Biochemistry, lactate dehydrogenase", 2023, "NBK557536"),
  `GOOGLE. Gemini API additional terms of service. In: GOOGLE. **Google AI for Developers**. [S. l.], [2026a]. Disponível em: https://ai.google.dev/gemini-api/terms. ${ACESSO_7}`,
  `GOOGLE. Models. In: GOOGLE. **Google AI for Developers**. [S. l.], [2026b]. Disponível em: https://ai.google.dev/gemini-api/docs/models. ${ACESSO_7}`,
  `GOOGLE. Target API level requirements for Google Play apps. In: GOOGLE. **Play Console Help**. [S. l.], [2026c]. Disponível em: https://support.google.com/googleplay/android-developer/answer/11926878. ${ACESSO}`,
  statpearls("GOUNDEN, V.; BHATT, H.; JIALAL, I.", "Renal function tests", 2024, "NBK507821"),
  statpearls("HANTZIDIAMANTIS, P. J.; AWOSIKA, A. O.; LAPPIN, S. L.", "Physiology, glucose", 2024, "NBK545201"),
  statpearls("HUFF, T.; BOYD, B.; JIALAL, I.", "Physiology, cholesterol", 2023, "NBK470561"),
  statpearls("IBRAHIM, M. A.; JIALAL, I.", "Hypercholesterolemia", 2023, "NBK459188"),
  statpearls("JOGU, P.; ZUBAIR, M.; MINTER, D. A.", "Liver function tests", 2026, "NBK482489"),
  statpearls("JOSEPH, A.; SAMANT, H.", "Hyperbilirubinemia", 2023, "NBK544252"),
  statpearls("KALAKONDA, A.; JENKINS, B. A.; JOHN, S.", "Physiology, bilirubin", 2022, "NBK470290"),
  "KARACA, M. et al. Low-performing students confidently overpredict their grade performance throughout the semester. **Journal of Intelligence**, [s. l.], v. 11, n. 10, art. 188, set. 2023. DOI: https://doi.org/10.3390/jintelligence11100188.",
  "KAYA, O. S.; ERCAG, E. The impact of applying challenge-based gamification program on students' learning outcomes: academic achievement, motivation and flow. **Education and Information Technologies**, [s. l.], p. 1-26, jan. 2023. DOI: https://doi.org/10.1007/s10639-023-11585-z.",
  `KIVY ORGANIZATION. **Kivy**. Versão 2.3.1. [S. l.], 2024. Disponível em: https://kivy.org. ${ACESSO}`,
  "KRUGER, J.; DUNNING, D. Unskilled and unaware of it: how difficulties in recognizing one's own incompetence lead to inflated self-assessments. **Journal of Personality and Social Psychology**, [s. l.], v. 77, n. 6, p. 1121-1134, dez. 1999. DOI: https://doi.org/10.1037//0022-3514.77.6.1121.",
  statpearls("KURAPATI, R.; ZUBAIR, M.", "Creatine kinase MB: diagnostic utility and limitations", 2026, "NBK557591"),
  statpearls("LESLIE, S. W.; MINTER, D. A.", "Hyperuricemia", 2023, "NBK459218"),
  "MAYE, J. A.; HURLEY, F. The effectiveness of spaced repetition in medical education: a systematic review and meta-analysis. **The Clinical Teacher**, [s. l.], v. 23, n. 2, art. e70353, abr. 2026. DOI: https://doi.org/10.1111/tct.70353.",
  statpearls("MELKONIAN, E. A.; ASUKA, E.; SCHURY, M. P.", "Physiology, gluconeogenesis", 2023, "NBK541119"),
  statpearls("MORILES, K. E.; ZUBAIR, M.; AZER, S. A.", "Alanine aminotransferase (ALT) test", 2024, "NBK559278"),
  `OLLAMA. **Ollama**. [S. l.], [2026]. Disponível em: https://ollama.com. ${ACESSO}`,
  statpearls("PAPPAN, N.; AWOSIKA, A. O.; REHMAN, A.", "Dyslipidemia", 2024, "NBK560891"),
  `PYTHON SOFTWARE FOUNDATION. **Python**. Versão 3.12. [S. l.], 2023. Disponível em: https://www.python.org. ${ACESSO}`,
  "ROEDIGER, H. L.; KARPICKE, J. D. Test-enhanced learning: taking memory tests improves long-term retention. **Psychological Science**, [s. l.], v. 17, n. 3, p. 249-255, mar. 2006. DOI: https://doi.org/10.1111/j.1467-9280.2006.01693.x.",
  statpearls("ROUT, P.; AFZAL, M.", "Hyponatremia", 2026, "NBK470386"),
  "RYAN, R. M.; DECI, E. L. Self-determination theory and the facilitation of intrinsic motivation, social development, and well-being. **American Psychologist**, [s. l.], v. 55, n. 1, p. 68-78, jan. 2000. DOI: https://doi.org/10.1037//0003-066x.55.1.68.",
  "SERRA, M. J. et al. The use of retrieval practice in the health professions: a state-of-the-art review. **Behavioral Sciences**, [s. l.], v. 15, n. 7, art. 974, jul. 2025. DOI: https://doi.org/10.3390/bs15070974.",
  statpearls("SHRIMANKER, I.; BHATTARAI, S.", "Electrolytes", 2023, "NBK541123"),
  statpearls("SIMON, L. V.; ROUT, P.", "Hyperkalemia", 2025, "NBK470284"),
  statpearls("VENUGOPAL, S. K.; ANORUO, M.; JIALAL, I.", "Biochemistry, low density lipoprotein", 2023, "NBK500010"),
  clinicalMethods("Alkaline phosphatase and gamma glutamyltransferase", "1990a", "NBK203"),
  clinicalMethods("Aminotransferases", "1990b", "NBK425"),
  `WORLD WIDE WEB CONSORTIUM. **Web content accessibility guidelines (WCAG) 2.2**. [S. l.]: W3C, 12 dez. 2024. Disponível em: https://www.w3.org/TR/WCAG22/. ${ACESSO_7}`,
  `WOZNIAK, P. A. **Optimization of learning**. 1990. Dissertação (Mestrado) – University of Technology in Poznan, Poznań, 1990. Seção 3.2: Application of a computer to improve the results obtained in working with the SuperMemo method. Disponível em: https://super-memory.com/english/ol/sm2.htm. ${ACESSO}`,
  statpearls("ZUBAIR, M.; SHARMA, S.", "Analytical and clinical aspects of troponin testing", 2026, "NBK507805"),
];

const referencia = (t) => new Paragraph({
  style: "Referencia", children: runs(t),
});

// ════════════════════════════════════════════════════════════════════
// DADOS DO APÊNDICE A (vêm dos arquivos do próprio software)
// ════════════════════════════════════════════════════════════════════
function lerMarcadores() {
  const linhas = fs.readFileSync(path.join(RAIZ, "data", "marcadores.csv"), "utf8")
    .replace(/^﻿/, "").split(/\r?\n/).filter(Boolean);
  const cab = linhas[0].split(",");
  const iCat = cab.indexOf("categoria"), iNome = cab.indexOf("nome"), iSigla = cab.indexOf("sigla");
  return linhas.slice(1).map((l) => {
    const c = l.split(",");
    return { categoria: c[iCat], nome: c[iNome], sigla: c[iSigla] };
  });
}
const MARCADORES = lerMarcadores();
const EXTRAS = JSON.parse(fs.readFileSync(path.join(RAIZ, "data", "marcadores_extras.json"), "utf8"))
  .marcadores_extras;

function fontesDoMarcador(sigla) {
  const extra = EXTRAS.find((e) => e.sigla === sigla) || { referencias: [] };
  const vistos = new Set();
  const cit = [];
  for (const r of extra.referencias) {
    const nbk = r.url.replace(/\/+$/, "").split("/").pop();
    if (!CITACAO_NBK[nbk]) throw new Error(`fonte sem referência no relatório: ${r.url}`);
    if (!vistos.has(nbk)) { vistos.add(nbk); cit.push(CITACAO_NBK[nbk]); }
  }
  return cit.join("; ");
}

// ════════════════════════════════════════════════════════════════════
// ESTILOS
// ════════════════════════════════════════════════════════════════════
const estilos = {
  default: {
    document: {
      run: { font: "Arial", size: 24 },
      paragraph: { spacing: { line: LINHA_15 } },
    },
  },
  paragraphStyles: [
    {
      id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: "Arial", size: 24, bold: true },
      paragraph: { pageBreakBefore: true, keepNext: true, outlineLevel: 0,
                   spacing: { before: 0, after: LINHA_15, line: LINHA_15 } },
    },
    {
      id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: "Arial", size: 24 },
      paragraph: { keepNext: true, outlineLevel: 1, spacing: { before: LINHA_15, after: LINHA_15, line: LINHA_15 } },
    },
    {
      id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: "Arial", size: 24, bold: true },
      paragraph: { keepNext: true, outlineLevel: 2, spacing: { before: LINHA_15, after: LINHA_15, line: LINHA_15 } },
    },
    {
      id: "TituloPre", name: "Título pré-textual", basedOn: "Normal", next: "Normal",
      run: { font: "Arial", size: 24, bold: true },
      paragraph: { alignment: AlignmentType.CENTER, pageBreakBefore: true, keepNext: true,
                   spacing: { before: 0, after: LINHA_15, line: LINHA_15 } },
    },
    {
      id: "Legenda", name: "Legenda ABNT", basedOn: "Normal", next: "Normal",
      run: { font: "Arial", size: 20 },
      paragraph: { alignment: AlignmentType.CENTER, keepNext: true,
                   spacing: { before: 240, after: 80, line: LINHA_1 } },
    },
    {
      id: "FonteIlustracao", name: "Fonte da ilustração", basedOn: "Normal", next: "Normal",
      run: { font: "Arial", size: 20 },
      paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 80, after: 240, line: LINHA_1 } },
    },
    {
      id: "Referencia", name: "Referência ABNT", basedOn: "Normal", next: "Referencia",
      run: { font: "Arial", size: 24 },
      paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 0, after: 240, line: LINHA_1 } },
    },
    {
      id: "TOC1", name: "toc 1", basedOn: "Normal", next: "Normal",
      run: { bold: true },
      paragraph: { spacing: { line: LINHA_15, before: 0, after: 0 } },
    },
    {
      id: "TOC2", name: "toc 2", basedOn: "Normal", next: "Normal",
      paragraph: { spacing: { line: LINHA_15, before: 0, after: 0 } },
    },
    {
      id: "TOC3", name: "toc 3", basedOn: "Normal", next: "Normal",
      paragraph: { spacing: { line: LINHA_15, before: 0, after: 0 } },
    },
    {
      id: "TableofFigures", name: "table of figures", basedOn: "Normal", next: "Normal",
      paragraph: { spacing: { line: LINHA_15, before: 0, after: 0 } },
    },
  ],
};

const numeracao = {
  config: [{
    reference: "alineas",
    levels: [{
      level: 0, format: LevelFormat.LOWER_LETTER, text: "%1)", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: RECUO + 397, hanging: 397 } } },
    }],
  }],
};

// ════════════════════════════════════════════════════════════════════
// ELEMENTOS PRÉ-TEXTUAIS
// ════════════════════════════════════════════════════════════════════
const centro = (t, opc = {}) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { line: opc.linha ?? LINHA_15 },
  children: [new TextRun({ text: t, bold: opc.negrito, break: opc.quebra })],
});

const tituloCapa = () => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { line: LINHA_15 },
  children: [new TextRun({ text: `${TITULO}: `, bold: true }), new TextRun({ text: SUBTITULO })],
});

const localAno = () => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { line: LINHA_15 },
  children: [new TextRun({ text: LOCAL, bold: true }), new TextRun({ text: ANO, bold: true, break: 1 })],
});

const vazio = () => new Paragraph({ children: [] });

const capa = [
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { line: LINHA_15 },
    children: [new TextRun({ text: INSTITUICAO, bold: true }), new TextRun({ text: CURSO, bold: true, break: 1 })],
  }),
  centro(AUTOR, { negrito: true }),
  tituloCapa(),
  vazio(),
  localAno(),
];

const folhaDeRosto = [
  centro(AUTOR, { negrito: true }),
  tituloCapa(),
  new Paragraph({
    indent: { left: 8 * CM }, alignment: AlignmentType.JUSTIFIED, spacing: { line: LINHA_1 },
    children: runs("Relatório final de pesquisa apresentado ao Programa Institucional de Bolsas de Iniciação " +
      "Científica (PIBIC/CNPq) da Universidade Cidade de São Paulo, como resultado do projeto " +
      "desenvolvido no curso de Ciência da Computação."),
  }),
  new Paragraph({
    indent: { left: 8 * CM }, spacing: { line: LINHA_1, before: 240 },
    children: [new TextRun(`Orientador: ${ORIENTADOR}`)],
  }),
  localAno(),
];

const agradecimentos = [
  tituloPre("AGRADECIMENTOS"),
  p("Ao Prof. Francisco de Assis Cavallaro, pela orientação ao longo deste projeto."),
  p("À Universidade Cidade de São Paulo e ao Conselho Nacional de Desenvolvimento Científico e " +
    "Tecnológico (CNPq), pelo Programa Institucional de Bolsas de Iniciação Científica, no qual " +
    "este trabalho foi realizado."),
  p("[[PREENCHER: agradecimento aos estudantes que participaram da avaliação e a outras pessoas que contribuíram.]]"),
];

const resumo = [
  tituloPre("RESUMO"),
  p("O estudo dos marcadores bioquímicos exige que o estudante retenha faixas de referência e associe " +
    "cada alteração às condições clínicas que ela sugere, um conteúdo extenso que tende a ser esquecido " +
    "entre a disciplina e a prática. Este trabalho teve como objetivo desenvolver e avaliar o " +
    "BioquímicaEDU, software educacional para o estudo de 20 marcadores bioquímicos de seis sistemas, " +
    "fundamentado em prática de recuperação, repetição espaçada e monitoramento metacognitivo. O " +
    "software foi desenvolvido em Python, de forma iterativa e com controle de versões, em três versões " +
    "que compartilham o mesmo conteúdo e o mesmo motor de aprendizagem: uma para computador, uma para " +
    "computador com tutor de inteligência artificial executado localmente e uma para dispositivos " +
    "móveis, configurada para gerar pacotes Android. O motor agenda as revisões com uma adaptação do " +
    "algoritmo SM-2, atribui notas diferentes a revisões, flashcards, questões e casos clínicos, e " +
    `compara a confiança declarada pelo estudante antes de ver a resposta com o acerto real. O conteúdo reúne ${C.flashcards} ` +
    `flashcards, ${C.questoes} questões, ${C.casos_clinicos} casos clínicos, ${C.exemplos} exemplos clínicos e ${C.diagramas} ` +
    "diagramas, com fontes conferidas na literatura médica, e os dados do estudante permanecem no " +
    "próprio aparelho. A verificação funcional foi feita com testes automatizados que percorrem as " +
    "telas das versões para computador e para celular. [[PREENCHER: síntese da avaliação com usuários — " +
    "número de participantes, instrumento e principais resultados.]] Após a avaliação, as interfaces " +
    "foram unificadas num único aplicativo, que se adapta ao celular, ao tablet e ao computador, com " +
    "recursos de acessibilidade — texto ampliado, alto contraste, fonte para baixa visão, leitura em voz " +
    "alta e atalho para Libras — e um tutor opcional com inteligência artificial generativa, ancorado no " +
    "conteúdo curado. Conclui-se que [[PREENCHER: conclusão apoiada nos resultados da avaliação.]]",
    { semRecuo: true }),
  p("**Palavras-chave:** bioquímica clínica; repetição espaçada; software educacional; aprendizagem " +
    "móvel; metacognição.", { semRecuo: true, antes: LINHA_15 }),
];

const abstract = [
  tituloPre("ABSTRACT"),
  p("Studying biochemical markers requires students to retain reference ranges and to relate each " +
    "abnormality to the clinical conditions it suggests, a large body of content that tends to be " +
    "forgotten between coursework and practice. This work aimed to develop and evaluate BioquímicaEDU, " +
    "an educational software for studying 20 biochemical markers across six body systems, grounded in " +
    "retrieval practice, spaced repetition and metacognitive monitoring. The software was developed in " +
    "Python, iteratively and under version control, in three versions that share the same content and " +
    "learning engine: a desktop version, a desktop version with an artificial intelligence tutor run " +
    "locally, and a mobile version configured to build Android packages. The engine schedules reviews " +
    "with an adaptation of the SM-2 algorithm, assigns different grades to reviews, flashcards, " +
    "questions and clinical cases, and compares the confidence students declare before seeing the " +
    `answer with their actual accuracy. The content comprises ${C.flashcards} flashcards, ${C.questoes} questions, ` +
    `${C.casos_clinicos} clinical cases, ${C.exemplos} clinical examples and ${C.diagramas} diagrams, with sources checked ` +
    "against the medical literature, and all student data stay on the device. Functional verification " +
    "used automated tests that go through the screens of the desktop and mobile versions. [[PREENCHER: " +
    "summary of the user evaluation — participants, instrument and main results.]] After the evaluation, " +
    "the interfaces were merged into a single app that adapts to phones, tablets and computers, with " +
    "accessibility features — larger text, high contrast, a typeface for low vision, read-aloud and a " +
    "shortcut to Brazilian Sign Language (Libras) — and an optional generative artificial intelligence " +
    "tutor grounded in the curated content. [[PREENCHER: conclusion.]]",
    { semRecuo: true }),
  p("**Keywords:** clinical biochemistry; spaced repetition; educational software; mobile learning; " +
    "metacognition.", { semRecuo: true, antes: LINHA_15 }),
];

const listaDe = (titulo, rotulo) => [
  tituloPre(titulo),
  new TableOfContents(titulo, { hyperlink: true, captionLabelIncludingNumbers: rotulo }),
];

const SIGLAS = [
  ["ALT", "Alanina aminotransferase"],
  ["API", "Interface de programação de aplicações (~Application Programming Interface~)"],
  ["APK", "Pacote de aplicativo Android (~Android Package~)"],
  ["AST", "Aspartato aminotransferase"],
  ["CK-MB", "Creatinoquinase, fração MB"],
  ["CNPq", "Conselho Nacional de Desenvolvimento Científico e Tecnológico"],
  ["CSV", "Valores separados por vírgula (~Comma-Separated Values~)"],
  ["dp", "Pixel independente de densidade (~density-independent pixel~)"],
  ["EF", "Fator de facilidade (~Easiness Factor~)"],
  ["GGT", "Gama-glutamiltransferase"],
  ["HbA1c", "Hemoglobina glicada"],
  ["HDL", "Lipoproteína de alta densidade (~High-Density Lipoprotein~)"],
  ["HTTPS", "Protocolo de transferência de hipertexto seguro (~Hypertext Transfer Protocol Secure~)"],
  ["IA", "Inteligência artificial"],
  ["JSON", "Notação de objetos JavaScript (~JavaScript Object Notation~)"],
  ["LDH", "Lactato desidrogenase"],
  ["LDL", "Lipoproteína de baixa densidade (~Low-Density Lipoprotein~)"],
  ["LGPD", "Lei Geral de Proteção de Dados Pessoais"],
  ["Libras", "Língua Brasileira de Sinais"],
  ["PIBIC", "Programa Institucional de Bolsas de Iniciação Científica"],
  ["SM-2", "Algoritmo SuperMemo 2"],
  ["UNICID", "Universidade Cidade de São Paulo"],
  ["WCAG", "Diretrizes de acessibilidade para conteúdo web (~Web Content Accessibility Guidelines~)"],
];
const listaSiglas = [
  tituloPre("LISTA DE ABREVIATURAS E SIGLAS"),
  ...SIGLAS.map(([s, d]) => new Paragraph({
    tabStops: [{ type: TabStopType.LEFT, position: 1701 }],
    indent: { left: 1701, hanging: 1701 },
    spacing: { line: LINHA_15 },
    children: [new TextRun(s), new TextRun("\t"), ...runs(d)],
  })),
];

const sumario = [
  tituloPre("SUMÁRIO"),
  new TableOfContents("Sumário", { hyperlink: true, headingStyleRange: "1-3" }),
];

// ════════════════════════════════════════════════════════════════════
// ELEMENTOS TEXTUAIS
// ════════════════════════════════════════════════════════════════════
const COLUNAS_QUADRO_MARCADORES = [
  { titulo: "Sistema", largura: 3100 },
  { titulo: "Marcadores", largura: 5970 },
];
const NOME_SISTEMA = {
  "Hepático": "Hepático", "Renal": "Renal", "Glicêmico": "Glicêmico", "Lipídico": "Lipídico",
  "Eletrólito": "Eletrólitos e equilíbrio ácido-base", "Cardíaco": "Cardíaco",
};
const porSistema = {};
for (const m of MARCADORES) (porSistema[m.categoria] ||= []).push(`${m.nome} (${m.sigla})`);

const introducao = [
  h1("1 INTRODUÇÃO"),
  p("Os exames laboratoriais participam de grande parte das decisões clínicas, e interpretar um " +
    "marcador bioquímico exige mais do que memorizar sua faixa de referência: é preciso saber o que " +
    "significa estar acima ou abaixo dela, a que condições cada alteração se associa e como diferentes " +
    "marcadores se combinam num mesmo quadro. As provas de função hepática ilustram bem esse ponto: " +
    "o padrão conjunto das aminotransferases, da fosfatase alcalina, da gama-glutamiltransferase (GGT) " +
    "e da bilirrubina ajuda a distinguir lesão hepatocelular de colestase, algo que nenhum desses " +
    "valores informa isoladamente (Jogu; Zubair; Minter, 2026)."),
  p("O volume desse conteúdo cria um problema conhecido de aprendizagem: o que é estudado de forma " +
    "concentrada, às vésperas de uma avaliação, tende a ser esquecido antes de ser usado. A psicologia " +
    "cognitiva descreve duas estratégias que atacam esse problema. Na prática de recuperação, o " +
    "estudante tenta lembrar a informação em vez de relê-la (Roediger; Karpicke, 2006); na prática " +
    "distribuída, as sessões de estudo são espaçadas no tempo (Cepeda ~et al.~, 2006). Em educação " +
    "médica, uma meta-análise recente com 13 estudos e 21.415 estudantes encontrou efeito favorável à " +
    "repetição espaçada em testes objetivos, com diferença média padronizada de 0,78 (Maye; Hurley, 2026)."),
  p("Aplicar essas estratégias sem apoio, porém, é trabalhoso: o estudante precisaria registrar o que " +
    "estudou, quando e com que resultado, e calcular quando revisar cada item. Além disso, estudantes " +
    "tendem a superestimar o próprio conhecimento, e os de menor desempenho são justamente os que mais " +
    "se enganam (Kruger; Dunning, 1999; Karaca ~et al.~, 2023). Um software pode assumir o agendamento " +
    "das revisões e devolver ao estudante uma medida da diferença entre o que ele acha que sabe e o que " +
    "de fato acerta."),
  p("Este trabalho, desenvolvido no Programa Institucional de Bolsas de Iniciação Científica (PIBIC) da " +
    "Universidade Cidade de São Paulo (UNICID), no curso de Ciência da Computação, apresenta o " +
    "BioquímicaEDU, software educacional para o estudo de marcadores bioquímicos construído sobre esses " +
    "princípios. O relatório descreve as decisões de projeto, a implementação das versões para " +
    "computador e para dispositivos móveis, a verificação realizada, a avaliação com usuários e a " +
    "evolução do software depois dela."),

  h2("1.1 OBJETIVOS"),
  h3("1.1.1 Objetivo geral"),
  p("Desenvolver e avaliar um software educacional para o estudo de marcadores bioquímicos que " +
    "organize o estudo por prática de recuperação e repetição espaçada, disponível para computador e " +
    "para dispositivos móveis."),
  h3("1.1.2 Objetivos específicos"),
  p("Os objetivos específicos foram:", { manterComProximo: true }),
  ...alineas([
    "reunir conteúdo sobre 20 marcadores bioquímicos — faixas de referência, interpretação das " +
      "alterações, casos clínicos e diagramas — com fontes verificáveis;",
    "implementar um motor de aprendizagem que agende as revisões por repetição espaçada e integre as " +
      "diferentes atividades de estudo;",
    "registrar a confiança declarada pelo estudante e compará-la com o desempenho, como recurso de " +
      "autorregulação;",
    "disponibilizar o software em versões para computador e para dispositivos móveis, mantendo os " +
      "dados do estudante no próprio aparelho;",
    "avaliar o software com estudantes quanto à usabilidade e à percepção de aprendizagem " +
      "[[CONFIRMAR: ajustar ao que a avaliação de fato mediu]].",
  ]),

  h2("1.2 ORGANIZAÇÃO DO RELATÓRIO"),
  p("A seção 2 apresenta a fundamentação teórica; a seção 3 descreve materiais e métodos; a seção 4 " +
    "reúne os resultados, isto é, o software produzido, sua avaliação e a evolução posterior; a seção 5 discute as decisões " +
    "de projeto e as limitações; e a seção 6 traz as considerações finais."),
];

const fundamentacao = [
  h1("2 FUNDAMENTAÇÃO TEÓRICA"),
  p("Esta seção reúne os conceitos que orientaram o projeto: o conteúdo a ser aprendido, as " +
    "estratégias de estudo com evidência de eficácia, o algoritmo de agendamento adotado e os " +
    "cuidados com motivação e autoavaliação."),

  h2("2.1 MARCADORES BIOQUÍMICOS NO DIAGNÓSTICO CLÍNICO"),
  p("Marcadores bioquímicos são substâncias medidas em amostras biológicas, sobretudo no sangue, cuja " +
    "concentração reflete o funcionamento de órgãos e sistemas. A interpretação parte de uma faixa de " +
    "referência e considera a direção da alteração e o contexto clínico. A creatinina e a ureia, por " +
    "exemplo, são usadas na avaliação da função renal (Gounden; Bhatt; Jialal, 2024); a troponina é o " +
    "marcador de escolha para lesão do miocárdio (Zubair; Sharma, 2026); e a hemoglobina glicada " +
    "(HbA1c) reflete a glicemia média dos meses anteriores, servindo ao diagnóstico e ao acompanhamento " +
    "do diabetes (Eyth; Zubair; Naik, 2025)."),
  p(`O software aborda ${C.marcadores} marcadores distribuídos em ${C.sistemas} sistemas, apresentados no Quadro 1. A ` +
    "seleção cobre exames de rotina na prática clínica e permite montar casos em que vários marcadores " +
    "precisam ser lidos em conjunto.", { manterComProximo: true }),
  ...quadro("Marcadores abordados no software, por sistema",
    COLUNAS_QUADRO_MARCADORES,
    Object.entries(porSistema).map(([cat, lista]) => [NOME_SISTEMA[cat] || cat, lista.join("; ")]),
    "elaborado pelo autor (2026), a partir de data/marcadores.csv."),

  h2("2.2 PRÁTICA DE RECUPERAÇÃO E REPETIÇÃO ESPAÇADA"),
  p("Roediger e Karpicke (2006) compararam estudantes que, depois de ler textos, fizeram testes de " +
    "recordação livre com estudantes que releram o material o mesmo número de vezes. No teste final " +
    "aplicado cinco minutos depois, a releitura levou vantagem; após dois dias e após uma semana, quem " +
    "havia sido testado lembrou substancialmente mais — embora a releitura tivesse aumentado a confiança " +
    "dos estudantes em sua memória. O teste, portanto, não apenas mede a aprendizagem: também a produz. " +
    "Nas profissões da saúde, a prática de recuperação foi amplamente adotada, sobretudo na preparação " +
    "para provas, mas ainda encontra barreiras à adoção pelos próprios estudantes (Serra ~et al.~, 2025)."),
  p("A segunda estratégia é o espaçamento. Em meta-análise com 839 avaliações de 317 experimentos, " +
    "Cepeda ~et al.~ (2006) verificaram que o intervalo entre sessões que maximiza a retenção cresce à " +
    "medida que aumenta o tempo até o teste final. Para quem precisa lembrar um conteúdo por meses ou " +
    "anos, os intervalos entre revisões devem crescer — e é exatamente isso que os algoritmos de " +
    "repetição espaçada fazem."),
  p("A evidência em educação médica é consistente com esses resultados. A revisão sistemática de Maye " +
    "e Hurley (2026) incluiu 14 estudos, dos quais 13 entraram na meta-análise, somando 21.415 " +
    "estudantes; a repetição espaçada superou as técnicas de estudo habituais em testes objetivos " +
    "(diferença média padronizada de 0,78; intervalo de confiança de 95% de 0,56 a 0,99), com " +
    "intervenções que incluíam ~flashcards~, questões de múltipla escolha enviadas por e-mail e testes " +
    "espaçados em sala de aula. Em estudo anterior, com 72 estudantes de Medicina, a quantidade de " +
    "~flashcards~ distintos estudados com repetição espaçada e a de questões resolvidas foram preditores " +
    "independentes da nota no exame de licenciamento médico norte-americano (Deng; Gluckstein; Larsen, 2015)."),

  h2("2.3 O ALGORITMO SM-2"),
  p("O SM-2 foi descrito por Wozniak (1990) para o método SuperMemo. Cada item tem um fator de " +
    "facilidade (EF), que começa em 2,5. Após cada repetição, o estudante avalia a qualidade da própria " +
    "resposta numa escala de 0 a 5, e o intervalo até a repetição seguinte é de 1 dia na primeira vez, " +
    "6 dias na segunda e, a partir daí, o intervalo anterior multiplicado pelo EF. O fator é ajustado a " +
    "cada resposta pela Equação 1, em que ~q~ é a nota atribuída, e nunca fica abaixo de 1,3:",
    { manterComProximo: true }),
  equacao("EF′ = EF + (0,1 − (5 − ~q~) × (0,08 + (5 − ~q~) × 0,02))", 1),
  p("Com nota 4 o fator não muda; com nota 5 aumenta 0,1; com nota 3 diminui 0,14; e com nota 0 " +
    "diminui 0,8. Notas abaixo de 3 indicam falha: as repetições do item recomeçam do início, sem " +
    "alterar o EF. Ao final de cada sessão diária, o algoritmo original ainda manda repetir todos os " +
    "itens que receberam nota inferior a 4, até que cada um alcance essa nota (Wozniak, 1990). O " +
    "BioquímicaEDU parte dessas regras com três adaptações, descritas na seção 4.2."),

  h2("2.4 GAMIFICAÇÃO E MOTIVAÇÃO"),
  p("Gamificação é o uso de elementos de jogos, como pontos, medalhas e classificações, em contextos " +
    "que não são jogos. A evidência sobre seu efeito na aprendizagem é mista. Em dois experimentos com " +
    "turmas de Física ~online~ (N = 102 e N = 88), medalhas (~badges~) e classificações " +
    "(~leaderboards~) não afetaram o desempenho acadêmico, ainda que os estudantes as vissem com bons " +
    "olhos (Balci; Secaur; Morris, 2022). Já um programa baseado em desafios, avaliado com 60 " +
    "universitários durante um semestre, aumentou o desempenho e a motivação do grupo experimental " +
    "(Kaya; Ercag, 2023)."),
  p("A teoria da autodeterminação ajuda a explicar a diferença. Ela postula três necessidades " +
    "psicológicas básicas — competência, autonomia e pertencimento —, cuja satisfação favorece a " +
    "motivação intrínseca (Ryan; Deci, 2000). Recompensas, porém, podem atuar contra ela: em " +
    "meta-análise de 128 estudos, recompensas tangíveis condicionadas a participar, concluir ou atingir " +
    "desempenho reduziram a motivação intrínseca medida pelo comportamento de livre escolha, enquanto o " +
    "~feedback~ positivo a aumentou (d = 0,33) e elevou o interesse declarado (d = 0,31) (Deci; " +
    "Koestner; Ryan, 1999). Para o projeto, a consequência foi tratar os números exibidos como " +
    "informação sobre a competência do estudante, e não como prêmio pela atividade."),

  h2("2.5 METACOGNIÇÃO E CALIBRAÇÃO"),
  p("Calibração é a correspondência entre o desempenho que a pessoa julga ter e o desempenho real. " +
    "Kruger e Dunning (1999) mostraram que participantes no quartil inferior de testes de gramática, " +
    "lógica e humor se situavam, em média, no 12º percentil, mas se estimavam no 62º. A má calibração " +
    "também é estável: estudantes de baixo desempenho mantiveram previsões de nota otimistas, e a " +
    "confiança nelas, ao longo de quatro provas de um semestre (Karaca ~et al.~, 2023). Em educação " +
    "médica, entre 157 estudantes do primeiro ano avaliados numa simulação de paciente virtual, 98% " +
    "superestimaram o próprio desempenho na anamnese e 95% no exame físico (Cleary ~et al.~, 2019)."),
  p("Esses resultados sugerem que o estudante, sozinho, dificilmente percebe a distância entre o que " +
    "acha que sabe e o que sabe. Medi-la exige registrar a confiança antes de a resposta ser revelada, " +
    "pois depois dela a estimativa já estaria contaminada pela própria resposta. Essa é a lógica do " +
    "registro de calibração descrito na seção 4.2."),
];

const COLUNAS_TECNOLOGIAS = [
  { titulo: "Tecnologia", largura: 2600 },
  { titulo: "Versão", largura: 1300 },
  { titulo: "Uso no projeto", largura: 5170 },
];

const metodos = [
  h1("3 MATERIAIS E MÉTODOS"),
  h2("3.1 NATUREZA DA PESQUISA E ETAPAS"),
  p("Trata-se de pesquisa aplicada, de desenvolvimento tecnológico, com avaliação junto a usuários " +
    "[[CONFIRMAR: abordagem quantitativa, qualitativa ou mista]]. O software foi construído de forma " +
    "iterativa e incremental: cada ciclo de implementação, verificação e revisão foi registrado no " +
    `sistema de controle de versões Git, e o código está publicado em ${REPOSITORIO}. O trabalho seguiu ` +
    "as etapas abaixo:", { manterComProximo: true }),
  ...alineas([
    "levantamento do conteúdo e das fontes bibliográficas de cada marcador;",
    "prototipação das versões para computador e para dispositivos móveis;",
    "implementação do motor de aprendizagem e sua integração às atividades de estudo;",
    "redesenho da interface móvel e criação da identidade visual;",
    "verificação automatizada do funcionamento;",
    "avaliação com usuários;",
    "evolução após a avaliação: interface única para celular, tablet e computador, recursos de " +
      "acessibilidade, intervalos diferenciados na revisão e tutor com inteligência artificial generativa.",
  ]),

  h2("3.2 CURADORIA DO CONTEÚDO"),
  p("O conteúdo fica em arquivos de dados separados do código, o que permite revisá-lo sem programar. " +
    "O arquivo de marcadores, em formato CSV, traz nome, sigla, sistema, limites da faixa de " +
    "referência, unidade, interpretação de valores altos e baixos e condições associadas a cada " +
    "direção. Arquivos JSON guardam os ~flashcards~, as questões, os casos clínicos e, para cada " +
    "marcador, exemplos clínicos, referências bibliográficas e vídeos. Os diagramas são gerados por um " +
    "programa a partir de dados, com a biblioteca Matplotlib, o que garante que possam ser refeitos e " +
    "corrigidos."),
  p("Cada marcador foi associado a capítulos do StatPearls e do ~Clinical Methods~, obras de " +
    "referência médica disponíveis no NCBI Bookshelf; a relação completa está no Apêndice A. Durante o " +
    "desenvolvimento, links de vídeos cuja origem não pôde ser confirmada foram removidos e substituídos " +
    "por essa bibliografia, restando apenas dois vídeos de canais identificados. Os textos também foram " +
    "revisados quanto à acentuação e ao uso da vírgula decimal. [[CONFIRMAR: se o conteúdo foi revisado " +
    "pelo orientador ou por docente da área da saúde, e como.]]"),

  h2("3.3 TECNOLOGIAS UTILIZADAS"),
  p("O software foi escrito em Python (Python Software Foundation, 2023), escolhido por permitir " +
    "compartilhar o mesmo motor de aprendizagem e os mesmos dados entre as interfaces para computador " +
    "e para celular. O Quadro 2 lista as tecnologias empregadas.", { manterComProximo: true }),
  ...quadro("Tecnologias utilizadas", COLUNAS_TECNOLOGIAS, [
    ["Python", "3.12", "Linguagem de todas as versões e dos programas auxiliares"],
    ["Tkinter (Tk)", "8.6", "Interface das versões para computador"],
    ["Kivy", "2.3.1", "Interface da versão para dispositivos móveis e, após a avaliação, do aplicativo único (Kivy Organization, 2024)"],
    ["Buildozer e python-for-android", "—", "Empacotamento da versão móvel para Android"],
    ["Ollama", "—", "Execução local do modelo de linguagem do tutor, opcional (Ollama, [2026])"],
    ["Gemini API", "gemini-3.8-flash", "Modelo de linguagem em nuvem do tutor, opcional, após a avaliação (Google, [2026b])"],
    ["Cloudflare Workers", "—", "Servidor intermediário que guarda a chave do Gemini para a versão móvel (Cloudflare, [2026])"],
    ["Atkinson Hyperlegible", "—", "Fonte opcional para leitura facilitada (Braille Institute, [2026])"],
    ["Matplotlib", "3.11", "Diagramas do conteúdo e gráficos deste relatório"],
    ["Pillow", "12.3", "Ícone e tela de abertura do aplicativo; capturas de tela"],
    ["fontTools", "4.64", "Conversão do texto da logo em contornos vetoriais"],
    ["Git e GitHub", "—", "Controle de versões e publicação do código"],
  ], "elaborado pelo autor (2026)."),

  h2("3.4 ARQUITETURA DO SOFTWARE"),
  p(`O software foi organizado em três camadas (Figura ${fig("arquitetura")}). Na camada de interfaces estão as três ` +
    "versões; no núcleo, o motor de aprendizagem e o tutor; e na camada de dados, o conteúdo, apenas " +
    "lido, e o progresso do estudante, lido e gravado pelo motor. Como o motor não depende de nenhuma " +
    "interface, as mesmas regras de agendamento valem no computador e no celular.",
    { manterComProximo: true }),
  ...figura("arquitetura", path.join(FIG, "arquitetura.png"), "Arquitetura do BioquímicaEDU",
    "elaborado pelo autor (2026)."),
  p("A versão móvel é um pacote próprio, dividido em tema (cores e tipografia), componentes visuais " +
    "reutilizáveis, telas e acesso a dados. No Android, o empacotador sempre executa o arquivo " +
    "main.py; por isso esse arquivo verifica em que plataforma está e, no celular, inicia a versão " +
    "móvel antes de carregar o Tkinter, que não existe no Android. Depois da avaliação, a camada de " +
    "interfaces passou a ter um único aplicativo, também iniciado pelo main.py (seção 4.7.2)."),

  h2("3.5 VERIFICAÇÃO DO SOFTWARE"),
  p("O funcionamento foi verificado com programas de teste automatizado incluídos no repositório. O " +
    "primeiro abre a versão móvel e percorre todas as abas, a busca e o filtro de marcadores, o detalhe " +
    "com suas abas, uma revisão completa, os ~flashcards~, um quiz inteiro, um caso clínico e o tutor, " +
    "conferindo ao final se o painel inicial reflete a sessão; depois da avaliação, passou a rodar nos " +
    "formatos de celular e de computador e a conferir também os recursos de acessibilidade e a troca de " +
    "formato ao redimensionar a janela. O segundo abre cada tela das duas versões para computador e o " +
    "detalhe de um marcador em todas as abas. Um terceiro, criado com o tutor em nuvem, é descrito na " +
    "seção 4.7.4. Os testes gravam numa pasta temporária, de modo que o progresso real do usuário não é " +
    "lido nem alterado."),
  p("Além disso, as telas da versão móvel foram renderizadas na resolução de um celular — e, depois da " +
    "avaliação, também nas de tablet e de computador — e inspecionadas uma a uma, e o comportamento do " +
    "motor de agendamento foi conferido executando o próprio código com sequências de respostas cujo " +
    "resultado esperado pode ser calculado à mão (seção 4.2)."),

  h2("3.6 AVALIAÇÃO COM USUÁRIOS"),
  p("[[PREENCHER: tipo de estudo — por exemplo, estudo exploratório com questionário após uso do software.]]"),
  p("**Participantes:** [[PREENCHER: número, curso, semestre e forma de recrutamento.]]"),
  p("**Instrumento:** [[PREENCHER: questionário próprio, escala de usabilidade, pré e pós-teste de " +
    "conhecimento etc. Se houver questionário próprio, incluí-lo como Apêndice.]]"),
  p("**Procedimento:** [[PREENCHER: versão usada (computador ou celular), duração do uso, tarefas " +
    "solicitadas e local.]]"),
  p("**Análise dos dados:** [[PREENCHER: estatística descritiva, testes aplicados.]]"),
  p("**Aspectos éticos:** [[PREENCHER: aprovação pelo Comitê de Ética em Pesquisa (número do CAAE e " +
    "do parecer) ou justificativa de dispensa, e forma de registro do consentimento livre e esclarecido.]]"),

  h2("3.7 USO DE FERRAMENTAS DE INTELIGÊNCIA ARTIFICIAL"),
  p("Durante o desenvolvimento foi utilizado um assistente de programação baseado em inteligência " +
    "artificial (IA), o Claude, da empresa Anthropic, como apoio na implementação, na revisão do código, " +
    "na documentação e na redação deste relatório. O assistente foi usado sob supervisão do autor, que " +
    "definiu os requisitos, revisou as alterações e validou o funcionamento do software. As referências " +
    "citadas foram conferidas nas bases de origem (PubMed e NCBI Bookshelf). [[CONFIRMAR com o " +
    "orientador a redação desta declaração, conforme a política da instituição e do programa.]]"),
];

const COLUNAS_ADAPTACOES = [
  { titulo: "Aspecto", largura: 1800 },
  { titulo: "SM-2 original", largura: 2300 },
  { titulo: "BioquímicaEDU", largura: 2300 },
  { titulo: "Motivo", largura: 2670 },
];
const COLUNAS_NOTAS = [
  { titulo: "Atividade", largura: 2000 },
  { titulo: "Acerto", largura: 1900, alinhamento: AlignmentType.CENTER },
  { titulo: "Erro", largura: 1300, alinhamento: AlignmentType.CENTER },
  { titulo: "Justificativa", largura: 3870 },
];
const COLUNAS_CONTEUDO = [
  { titulo: "Item", largura: 6200 },
  { titulo: "Quantidade", largura: 2000, alinhamento: AlignmentType.CENTER },
];
const COLUNAS_CODIGO = [
  { titulo: "Módulo", largura: 6200 },
  { titulo: "Linhas", largura: 2000, alinhamento: AlignmentType.CENTER },
];
const COLUNAS_VERSOES = [
  { titulo: "Versão", largura: 1900 },
  { titulo: "Arquivo de entrada", largura: 2300 },
  { titulo: "Recursos", largura: 4870 },
];

const sm2 = JSON.parse(fs.readFileSync(path.join(FIG, "sm2_intervalos.json"), "utf8"));
const seq = Object.values(sm2);
const serie = (v) => v.join(", ");

// Evolução após a avaliação (seção 4.7): números gerados por gerar_figuras.py
const SM2E = JSON.parse(fs.readFileSync(path.join(FIG, "sm2_evolucao.json"), "utf8"));
const ME = JSON.parse(fs.readFileSync(path.join(FIG, "metricas_evolucao.json"), "utf8"));
const TUTOR = TEM_FIGURA_TUTOR
  ? JSON.parse(fs.readFileSync(path.join(FIG, "evolucao_tutor.json"), "utf8")) : null;
const trio = (v) => v.join(" / ");
const MESES = ["jan.", "fev.", "mar.", "abr.", "maio", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."];
const dataAbnt = (iso) => { const [a, m, d] = iso.split("-").map(Number); return `${d} ${MESES[m - 1]} ${a}`; };
const COLUNAS_INTERVALOS = [
  { titulo: "Revisão", largura: 2270 },
  { titulo: "Versão avaliada (Difícil / Bom / Fácil)", largura: 3400, alinhamento: AlignmentType.CENTER },
  { titulo: "Versão atual (Difícil / Bom / Fácil)", largura: 3400, alinhamento: AlignmentType.CENTER },
];
const COLUNAS_FORMATOS = [
  { titulo: "Formato", largura: 1400 },
  { titulo: "Largura da janela", largura: 1650 },
  { titulo: "Aparelho típico", largura: 1800 },
  { titulo: "Navegação", largura: 1550 },
  { titulo: "Organização do conteúdo", largura: 2670 },
];
const ROTULO_REVISAO = { 1: "1ª (primeiro acerto)", 2: "2ª", 3: "3ª", 4: "4ª" };

const resultados = [
  h1("4 RESULTADOS"),
  h2("4.1 VISÃO GERAL DO SOFTWARE"),
  p("O BioquímicaEDU foi entregue em três versões que compartilham conteúdo e motor de aprendizagem " +
    "(Quadro 3). As versões para computador foram testadas em Windows 10; a versão móvel roda também no " +
    "computador, o que facilita o desenvolvimento, e está configurada para gerar o pacote Android.",
    { manterComProximo: true }),
  ...quadro("Versões do BioquímicaEDU", COLUNAS_VERSOES, [
    ["Computador", "main.py", "Painel de estudo, revisão espaçada, estudo por marcador, ~flashcards~, quiz e casos clínicos"],
    ["Computador com tutor", "main_enhanced.py", "Recursos da versão anterior, mais tutor por conversa, questões geradas pelo modelo de linguagem e discussão de casos"],
    ["Dispositivos móveis", "main_kivy_completo.py (no Android, main.py)", "Cinco abas — Início, Estudo, Cards, Prática e Tutor — e revisão espaçada"],
  ], "elaborado pelo autor (2026)."),
  p("A Tabela 1 resume o conteúdo educacional disponível, e a Tabela 2, o tamanho do código-fonte.",
    { manterComProximo: true }),
  ...tabela("Conteúdo educacional do software", COLUNAS_CONTEUDO, [
    ["Marcadores bioquímicos", String(C.marcadores)],
    ["Sistemas", String(C.sistemas)],
    ["~Flashcards~", String(C.flashcards)],
    ["Questões de múltipla escolha", String(C.questoes)],
    ["Casos clínicos para diagnóstico", String(C.casos_clinicos)],
    ["Exemplos clínicos ligados aos marcadores", String(C.exemplos)],
    [`Diagramas (em ${C.marcadores_com_diagrama} marcadores)`, String(C.diagramas)],
    [`Vínculos com referências bibliográficas (${C.referencias_unicas} fontes distintas)`, String(C.referencias)],
    ["Vídeos de canais identificados", String(C.videos)],
  ], "elaborado pelo autor (2026), a partir dos arquivos de dados do software."),
  ...tabela("Tamanho do código-fonte por módulo", COLUNAS_CODIGO, [
    ...Object.entries(M.codigo).map(([k, v]) => [k, fmt(v)]),
    totalLinha(["Total", fmt(M.codigo_total)]),
  ], "elaborado pelo autor (2026). Contam-se as linhas não vazias, excluídos os comentários."),

  h2("4.2 MOTOR DE APRENDIZAGEM"),
  p("O motor guarda, para cada marcador, o número de repetições bem-sucedidas, o fator de facilidade, " +
    "o intervalo atual, a data da próxima revisão e o total de acertos e tentativas. A revisão segue " +
    "sempre a mesma ordem: o estudante vê a pergunta, declara numa escala de cinco níveis o quanto acha " +
    "que sabe, vê a resposta e se autoavalia em quatro botões — “De novo”, “Difícil”, “Bom” e “Fácil” " +
    "—, que correspondem às notas 0, 3, 4 e 5 do SM-2. Cada botão mostra, antes de ser tocado, quando o " +
    "marcador voltará. Na versão avaliada, o próximo intervalo é calculado com o fator de facilidade " +
    "anterior à resposta; por isso, depois do primeiro contato, “Difícil”, “Bom” e “Fácil” levam ao mesmo " +
    "próximo intervalo, e a diferença entre essas avaliações aparece nos intervalos seguintes, pelo " +
    "ajuste do fator. Esse comportamento foi alterado depois da avaliação (seção 4.7.1)."),
  p("O Quadro 4 descreve as três adaptações feitas ao SM-2 original.", { manterComProximo: true }),
  ...quadro("Adaptações do BioquímicaEDU ao SM-2", COLUNAS_ADAPTACOES, [
    ["Fator de facilidade após erro (nota < 3)",
      "O ciclo recomeça sem alterar o fator",
      "O ciclo recomeça e o fator é recalculado pela Equação 1, caindo",
      "Permite que um erro em caso clínico (nota 2) pese menos que um erro em questão direta (nota 0 ou 1)"],
    ["Repetição no mesmo dia",
      "Ao fim da sessão, repetem-se os itens com nota < 4 até cada um alcançar 4",
      "Voltam no mesmo dia só os itens errados (nota < 3), e um acerto basta para sair",
      "Manter a sessão curta, adequada ao celular; a nota 3 já é um acerto"],
    ["Primeiro acerto com “Fácil”",
      "Intervalo de 1 dia para qualquer nota ≥ 3",
      "Intervalo de 4 dias com nota 5",
      "Sem isso, as quatro avaliações dariam o mesmo agendamento no primeiro contato"],
  ], "elaborado pelo autor (2026), com base em Wozniak (1990)."),
  p(`A Figura ${fig("sm2")} mostra os intervalos calculados pelo próprio motor em três sequências de respostas a ` +
    `um mesmo marcador. Respondendo sempre “Bom”, os intervalos são de ${serie(seq[0])} dias; sempre ` +
    `“Fácil”, de ${serie(seq[1])} dias. Com um erro na quarta revisão, o marcador volta a 1 dia e ` +
    "recomeça o ciclo; como o fator de facilidade caiu de 2,5 para 1,96, a revisão seguinte às " +
    "mostradas seria em 12 dias, e não mais em 15.", { manterComProximo: true }),
  ...figura("sm2", path.join(FIG, "sm2_intervalos.png"),
    "Intervalos calculados pelo motor em três sequências de respostas",
    "elaborado pelo autor (2026), executando o código do motor (progresso.py).", { larguraCm: 15 }),
  p("As demais atividades também alimentam o agendamento, com as notas da Tabela 3. Para isso, o " +
    "motor identifica a quais marcadores cada questão ou caso se refere, procurando no texto as siglas, " +
    "os nomes e apelidos comuns (“troponina” para troponina I, por exemplo). Siglas que também são " +
    "palavras do português, como “Na”, só contam na forma iônica (Na+); assim, uma frase iniciada por " +
    "“Na hepatite…” não altera o agendamento do sódio. Quando nada é identificado, nada é registrado.",
    { manterComProximo: true }),
  ...tabela("Notas atribuídas pelo motor a cada atividade", COLUNAS_NOTAS, [
    ["Revisão", "3, 4 ou 5", "0", "Autoavaliação graduada pelo próprio estudante"],
    ["~Flashcard~", "4", "1", "Recuperação direta, avaliada como lembrei ou não lembrei"],
    ["Quiz", "4", "1", "A múltipla escolha permite acertar por eliminação, então o acerto não vale 5; ver as alternativas já é alguma exposição, então o erro não vale 0"],
    ["Caso clínico", "4", "2", "Errar o diagnóstico não prova desconhecer cada marcador do caso; a nota 2 ainda é falha, mas reduz menos o fator"],
  ], "elaborado pelo autor (2026)."),
  p("A fila de estudo do dia é montada em três prioridades: primeiro os marcadores errados no próprio " +
    "dia, depois os que chegaram à data de revisão, do mais atrasado ao mais recente, e por último " +
    "marcadores ainda não estudados, até o limite de 12 itens. Cada marcador é classificado em um de " +
    "quatro estágios conforme o intervalo já alcançado: novo (nunca estudado), aprendendo (menos de 6 " +
    "dias), firmando (de 6 a 20 dias) e consolidado (21 dias ou mais). O domínio de um marcador, " +
    "exibido em porcentagem, combina a taxa de acerto ~A~ e o intervalo ~I~, em dias, pela Equação 2:",
    { manterComProximo: true }),
  equacao("Domínio = 0,4 × ~A~ + 0,6 × mín(1, ~I~ / 30)", 2),
  p("O peso maior do intervalo reflete que acertar várias vezes no mesmo dia demonstra pouco sobre " +
    "retenção; um marcador lembrado depois de 30 dias, por outro lado, já é considerado retido."),
  p("Para a calibração, a confiança declarada antes de cada resposta (1 a 5) é convertida para a escala " +
    "de 0 a 1 e comparada com a taxa de acerto nas últimas 200 respostas. O resultado só é exibido a " +
    "partir de 10 respostas, para não rotular o estudante com base em poucas tentativas. Uma diferença " +
    "de até 0,15 é tratada como percepção próxima do desempenho; acima disso, o painel informa que o " +
    "estudante tem se achado mais preparado do que os acertos mostram ou, no caso contrário, que sabe " +
    "mais do que imagina."),
  p("Por fim, o painel mostra a sequência de dias de estudo e sete marcos, todos ligados à " +
    "aprendizagem e não ao tempo de uso: primeiro estudo, todos os marcadores estudados, primeira " +
    "retenção, 10 marcadores consolidados, metade consolidada, sete dias seguidos de estudo e confiança " +
    "alinhada ao desempenho. A sequência é contada a partir do dia anterior quando o estudante ainda " +
    "não estudou no dia corrente, para informar sem punir."),

  h2("4.3 VERSÃO PARA DISPOSITIVOS MÓVEIS"),
  p("A interface móvel foi redesenhada com fundo claro, verde como cor de destaque, uma cor por " +
    "sistema e tipografia Roboto, distribuída com o Kivy. A navegação usa cinco abas, com indicador " +
    "animado, e o botão voltar do Android percorre o histórico de telas. As Figuras " +
    `${fig("telas_inicio")} a ${fig("telas_pratica")} mostram as principais telas, capturadas com um ` +
    "progresso de exemplo de cerca de quatro semanas de uso.",
    { manterComProximo: true }),
  ...figura("telas_inicio", path.join(FIG, "telas_inicio_estudo.png"),
    "Início e estudo na versão móvel",
    "elaborado pelo autor (2026), com progresso de exemplo.",
    { nota: "(a) tela inicial; (b) lista de marcadores, com busca e filtro por sistema; (c) detalhe de um marcador." }),
  p("A tela inicial responde primeiro à pergunta “o que estudar agora?”: o cartão em destaque mostra a " +
    "revisão do dia e o tempo estimado. Abaixo vêm os atalhos para as atividades, o estado da memória, " +
    "os marcadores mais frágeis, o domínio por sistema, a autoavaliação, a constância das últimas quatro " +
    `semanas e os marcos. No detalhe de cada marcador (Figura ${fig("telas_inicio")}c), as abas reúnem ` +
    "visão geral, exemplos clínicos, diagramas, fontes e vídeos."),
  ...figura("telas_revisao", path.join(FIG, "telas_revisao.png"),
    "Revisão espaçada e ~flashcards~ na versão móvel",
    "elaborado pelo autor (2026), com progresso de exemplo.",
    { nota: "(a) revisão antes da resposta, com a confiança a declarar; (b) revisão depois da resposta, " +
            "com a autoavaliação; (c) verso de um ~flashcard~." }),
  p(`Na revisão (Figura ${fig("telas_revisao")}a), o botão de mostrar a resposta só se libera depois que ` +
    "o estudante declara sua confiança; os níveis não escolhidos ficam esmaecidos. Revelada a resposta " +
    `(Figura ${fig("telas_revisao")}b), os quatro botões de autoavaliação informam quando o marcador ` +
    "voltará; no exemplo, o marcador está na segunda repetição, e todas as avaliações de acerto levam " +
    `aos 6 dias previstos pelo SM-2. Nos ~flashcards~ (Figura ${fig("telas_revisao")}c), depois de virar o cartão o estudante ` +
    "informa se havia lembrado a resposta, e essa informação também reagenda o marcador."),
  ...figura("telas_pratica", path.join(FIG, "telas_pratica_tutor.png"),
    "Prática e tutor na versão móvel",
    "elaborado pelo autor (2026), com progresso de exemplo.",
    { nota: "(a) quiz, com ~feedback~ após uma resposta errada; (b) caso clínico; (c) tutor." }),
  p("No quiz e nos casos clínicos, cada resposta recebe ~feedback~ imediato com a explicação. Na versão " +
    "avaliada, o tutor da versão móvel funciona sem internet: responde a partir da base do próprio " +
    "aplicativo, apresentando faixa de referência, interpretação e condições associadas ao marcador " +
    "perguntado, e oferece sugestões de perguntas. A seção 4.7.4 descreve o tutor com inteligência " +
    "artificial generativa acrescentado depois."),
  p("Para o Android, o arquivo de configuração do empacotamento define a versão 36 da API como alvo, " +
    "exigência da Google Play para novos aplicativos e atualizações desde 31 de agosto de 2026 (Google, " +
    "[2026c]), e a versão 21 como mínima, abrangendo aparelhos antigos. O aplicativo não solicita nenhuma " +
    "permissão: não acessa a internet, e as referências e vídeos abrem no navegador do sistema. Depois " +
    "da avaliação, só o tutor em nuvem, opcional, passou a exigir acesso à internet (seção 4.7.4). " +
    "[[CONFIRMAR: se o APK foi gerado e testado em aparelho físico; em caso afirmativo, informar " +
    "modelo e versão do Android.]]"),

  h2("4.4 VERSÕES PARA COMPUTADOR"),
  p("A versão para computador oferece o mesmo motor, com a tela inicial organizada como um painel em " +
    "sete seções, na ordem em que ajudam a decidir o que fazer: hoje, memória, sistemas, onde focar, " +
    `autoavaliação, constância e marcos (Figura ${fig("desktop")}). O estudo por marcador tem as mesmas ` +
    "cinco abas da versão móvel.", { manterComProximo: true }),
  ...figura("desktop", path.join(FIG, "desktop_painel.png"), "Painel inicial da versão para computador",
    "elaborado pelo autor (2026), com progresso de exemplo."),
  p("A versão com tutor acrescenta uma conversa sobre cada marcador, questões geradas por um modelo de " +
    "linguagem executado localmente com o Ollama e a discussão de casos clínicos. Por rodar no próprio " +
    "computador, o tutor não envia as perguntas do estudante a serviços externos. Quando não há modelo " +
    "instalado, o software avisa e passa a responder pela base local."),

  h2("4.5 IDENTIDADE VISUAL"),
  p("A logo combina um hexágono, que remete ao anel benzênico e à química, com uma gota, que remete à " +
    `amostra de sangue de onde vêm os marcadores (Figura ${fig("logo")}). Ela é gerada por um programa a partir de ` +
    "uma única geometria, que produz arquivos vetoriais (SVG), com o texto convertido em contornos, e " +
    "imagens PNG, nas variações horizontal, vertical, símbolo e negativa. O ícone e a tela de abertura " +
    "do aplicativo usam o mesmo símbolo.", { manterComProximo: true }),
  ...figura("logo", path.join(RAIZ, "assets", "logo", "horizontal.png"), "Logo do BioquímicaEDU",
    "elaborado pelo autor (2026).", { larguraCm: 10 }),

  h2("4.6 RESULTADOS DA AVALIAÇÃO COM USUÁRIOS"),
  p("[[PREENCHER: caracterização dos participantes — pode ser apresentada em tabela.]]"),
  p("[[PREENCHER: resultados do instrumento — médias, desvios-padrão e distribuição das respostas; " +
    "se for usada escala de usabilidade, o escore médio e sua interpretação.]]"),
  p("[[PREENCHER: comentários abertos mais frequentes, com exemplos.]]"),

  h2("4.7 EVOLUÇÃO DO SOFTWARE APÓS A AVALIAÇÃO"),
  p("Depois da avaliação com usuários, o software continuou a ser desenvolvido. As mudanças são " +
    "descritas aqui, separadas das seções anteriores, porque os participantes usaram a versão " +
    "apresentada nas seções 4.1 a 4.5 [[CONFIRMAR: versão usada na avaliação]] e porque elas não foram " +
    "avaliadas com usuários. Quatro frentes foram tratadas: os intervalos da revisão, que não " +
    "diferenciavam de imediato as avaliações “Difícil”, “Bom” e “Fácil”; a existência de uma interface " +
    "diferente para cada aparelho; a acessibilidade, que ainda não havia sido tratada de forma " +
    "sistemática; e o tutor, que passou a contar, como opção, com um modelo de linguagem em nuvem. A " +
    "tela de abertura, a apresentação do primeiro acesso e a identidade visual também foram completadas. " +
    `Com essas mudanças, o código-fonte passou de ${fmt(M.codigo_total)} para ${fmt(ME.codigo_total)} ` +
    "linhas não vazias, excluídos os comentários."),

  h3("4.7.1 Intervalos da revisão"),
  p("Na versão avaliada, “Difícil”, “Bom” e “Fácil” levavam ao mesmo próximo intervalo depois do " +
    "primeiro contato (seção 4.2). Na versão atual, cada avaliação leva a um intervalo diferente já no " +
    "agendamento seguinte. No primeiro acerto, os intervalos são de 1, 2 e 4 dias; no segundo, de 4, 6 e " +
    "8 dias, isto é, o intervalo de 6 dias do SM-2 multiplicado por 0,6, 1,0 e 1,3. A partir do terceiro " +
    "acerto, “Bom” mantém a regra do SM-2 — o intervalo anterior multiplicado pelo fator de facilidade —, " +
    "“Difícil” multiplica o intervalo anterior por 1,2 e “Fácil” multiplica o intervalo de “Bom” por 1,3, " +
    "os valores padrão do Anki para essas avaliações (Anki, [2026]). Os intervalos são arredondados para " +
    "dias inteiros, mantêm a ordem “Difícil” < “Bom” < “Fácil” e não passam de 365 dias. A nota enviada " +
    "ao SM-2 e o ajuste do fator de facilidade pela Equação 1 não mudaram. A Tabela 4 compara as duas " +
    "versões para um marcador avaliado com “Bom” em todas as revisões anteriores.",
    { manterComProximo: true }),
  ...tabela("Próximo intervalo, em dias, conforme a avaliação, nas duas versões do motor", COLUNAS_INTERVALOS,
    Object.keys(SM2E.atual).map((n) => [ROTULO_REVISAO[n], trio(SM2E.avaliada[n]), trio(SM2E.atual[n])]),
    "elaborado pelo autor (2026), executando o código do motor (progresso.py) da versão avaliada e da atual."),
  p("Com isso, a escolha do estudante passa a ter consequência visível no próprio botão, que já " +
    `mostrava, antes do toque, quando o marcador voltaria (Figura ${fig("evolucao_formatos")}c, na seção ` +
    "4.7.2). A sequência em que todas as respostas são “Bom” mudou apenas no primeiro intervalo, de 1 " +
    "para 2 dias."),

  h3("4.7.2 Um aplicativo para celular, tablet e computador"),
  p("Na versão avaliada, o computador tinha duas interfaces em Tkinter, e o celular, uma em Kivy " +
    "(Quadro 3), o que obrigava a manter interfaces separadas para o mesmo conteúdo, com aparência e " +
    "recursos diferentes entre os aparelhos. Como a interface em Kivy também " +
    "roda no computador, ela passou a ser a única: o comando python main.py abre o mesmo aplicativo no " +
    "computador, e as versões em Tkinter continuam disponíveis pela opção --classico. Para isso, a " +
    "interface passou a se adaptar à largura da janela, medida em pixels independentes de densidade " +
    "(dp), unidade que mantém o tamanho físico aproximado dos elementos em telas de densidades " +
    "diferentes. As faixas seguem as classes de tamanho de janela recomendadas para o Android (Android " +
    "Developers, [2026b]), como resume o Quadro 5.", { manterComProximo: true }),
  ...quadro("Adaptação da interface à largura da janela", COLUNAS_FORMATOS, [
    ["Compacto", "menos de 600 dp", "celular", "barra inferior com cinco abas", "uma coluna"],
    ["Médio", "de 600 a 839 dp", "tablet em pé", "menu lateral", "uma coluna; lista de marcadores em até duas"],
    ["Expandido", "840 dp ou mais", "tablet deitado e computador", "menu lateral",
      "tela inicial em até duas colunas; lista de marcadores em até três"],
  ], "elaborado pelo autor (2026), com as faixas de Android Developers ([2026b])."),
  p("Telas de leitura contínua, como a revisão, os ~flashcards~ e o tutor, ficam numa coluna central de " +
    "largura limitada, para que as linhas não se estendam por toda a tela. Ao redimensionar a janela, o " +
    "aplicativo troca de formato sem perder a tela aberta nem uma sessão de revisão em andamento, o que é " +
    "conferido pelos testes automatizados. No Android, a configuração pede a orientação retrato, mas, a " +
    "partir do Android 16, o sistema ignora restrições de orientação em telas cuja menor largura é de " +
    "600 dp ou mais (Android Developers, [2026a]); por isso, o formato do tablet deitado também foi " +
    "verificado."),
  p("Os formatos se complementam no uso. O agendamento espaçado pede sessões curtas e frequentes, que " +
    "cabem no celular, em qualquer intervalo do dia; o computador e o tablet favorecem o estudo mais " +
    "longo — a leitura do detalhe de cada marcador, os casos clínicos e as conversas com o tutor —, com " +
    "mais informação visível ao mesmo tempo. Como o conteúdo, o motor de aprendizagem e a interface são " +
    "os mesmos, o estudante encontra as mesmas telas e as mesmas regras em qualquer aparelho. Hoje, porém, " +
    "cada aparelho guarda o próprio progresso; a sincronização opcional, por meio da conta Google, está " +
    "em desenvolvimento. [[CONFIRMAR: atualizar se a sincronização for concluída antes da entrega.]] " +
    `A Figura ${fig("evolucao_formatos")} mostra o aplicativo nos três formatos.`,
    { manterComProximo: true }),
  ...figura("evolucao_formatos", path.join(FIG, "evolucao_formatos.png"),
    "O mesmo aplicativo no computador, no tablet e no celular",
    "elaborado pelo autor (2026), com progresso de exemplo.",
    { nota: "(a) computador, com a tela inicial em duas colunas e o menu lateral; (b) tablet em pé, com a " +
            "lista de marcadores em duas colunas; (c) celular, com a revisão depois da resposta e os novos " +
            "intervalos nos botões de autoavaliação." }),

  h3("4.7.3 Acessibilidade"),
  p("A Lei Brasileira de Inclusão da Pessoa com Deficiência inclui a informação e a comunicação, com " +
    "seus sistemas e tecnologias, entre o que deve ser acessível (Brasil, 2015). No BioquímicaEDU, os " +
    "recursos de acessibilidade foram reunidos numa tela própria, aberta pelo ícone no topo da tela " +
    "inicial e oferecida ao fim da apresentação do primeiro acesso, para que quem precisa deles não tenha " +
    "de percorrer o aplicativo até encontrá-los. Eles funcionam da mesma forma no celular, no tablet e no " +
    `computador (Figura ${fig("evolucao_acessibilidade")}):`, { manterComProximo: true }),
  ...alineas([
    "tamanho do texto em quatro níveis, até 150%, com os componentes reorganizados para que nenhum " +
      "texto seja cortado;",
    "tema de alto contraste, com texto preto sobre fundo branco e bordas no lugar de sombras;",
    "fonte Atkinson Hyperlegible, opcional, criada pelo Braille Institute para leitores com baixa visão, " +
      "com letras e números de formas bem distintas (Braille Institute, [2026]);",
    "leitura em voz alta do conteúdo, com a voz do próprio sistema e três velocidades;",
    "atalho para o VLibras, tradutor gratuito de português para Libras mantido pelo Governo Federal " +
      "(Brasil, [2026]): o aplicativo copia o texto e abre o VLibras no celular, ou a página dele no " +
      "computador, onde basta colar o texto;",
    "modo foco, que reduz a tela inicial ao essencial, sessões de revisão de 5, 12 ou 20 itens e opção " +
      "para reduzir as animações.",
  ]),
  ...figura("evolucao_acessibilidade", path.join(FIG, "evolucao_acessibilidade.png"),
    "Recursos de acessibilidade na versão para celular",
    "elaborado pelo autor (2026), com progresso de exemplo.",
    { nota: "(a) tela de acessibilidade; (b) detalhe de um marcador com alto contraste, texto a 130% e a " +
            "fonte Atkinson Hyperlegible, com os botões de ouvir e de Libras; (c) tela inicial no modo foco." }),
  p("As cores de texto dos dois temas foram conferidas pela razão de contraste definida nas diretrizes " +
    "WCAG 2.2: todas as combinações de texto e fundo usadas atingem pelo menos 4,5:1, o mínimo do nível " +
    "AA (World Wide Web Consortium, 2024); a menor é de 4,79:1 no tema padrão e de 6,78:1 no de alto " +
    "contraste. Botões e chips têm área de toque de pelo menos 44 dp. A leitura em voz alta existe porque " +
    "o Kivy não se integra a leitores de tela, como o TalkBack, do Android: em vez de depender deles, o " +
    "próprio aplicativo lê o conteúdo, com o serviço de voz do Android ou, no Windows, com a voz do " +
    "sistema. O VLibras, por sua vez, não oferece integração direta para aplicativos nativos; por isso, o " +
    "atalho leva o texto pela área de transferência."),

  h3("4.7.4 Tutor com inteligência artificial generativa"),
  p("Na versão avaliada, o tutor do celular respondia apenas pela base do aplicativo, e o do computador " +
    "podia usar um modelo de linguagem local, executado com o Ollama (seção 4.4). Modelos locais, porém, " +
    "não rodam no celular e, nos tamanhos que cabem num computador comum, tendem a responder mais devagar " +
    "e com qualidade inferior à de modelos maiores. O tutor passou a aceitar, como opção, o Gemini, " +
    "modelo de linguagem do Google acessado pela internet (Google, [2026b]). Os provedores de resposta são " +
    "tentados em ordem — Gemini, modelo local e base do aplicativo —, e a base, que sempre responde, é a " +
    `reserva de todos (Figura ${fig("tutor_arquitetura")}).`, { manterComProximo: true }),
  ...figura("tutor_arquitetura", path.join(FIG, "tutor_arquitetura.png"),
    "Provedores de resposta do tutor e local da chave de acesso",
    "elaborado pelo autor (2026)."),
  p("A principal decisão foi manter o conteúdo curado como fonte da verdade. A cada pergunta, o tutor " +
    "envia ao modelo uma instrução fixa e as fichas dos 20 marcadores do aplicativo — faixa de " +
    "referência, interpretação e condições associadas —, com o marcador da pergunta em destaque, além das " +
    "últimas seis mensagens da conversa. A instrução determina que valores e interpretações venham somente " +
    "desses dados, que o modelo não faça diagnóstico nem indique conduta para pacientes reais e que " +
    "ignore pedidos para mudar as regras. Assim, o tutor pode explicar mecanismos, comparar marcadores e " +
    "responder a perguntas de continuidade, como “e quando está baixo?”, sem se afastar do conteúdo " +
    "curado. A temperatura de geração foi fixada em 0,3, para respostas mais estáveis."),
  p("A chave de acesso à API do Gemini dá acesso à conta de quem a criou e, por isso, não fica no " +
    "código-fonte nem no pacote do aplicativo, de onde poderia ser extraída. No computador, ela é lida de " +
    "um arquivo local excluído do controle de versões; no celular, o aplicativo não tem chave e envia a " +
    "pergunta a um servidor intermediário, executado no Cloudflare Workers, que guarda a chave como " +
    "segredo e aplica a mesma instrução fixa (Cloudflare, [2026]). Só são aceitas conexões criptografadas " +
    "(HTTPS). Essa é a única função que exige acesso à internet no Android, e a permissão só precisa ser " +
    "incluída no pacote quando o servidor é configurado."),
  p("O projeto usa a camada gratuita da API, adequada a demonstrações. Nela, o Google pode usar as " +
    "perguntas e respostas para melhorar seus produtos, com possibilidade de revisão humana, e os termos " +
    "pedem que não se enviem informações pessoais ou sensíveis; na camada paga, os dados não são usados " +
    "para esse fim (Google, [2026a]). Por isso, o tutor avisa o estudante antes da primeira pergunta. Os " +
    "termos também exigem que os usuários tenham pelo menos 18 anos, o que é compatível com o público de " +
    "graduação, mas precisaria ser garantido num uso em produção. Quando o Gemini não responde — por " +
    "falta de internet, limite de uso da camada gratuita, chave recusada ou bloqueio pelo filtro de " +
    "segurança —, o tutor informa o motivo em linguagem simples e responde pela base."),
  p("Esse comportamento é verificado por um programa de testes que substitui a conexão com o Google por " +
    "uma simulada: ele confere o conteúdo enviado, a leitura das respostas, cada tipo de falha, o caminho " +
    "do celular, a igualdade entre as instruções do aplicativo e do servidor e a ausência de chaves de API " +
    "nos arquivos do projeto." +
    (TEM_FIGURA_TUTOR ? ` A Figura ${fig("evolucao_tutor")} mostra uma conversa real com o tutor.` : ""),
    { manterComProximo: TEM_FIGURA_TUTOR }),
  ...(TEM_FIGURA_TUTOR
    ? figura("evolucao_tutor", path.join(FIG, "evolucao_tutor.png"),
        "Conversa com o tutor usando o Gemini na versão para celular",
        `elaborado pelo autor (2026). Respostas geradas pelo modelo ${TUTOR.modelo} em ` +
          `${dataAbnt(TUTOR.data)}, sem edição.`,
        { nota: "(a) início da conversa, com o aviso sobre a camada gratuita; (b) resposta a uma pergunta " +
                "de comparação; (c) resposta a uma pergunta de continuidade." })
    : [p("[[PREENCHER: figura com uma conversa real com o tutor usando o Gemini — gerada por " +
         "relatorio/gerar_figuras.py depois que a chave for configurada (docs/TUTOR_GEMINI.md).]]")]),

  h3("4.7.5 Abertura, apresentação e identidade visual"),
  p("Por fim, o aplicativo ganhou uma tela de abertura com a logo, exibida enquanto o conteúdo e o " +
    "progresso são carregados, que, se a leitura dos dados falhar, explica o problema e oferece nova " +
    "tentativa; uma apresentação de três passos no primeiro acesso, que termina nos ajustes de " +
    "acessibilidade; e as variações da identidade visual de que um aplicativo precisa, como o ícone " +
    "adaptativo do Android, que se ajusta ao formato de ícone de cada aparelho."),
];

const discussao = [
  h1("5 DISCUSSÃO"),
  p("O SM-2 foi escolhido por ser simples, publicado e auditável: cada intervalo pode ser explicado ao " +
    "estudante a partir de regras curtas, e o comportamento do motor pode ser conferido à mão, como na " +
    `Figura ${fig("sm2")}. As adaptações não pretenderam melhorar a previsão de esquecimento do algoritmo, mas ` +
    "integrar ao mesmo agendamento atividades de natureza diferente — revisão, ~flashcards~, quiz e casos " +
    "— e manter as sessões curtas. O efeito dessas adaptações sobre a retenção não foi medido neste " +
    "trabalho. Na versão avaliada, depois do primeiro contato, “Difícil”, “Bom” e “Fácil” mostravam o " +
    "mesmo próximo intervalo, o que podia fazer a autoavaliação graduada parecer sem efeito. A versão " +
    "atual diferencia os intervalos já no agendamento seguinte (seção 4.7.1), com os multiplicadores " +
    "padrão do Anki para “Difícil” e “Fácil”; esses valores não foram calibrados com dados de estudantes " +
    "do próprio software, o que exigiria acompanhar o desempenho por meses."),
  p("A ausência deliberada de pontos, medalhas e classificações segue a evidência discutida na seção " +
    "2.4: recompensas esperadas podem reduzir a motivação intrínseca (Deci; Koestner; Ryan, 1999), e " +
    "medalhas e classificações não melhoraram o desempenho em turmas ~online~ (Balci; Secaur; Morris, " +
    "2022). Os números exibidos medem memória e domínio, funcionando como ~feedback~ de competência, e os " +
    "marcos correspondem a algo que o estudante passou a saber. Há, porém, evidência de que gamificação " +
    "baseada em desafios pode elevar desempenho e motivação (Kaya; Ercag, 2023), de modo que a escolha " +
    "por um painel informativo pode ter custo em engajamento — questão a ser examinada com usuários. " +
    "[[PREENCHER: relacionar com os resultados da avaliação, se houver dados sobre motivação.]]"),
  p("O registro de calibração torna visível uma diferença que, segundo a literatura, o estudante tende a " +
    "não perceber sozinho (Kruger; Dunning, 1999; Cleary ~et al.~, 2019). Como a má calibração de " +
    "estudantes de baixo desempenho se mostrou estável mesmo diante de notas anteriores (Karaca ~et al.~, " +
    "2023), uma devolutiva explícita e frequente pode ajudar, mas esse efeito também precisa ser " +
    "investigado."),
  p("Quanto à privacidade, todos os dados do estudante ficam no aparelho, não há cadastro e a versão " +
    "móvel não solicita acesso à internet. A escolha está alinhada ao princípio da necessidade da Lei " +
    "Geral de Proteção de Dados Pessoais (LGPD), que limita o tratamento ao mínimo necessário para sua " +
    "finalidade (Brasil, 2018). O custo é a falta de sincronização: o progresso no celular e no " +
    "computador é independente. Na versão atual, isso continua valendo enquanto o tutor com Gemini não é " +
    "usado. Quando é, a pergunta e o conteúdo curado saem do aparelho para um serviço externo, e a camada " +
    "gratuita permite ao Google usá-los para melhorar seus produtos (Google, [2026a]). O aviso ao " +
    "estudante e o fato de o aplicativo não enviar nenhuma identificação dele reduzem esse risco, mas não " +
    "o eliminam, porque o estudante pode digitar dados pessoais na pergunta; fora de demonstrações, a " +
    "camada paga seria a escolha adequada. A sincronização pela conta Google, por sua vez, trará dados " +
    "pessoais, como nome e e-mail, e exigirá base legal, aviso de privacidade e consentimento, nos termos " +
    "da LGPD."),
  p("Os recursos de acessibilidade seguem critérios verificáveis, como a razão mínima de contraste da " +
    "WCAG 2.2, mas a falta de integração do Kivy com leitores de tela é uma limitação estrutural: a " +
    "leitura em voz alta do próprio aplicativo atende a quem prefere ouvir o conteúdo, mas não substitui a " +
    "navegação por leitor de tela de que dependem pessoas cegas. Uma aplicação web instalável, que tem " +
    "acesso às tecnologias assistivas do sistema e permitiria integrar o VLibras à própria página, é uma " +
    "alternativa para uma próxima fase, com reaproveitamento do motor de aprendizagem e do conteúdo."),
  p("No tutor, ancorar o modelo de linguagem no conteúdo curado reduz a chance de valores de referência " +
    "inventados, mas não a elimina, e a qualidade das explicações não foi avaliada. Antes de recomendar o " +
    "recurso para estudo autônomo, seria necessário que docentes da área da saúde avaliassem as respostas " +
    "a um conjunto representativo de perguntas."),
  p("O trabalho tem limitações. O conteúdo cobre 20 marcadores, e o banco de 12 questões é pequeno, o " +
    "que favorece a repetição das mesmas perguntas. As questões geradas pelo modelo de linguagem na " +
    "versão com tutor não passam por curadoria e podem conter erros. A versão para iOS, possível com o " +
    "Kivy, não foi testada. Os recursos acrescentados depois da avaliação (seção 4.7) não foram testados " +
    "com usuários, em particular com estudantes com deficiência. Por fim, a avaliação [[PREENCHER: limitações da avaliação — tamanho e perfil " +
    "da amostra, duração do uso]], e o efeito do software sobre a retenção de longo prazo exigiria um " +
    "estudo longitudinal."),
];

const consideracoes = [
  h1("6 CONSIDERAÇÕES FINAIS"),
  p("Este trabalho desenvolveu o BioquímicaEDU, software educacional para o estudo de marcadores " +
    "bioquímicos baseado em prática de recuperação, repetição espaçada e registro de calibração. Em " +
    `relação aos objetivos, foram reunidos conteúdos sobre ${C.marcadores} marcadores com fontes verificáveis; foi ` +
    "implementado um motor de aprendizagem que agenda as revisões com uma adaptação do SM-2 e integra " +
    "revisão, ~flashcards~, quiz e casos clínicos; a confiança declarada pelo estudante passou a ser " +
    "comparada com seu desempenho; e o software foi disponibilizado em versões para computador e para " +
    "dispositivos móveis, com os dados mantidos no aparelho. [[PREENCHER: o que a avaliação com " +
    "usuários permitiu concluir sobre o último objetivo.]]"),
  p("Depois da avaliação, o software foi unificado num único aplicativo, que se adapta ao celular, ao " +
    "tablet e ao computador e cujos formatos se complementam no estudo; ganhou recursos de " +
    "acessibilidade — texto ampliado, alto contraste, fonte para baixa visão, leitura em voz alta e " +
    "atalho para Libras —; passou a diferenciar os intervalos de “Difícil”, “Bom” e “Fácil”; e recebeu, " +
    "como opção, um tutor com inteligência artificial generativa ancorado no conteúdo curado, com a chave " +
    "de acesso mantida fora do aplicativo."),
  p("Como trabalhos futuros, sugerem-se: ampliar o número de marcadores e de questões, com revisão por " +
    "docentes da área da saúde; realizar estudo longitudinal que compare a retenção com e sem o " +
    "agendamento espaçado; publicar a versão móvel na Google Play, após testes em diferentes aparelhos; " +
    "concluir a sincronização opcional entre aparelhos pela conta Google, mediante consentimento " +
    "explícito; avaliar os recursos de acessibilidade com estudantes com deficiência e a qualidade das " +
    "respostas do tutor com docentes; e testar a versão para iOS."),
];

const referencias = [
  h1("REFERÊNCIAS", { centro: true }),
  ...REFERENCIAS.map(referencia),
];

const COLUNAS_APENDICE = [
  { titulo: "Marcador", largura: 2700 },
  { titulo: "Sistema", largura: 1500 },
  { titulo: "Fontes consultadas", largura: 4870 },
];

const apendices = [
  h1("APÊNDICE A – FONTES DO CONTEÚDO POR MARCADOR", { centro: true }),
  p("O quadro abaixo relaciona cada marcador às fontes indicadas no software, na aba “Fontes” do " +
    "detalhe. As referências completas estão na lista de referências.", { manterComProximo: true }),
  ...quadro("Fontes bibliográficas de cada marcador", COLUNAS_APENDICE,
    MARCADORES.map((m) => [`${m.nome} (${m.sigla})`, m.categoria, fontesDoMarcador(m.sigla)]),
    "elaborado pelo autor (2026), a partir de data/marcadores_extras.json."),

  h1("APÊNDICE B – CÓDIGO-FONTE E EXECUÇÃO", { centro: true }),
  p(`O código-fonte, os dados e este relatório estão em ${REPOSITORIO}. As versões são iniciadas pelos ` +
    "comandos abaixo, executados na pasta do projeto com Python 3 instalado:", { manterComProximo: true }),
  ...alineas([
    "aplicativo para celular, tablet e computador: python main.py, após instalar o Kivy;",
    "o mesmo aplicativo em formato de celular: python main.py --celular;",
    "versão clássica para computador, em Tkinter: python main.py --classico;",
    "versão com tutor local: python main_enhanced.py (o Ollama é opcional);",
    "testes automatizados: python test_kivy_completo.py, python test_tutor.py e python test_desktop.py.",
  ]),
  p("O pacote Android é gerado com o Buildozer, a partir do arquivo buildozer.spec, conforme o guia " +
    "GUIA_MOBILE.md do repositório. O tutor com Gemini é configurado conforme docs/TUTOR_GEMINI.md, sem " +
    "que a chave de acesso entre no repositório. As figuras deste relatório são refeitas por " +
    "relatorio/gerar_figuras.py."),
];

// ════════════════════════════════════════════════════════════════════
// DOCUMENTO
// ════════════════════════════════════════════════════════════════════
const paginaBase = {
  size: { width: PAGINA.largura, height: PAGINA.altura },
  margin: { top: MARGEM.topo, bottom: MARGEM.base, left: MARGEM.esquerda, right: MARGEM.direita,
            header: 2 * CM, footer: CM },
};

const cabecalhoNumerado = new Header({
  children: [new Paragraph({
    alignment: AlignmentType.RIGHT,
    children: [new TextRun({ children: [PageNumber.CURRENT], size: 20 })],
  })],
});
const cabecalhoVazio = new Header({ children: [new Paragraph({ children: [] })] });

const doc = new Document({
  creator: "Alexandro de Araujo Junior",
  title: `${TITULO}: ${SUBTITULO}`,
  description: "Relatório final PIBIC/CNPq — UNICID",
  language: "pt-BR",
  styles: estilos,
  numbering: numeracao,
  sections: [
    { // capa: não conta na numeração
      properties: { page: paginaBase, verticalAlign: VerticalAlignSection.BOTH },
      headers: { default: cabecalhoVazio },
      children: capa,
    },
    { // folha de rosto: primeira folha contada
      properties: { type: SectionType.NEXT_PAGE, page: { ...paginaBase, pageNumbers: { start: 1 } },
                    verticalAlign: VerticalAlignSection.BOTH },
      headers: { default: cabecalhoVazio },
      children: folhaDeRosto,
    },
    { // demais pré-textuais: contadas, sem número visível
      properties: { type: SectionType.NEXT_PAGE, page: paginaBase },
      headers: { default: cabecalhoVazio },
      children: [
        ...agradecimentos, ...resumo, ...abstract,
        ...listaDe("LISTA DE FIGURAS", "Figura"),
        ...listaDe("LISTA DE QUADROS", "Quadro"),
        ...listaDe("LISTA DE TABELAS", "Tabela"),
        ...listaSiglas, ...sumario,
      ],
    },
    { // textuais e pós-textuais: número no canto superior direito
      properties: { type: SectionType.NEXT_PAGE, page: paginaBase },
      headers: { default: cabecalhoNumerado },
      children: [
        ...introducao, ...fundamentacao, ...metodos, ...resultados, ...discussao,
        ...consideracoes, ...referencias, ...apendices,
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(SAIDA, buf);
  console.log("gerado:", SAIDA, `(${(buf.length / 1024).toFixed(0)} KB)`);
});
