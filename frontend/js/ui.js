// Utilitários de UI compartilhados: layout do app, guarda de autenticação,
// toasts e helpers. Usado por todas as páginas internas.

const NAV_ITEMS = [
  { href: "dashboard.html", icon: "🏠", label: "Painel" },
  { href: "questoes.html", icon: "📝", label: "Questões" },
  { href: "cronograma.html", icon: "📅", label: "Cronograma" },
  { href: "desempenho.html", icon: "📊", label: "Desempenho" },
  { href: "materiais.html", icon: "📚", label: "Materiais" },
  { href: "conta.html", icon: "⚙️", label: "Conta" },
];

// Redireciona para login se não autenticado.
function requireAuth() {
  if (!Session.isLogged) {
    location.href = "auth.html";
    return false;
  }
  return true;
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

  const links = NAV_ITEMS.map(
    (i) => `
    <a href="${i.href}" class="side-link ${
      i.href === activeHref ? "active" : ""
    }">
      <span class="ic">${i.icon}</span> ${i.label}
    </a>`
  ).join("");

  const sidebar = `
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-logo">⏱️</span> Study<span>Time</span>
      </div>
      <nav class="side-nav">${links}</nav>
      <div>
        <div class="side-user">
          <div class="avatar">${initials}</div>
          <div class="info">
            <b>${user.name}</b>
            <span>${user.email}</span>
          </div>
        </div>
        <button class="btn btn-ghost btn-block btn-sm" style="margin-top:.8rem"
          onclick="logout()">Sair</button>
      </div>
    </aside>`;

  const mobile = `
    <div class="mobile-nav">
      <div class="brand"><span class="brand-logo">⏱️</span> Study<span>Time</span></div>
      <button class="menu-btn" onclick="document.getElementById('drawer').classList.toggle('open')">☰</button>
    </div>
    <div class="mobile-drawer" id="drawer">
      ${links}
      <button class="btn btn-ghost btn-sm" onclick="logout()">Sair</button>
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
