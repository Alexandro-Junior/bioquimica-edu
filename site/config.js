/*
 * Configuração do site do BioquímicaEDU: o único arquivo a editar quando
 * sair uma versão nova. Detalhes no README.md desta pasta.
 *
 * Os arquivos de instalação ficam na página de versões (Releases) do
 * GitHub, que não limita downloads de repositórios públicos; o plano
 * gratuito do Firebase Hosting, onde fica o site, permite só 360 MB de
 * tráfego por dia, o que acabaria em poucos downloads.
 */
window.BIOQ = {
  versao: "0.4",
  dataVersao: "outubro de 2026",

  // "publicado: false" mostra o botão como "Em breve", sem link.
  windows: {
    publicado: false,
    url: "https://github.com/Alexandro-Junior/bioquimica-edu/releases/latest/download/BioquimicaEDU-Windows.exe",
    tamanho: "",          // ex.: "62 MB"
  },
  android: {
    publicado: false,
    url: "https://github.com/Alexandro-Junior/bioquimica-edu/releases/latest/download/BioquimicaEDU-Android.apk",
    tamanho: "",
  },

  // true quando o servidor intermediário do tutor estiver no ar
  // (docs/TUTOR_GEMINI.md, parte 3 do repositório do app)
  tutorComIA: false,

  codigoFonte: "https://github.com/Alexandro-Junior/bioquimica-edu",
};
