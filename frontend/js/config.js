// Configuração global do frontend Study Time.
// A API é servida pelo mesmo domínio (Flask serve o frontend), então usamos
// caminho relativo. Para desenvolvimento separado, altere para a URL do backend.
window.STUDYTIME = {
  API_BASE: "/api",
  TOKEN_KEY: "studytime_token",
  USER_KEY: "studytime_user",
};

// Injeta o favicon (logo) em todas as páginas.
(function () {
  if (document.querySelector('link[rel="icon"]')) return;
  var l = document.createElement("link");
  l.rel = "icon";
  l.type = "image/png";
  l.href = "assets/favicon.png";
  document.head.appendChild(l);
})();
