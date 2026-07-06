# 🚀 Como publicar o Study Time no Hostinger

Este guia coloca a plataforma **completa e funcional** no seu domínio Hostinger
(ex.: `https://forestgreen-gorilla-581996.hostingersite.com/`).

A hospedagem compartilhada do Hostinger roda **PHP + MySQL**, então o deploy usa
a **versão PHP do backend** (pasta `frontend/api/`). O backend Flask/Python
(pasta `backend/`) continua no projeto para o TCC — ele não vai para o Hostinger.

> **Importante:** ninguém além de você consegue subir os arquivos, pois é
> necessário o login da sua conta Hostinger. Siga os passos abaixo — leva ~10 min.

---

## Passo 1 — Criar o banco de dados MySQL

1. Entre no **hPanel** → **Bancos de dados** → **Gerenciamento de bancos MySQL**.
2. Crie um **novo banco** (ex.: `studytime`). O Hostinger vai gerar nomes com
   prefixo, por exemplo:
   - Banco: `u123456789_studytime`
   - Usuário: `u123456789_admin`
   - Senha: *(a que você definir)*
3. **Anote** esses três valores — você vai usá-los no Passo 3.

*(Não precisa criar tabelas: o sistema cria sozinho na primeira execução.)*

---

## Passo 2 — Enviar os arquivos do site

Você vai subir **o conteúdo da pasta `frontend/`** para a pasta `public_html`.

**Opção A — Gerenciador de Arquivos (mais fácil):**
1. hPanel → **Arquivos** → **Gerenciador de Arquivos** → entre em `public_html`.
2. Faça upload do arquivo **`studytime-public_html.zip`** (está na raiz do projeto).
3. Clique com o botão direito no zip → **Extrair** (Extract) dentro de `public_html`.
4. Apague o `.zip` depois de extrair.

O `public_html` deve ficar assim:
```
public_html/
├── index.html
├── auth.html
├── dashboard.html   (e demais .html)
├── css/  js/  assets/
└── api/             ← backend PHP
```

**Opção B — Git (se preferir):**
No hPanel → **Avançado** → **Git**, conecte o repositório
`https://github.com/BrayanFerreiraDacruz/tccdagaby.git` e defina o diretório de
deploy. Depois mova o conteúdo de `frontend/` para dentro de `public_html`.

---

## Passo 3 — Configurar a conexão com o banco

1. No Gerenciador de Arquivos, abra `public_html/api/config.php` (botão direito →
   **Editar**).
2. Preencha com os dados do Passo 1:
   ```php
   define('DB_HOST', 'localhost');
   define('DB_NAME', 'u123456789_studytime');
   define('DB_USER', 'u123456789_admin');
   define('DB_PASS', 'sua_senha_do_banco');
   ```
3. Troque também a `JWT_SECRET` por uma frase longa e aleatória (qualquer texto
   grande e único).
4. Salve.

---

## Passo 4 — Testar

1. Acesse `https://SEU-DOMINIO/api/health`
   → deve responder: `{"status":"ok","service":"Study Time API (PHP)",...}`
2. Acesse `https://SEU-DOMINIO/` → a plataforma abre.
3. Crie uma conta, monte um cronograma e resolva uma questão. 🎉

---

## Solução de problemas

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| `500` em `/api/health` | Dados do MySQL errados em `config.php` | Revise DB_NAME/USER/PASS |
| Página inicial dá 403 | Arquivos não estão em `public_html` (ou faltou o `index.html`) | Reenvie/extraia na pasta certa |
| Login não funciona | Cabeçalho `Authorization` bloqueado | Confirme que o `api/.htaccess` foi enviado |
| Questões não carregam | Servidor sem acesso à internet de saída | Raro no Hostinger; contate o suporte |

---

## Estrutura no servidor (resumo)

- **Frontend** (HTML/CSS/JS) → `public_html/`
- **API PHP** → `public_html/api/` (login, cronograma, questões, desempenho)
- **Banco** → MySQL do Hostinger (criado no Passo 1)
- **Questões** → API oficial [ENEM.dev](https://enem.dev) (em tempo real)
