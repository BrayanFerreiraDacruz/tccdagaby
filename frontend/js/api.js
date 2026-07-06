// Camada de acesso à API (Fetch API) + gestão de sessão do usuário.
const { API_BASE, TOKEN_KEY, USER_KEY } = window.STUDYTIME;

const Session = {
  get token() {
    return localStorage.getItem(TOKEN_KEY);
  },
  get user() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY));
    } catch {
      return null;
    }
  },
  set({ token, user }) {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  updateUser(user) {
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
  get isLogged() {
    return Boolean(this.token);
  },
};

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth && Session.token) {
    headers["Authorization"] = `Bearer ${Session.token}`;
  }

  let resp;
  try {
    resp = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error("Não foi possível conectar ao servidor. Ele está rodando?");
  }

  let data = null;
  try {
    data = await resp.json();
  } catch {
    /* resposta sem corpo */
  }

  if (resp.status === 401 && auth) {
    Session.clear();
    if (!location.pathname.includes("auth")) {
      location.href = "auth.html";
    }
  }

  if (!resp.ok) {
    throw new Error((data && data.error) || "Ocorreu um erro inesperado.");
  }
  return data;
}

const API = {
  // Autenticação
  register: (payload) =>
    request("/auth/register", { method: "POST", body: payload, auth: false }),
  login: (payload) =>
    request("/auth/login", { method: "POST", body: payload, auth: false }),
  me: () => request("/auth/me"),
  updateMe: (payload) => request("/auth/me", { method: "PUT", body: payload }),
  deleteMe: () => request("/auth/me", { method: "DELETE" }),

  // Cronograma
  listSchedules: () => request("/schedules"),
  createSchedule: (payload) =>
    request("/schedules", { method: "POST", body: payload }),
  updateSchedule: (id, payload) =>
    request(`/schedules/${id}`, { method: "PUT", body: payload }),
  deleteSchedule: (id) => request(`/schedules/${id}`, { method: "DELETE" }),

  // Questões (ENEM.dev)
  exams: () => request("/exams", { auth: false }),
  questions: (params) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/questions?${qs}`, { auth: false });
  },
  answer: (payload) => request("/answer", { method: "POST", body: payload }),

  // Desempenho
  summary: () => request("/performance/summary"),
  history: () => request("/performance/history"),

  // Materiais
  materials: () => request("/materials", { auth: false }),
};

window.API = API;
window.Session = Session;
