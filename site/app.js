/*
 * Preenche os botões de download a partir de config.js e destaca a versão
 * certa para o aparelho de quem visita. Sem JavaScript, os botões levam à
 * seção "Baixar", que explica tudo.
 */
(function () {
  "use strict";
  var cfg = window.BIOQ || {};

  // versão, data e links
  document.querySelectorAll("[data-info]").forEach(function (el) {
    var valor = cfg[el.getAttribute("data-info")];
    if (valor) el.textContent = valor;
  });
  document.querySelectorAll("[data-link]").forEach(function (el) {
    var valor = cfg[el.getAttribute("data-link")];
    if (valor) el.href = valor;
  });

  // botões de download
  document.querySelectorAll("[data-download]").forEach(function (botao) {
    var plataforma = cfg[botao.getAttribute("data-download")];
    if (!plataforma) return;
    if (plataforma.publicado && plataforma.url) {
      botao.href = plataforma.url;
      botao.setAttribute("download", "");
      if (plataforma.tamanho && botao.classList.contains("botao--largo")) {
        var detalhe = document.createElement("span");
        detalhe.className = "botao__detalhe";
        detalhe.textContent = "(" + plataforma.tamanho + ")";
        botao.appendChild(detalhe);
      }
    } else if (botao.classList.contains("botao--largo")) {
      // no cartão de download, deixa claro que ainda não saiu
      botao.removeAttribute("href");
      botao.setAttribute("aria-disabled", "true");
      botao.setAttribute("role", "link");
      botao.textContent = "Em breve";
    }
  });

  // aviso do tutor enquanto o servidor de IA não está no ar
  if (!cfg.tutorComIA) {
    document.querySelectorAll('[data-se-tutor="desligado"]').forEach(function (el) { el.hidden = false; });
  }

  // destaca a versão para o aparelho de quem visita
  var ua = navigator.userAgent || "";
  var ios = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  var recomendada = /Android/.test(ua) ? "android" : (/Windows/.test(ua) ? "windows" : null);
  if (ios) {
    var aviso = document.getElementById("aviso-iphone");
    if (aviso) aviso.hidden = false;
  }
  if (recomendada) {
    var cartao = document.querySelector('.download[data-plataforma="' + recomendada + '"]');
    if (cartao) {
      cartao.classList.add("recomendado");
      var selo = document.createElement("span");
      selo.className = "download__selo";
      selo.textContent = "Para este aparelho";
      cartao.prepend(selo);
    }
  }
})();
