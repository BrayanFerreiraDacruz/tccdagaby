# ⏱️ Study Time — Plataforma auxiliar para estudos ENEM

Plataforma web **gratuita e acessível** para auxiliar estudantes do ensino médio
na preparação para o **ENEM** e vestibulares. Reúne, em um único ambiente,
**questões oficiais**, **cronograma de estudos personalizado**, **acompanhamento
de desempenho** e **materiais de apoio confiáveis**.

> Projeto Integrador — Curso Técnico em Informática Integrado ao Ensino Médio
> Alunas: **Gabrielly Wagner Groth** e **Naiara Fardo Riboldi**

---

## ✨ Funcionalidades

| Requisito | Funcionalidade |
|-----------|----------------|
| RF01–RF03 | Cadastro, login e gerenciamento de conta (editar dados / excluir) |
| RF04–RF06 | Criar, editar, excluir e visualizar cronogramas de estudo |
| RF07–RF09 | Resolver questões do ENEM e verificar respostas |
| RF08 | Integração com a **API oficial ENEM.dev** (2.700+ questões reais, 2009–2023) |
| RF10–RF11 | Registro de desempenho e visualização de progresso (com gráficos) |
| RF12 | Materiais de apoio de fontes oficiais (INEP/MEC, Khan Academy, etc.) |
| RF13 | Organização do tempo de estudo por dia da semana |

Todas as questões são **reais e oficiais**, obtidas da API pública
[ENEM.dev](https://enem.dev). Nenhum banco de questões é armazenado localmente —
o conteúdo está sempre atualizado.

---

## 🏗️ Arquitetura

Aplicação **cliente-servidor** (conforme definição do TCC):

```
tccStudyTime/
├── backend/                # API REST em Python + Flask (RS03)
│   ├── app.py              # ponto de entrada (também serve o frontend)
│   ├── config.py           # configuração + conexão MySQL/SQLite
│   ├── models.py           # modelos: User, Schedule, Attempt
│   ├── auth_utils.py       # autenticação JWT (RNF04)
│   ├── enem_client.py      # integração com a API ENEM.dev (RS05)
│   ├── routes/             # blueprints: auth, schedules, questions, ...
│   └── requirements.txt
└── frontend/               # HTML + CSS + JavaScript (RS02)
    ├── index.html          # página inicial (home)
    ├── auth.html           # login / cadastro
    ├── dashboard.html      # painel do usuário
    ├── questoes.html       # resolução de questões
    ├── cronograma.html     # cronograma de estudos
    ├── desempenho.html     # relatórios de desempenho
    ├── materiais.html      # materiais de apoio
    ├── conta.html          # gerenciamento de conta
    ├── css/style.css
    └── js/                 # config, api (Fetch API), ui
```

### Tecnologias
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API), Chart.js
- **Backend:** Python 3.10+ com Flask
- **Banco de dados:** MySQL (via XAMPP) — com *fallback* automático para SQLite
- **Integração:** API oficial ENEM.dev
- **Autenticação:** JWT + hash de senha (Werkzeug)

---

## 🌐 Publicar online (Hostinger)

O projeto tem **deploy automático**: cada `git push` publica o site no Hostinger
via **GitHub Actions (FTP)**. Para isso há uma versão do backend em **PHP**
(`frontend/api/`), que roda no Hostinger (PHP + MySQL), além do Flask.

Configuração única (segredos de FTP + banco): veja
**[DEPLOY-HOSTINGER.md](DEPLOY-HOSTINGER.md)**.

> O backend Flask/Python (`backend/`) permanece como implementação oficial do TCC.

## 🚀 Como executar (local, Flask)

### Pré-requisitos
- [Python 3.10+](https://www.python.org/downloads/) instalado
  (marque **“Add Python to PATH”** na instalação)
- [XAMPP](https://www.apachefriends.org/) com o **MySQL** ativo *(opcional —
  veja abaixo)*

### 1. Instalar as dependências
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar o ambiente
```bash
# copie o arquivo de exemplo e ajuste se necessário
cp .env.example .env      # (Windows PowerShell: Copy-Item .env.example .env)
```

O arquivo `.env` já vem pronto para o MySQL padrão do XAMPP
(`root` sem senha). **Se o MySQL não estiver disponível, o sistema usa SQLite
automaticamente** — ou seja, o projeto roda mesmo sem o XAMPP ligado.

### 3. Iniciar o servidor
```bash
python app.py
```

### 4. Acessar
Abra o navegador em **http://localhost:5000**

O Flask serve tanto a API quanto o frontend, então basta acessar essa URL.

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/register` | Cadastro de usuário |
| POST | `/api/auth/login` | Login |
| GET/PUT/DELETE | `/api/auth/me` | Consultar / editar / excluir conta |
| GET/POST | `/api/schedules` | Listar / criar cronograma |
| PUT/DELETE | `/api/schedules/<id>` | Editar / excluir bloco |
| GET | `/api/exams` | Provas disponíveis (ENEM.dev) |
| GET | `/api/questions` | Questões filtradas (ano, área, idioma) |
| POST | `/api/answer` | Verificar resposta e registrar desempenho |
| GET | `/api/performance/summary` | Resumo de desempenho |
| GET | `/api/performance/history` | Histórico de respostas |
| GET | `/api/materials` | Materiais de apoio |

> Por segurança, o gabarito das questões **não** é enviado ao frontend —
> a verificação da resposta acontece exclusivamente no backend.

---

## 🔒 Segurança (RNF04)
- Senhas armazenadas com **hash** (nunca em texto puro)
- Sessões autenticadas via **token JWT**
- Rotas privadas protegidas por *middleware* de autenticação
- Validação de dados no servidor

---

## 📚 Créditos das fontes
- Questões: [API ENEM.dev](https://enem.dev) — dados oficiais do ENEM
- Provas e cartilhas: [INEP / MEC](https://www.gov.br/inep)

---

## 📄 Licença
Projeto acadêmico desenvolvido para fins educacionais.
