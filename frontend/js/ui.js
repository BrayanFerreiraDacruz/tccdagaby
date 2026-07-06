// Utilitários de UI compartilhados: layout do app, guarda de autenticação,
// toasts, ícones SVG e helpers. Usado por todas as páginas internas.

// ---- Biblioteca de ícones (SVG traço, herdam a cor via currentColor) ----
const ICON_PATHS = {
  dashboard:
    '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>',
  questions:
    '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M9 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-3"/><path d="m9 14 2 2 4-4"/>',
  calendar:
    '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
  chart: '<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6" rx="1"/><rect x="12" y="8" width="3" height="10" rx="1"/><rect x="17" y="5" width="3" height="13" rx="1"/>',
  book: '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
  settings:
    '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>',
  check: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/>',
  x: '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/>',
  target:
    '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
  trending: '<path d="M22 7 13.5 15.5l-5-5L2 17"/><path d="M16 7h6v6"/>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="m9 12 2 2 4-4"/>',
  devices:
    '<rect x="2" y="3" width="14" height="12" rx="2"/><path d="M2 15h14M8 19h4"/><rect x="17" y="9" width="5" height="12" rx="1.5"/>',
  logout:
    '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5M21 12H9"/>',
  home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>',
  login: '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><path d="m10 17 5-5-5-5M15 12H3"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  video:
    '<rect x="2" y="6" width="14" height="12" rx="2"/><path d="m16 10 6-3.5v11L16 14z"/>',
  pen: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
  key: '<circle cx="7.5" cy="15.5" r="4.5"/><path d="m10.5 12.5 8-8M17 4l3 3M15 6l3 3"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
  alert:
    '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/>',
  party:
    '<path d="M22 12 3 21l4-9-4-9z"/><path d="M12 3v4M17 6l-2 2M7 6l2 2"/>',
};

function icon(name, size = 20) {
  const path = ICON_PATHS[name] || "";
  return `<svg class="ic-svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${path}</svg>`;
}

const NAV_ITEMS = [
  { href: "dashboard.html", icon: "dashboard", label: "Painel" },
  { href: "questoes.html", icon: "questions", label: "Questões" },
  { href: "cronograma.html", icon: "calendar", label: "Cronograma" },
  { href: "desempenho.html", icon: "chart", label: "Desempenho" },
  { href: "materiais.html", icon: "book", label: "Materiais" },
  { href: "conta.html", icon: "settings", label: "Conta" },
];

// Redireciona para login se não autenticado.
function requireAuth() {
  if (!Session.isLogged) {
    location.href = "auth.html";
    return false;
  }
  return true;
}

function brandMarkup() {
  return `<span class="brand-logo">${icon("clock", 22)}</span> Study<span>Time</span>`;
}

function navLinks(activeHref) {
  return NAV_ITEMS.map(
    (i) => `
    <a href="${i.href}" class="side-link ${i.href === activeHref ? "active" : ""}">
      <span class="ic">${icon(i.icon)}</span>
      <span class="lbl">${i.label}</span>
    </a>`
  ).join("");
}

// Monta o app shell (sidebar + topo mobile) na página.
function renderShell(activeHref) {
  const user = Session.user || { name: "Estudante", email: "" };
  const initials = (user.name || "E")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  const sidebar = `
    <aside class="sidebar">
      <a href="dashboard.html" class="brand">${brandMarkup()}</a>
      <p class="side-label">Menu</p>
      <nav class="side-nav">${navLinks(activeHref)}</nav>
      <div class="side-user">
        <div class="avatar">${initials}</div>
        <div class="info">
          <b>${esc(user.name)}</b>
          <span>${esc(user.email)}</span>
        </div>
      </div>
      <button class="btn btn-ghost btn-block btn-sm" onclick="logout()">
        ${icon("logout", 18)} Sair
      </button>
    </aside>`;

  const mobile = `
    <div class="mobile-nav">
      <a href="dashboard.html" class="brand">${brandMarkup()}</a>
      <button class="menu-btn" aria-label="Abrir menu"
        onclick="document.getElementById('drawer').classList.toggle('open')">
        ${icon("menu", 22)}
      </button>
    </div>
    <div class="mobile-drawer" id="drawer">
      ${navLinks(activeHref)}
      <button class="btn btn-ghost btn-sm" onclick="logout()">${icon("logout", 18)} Sair</button>
    </div>`;

  document.getElementById("shell").innerHTML = sidebar;
  const mob = document.getElementById("mobile-shell");
  if (mob) mob.innerHTML = mobile;
}

function logout() {
  Session.clear();
  location.href = "index.html";
}

// ---- Toast ----
function toast(message, type = "") {
  let wrap = document.querySelector(".toast-wrap");
  if (!wrap) {
    wrap = document.createElement("div");
    wrap.className = "toast-wrap";
    document.body.appendChild(wrap);
  }
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  wrap.appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transition = "opacity .3s";
    setTimeout(() => el.remove(), 300);
  }, 3200);
}

// Escapa HTML para evitar injeção ao renderizar conteúdo de texto.
function esc(str) {
  const d = document.createElement("div");
  d.textContent = str == null ? "" : String(str);
  return d.innerHTML;
}

// Converte markdown de imagem ![](url) e quebras em HTML seguro (contexto ENEM).
function renderContext(text) {
  if (!text) return "";
  let html = esc(text);
  html = html.replace(
    /!\[[^\]]*\]\((https?:\/\/[^\s)]+)\)/g,
    '<img src="$1" alt="figura da questão" loading="lazy">'
  );
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  return html;
}

const WEEKDAYS = [
  "Domingo",
  "Segunda",
  "Terça",
  "Quarta",
  "Quinta",
  "Sexta",
  "Sábado",
];
const WEEKDAYS_SHORT = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

window.icon = icon;

// Preenche ícones em elementos estáticos: <span data-ic="chart" data-ic-size="40">
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-ic]").forEach((el) => {
    el.innerHTML = icon(el.dataset.ic, parseInt(el.dataset.icSize || "40", 10));
  });
});
