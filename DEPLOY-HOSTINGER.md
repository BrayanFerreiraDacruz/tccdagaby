# 🚀 Deploy automático no Hostinger (a cada commit)

O projeto está configurado para **publicar sozinho** no Hostinger a cada `git push`
na branch `main`, usando **GitHub Actions + FTP**.

- Frontend (HTML/CSS/JS) e a **API em PHP** (`frontend/api/`) vão para o `public_html`.
- O backend Flask/Python (`backend/`) continua no projeto para o TCC — não é enviado.
- Suas credenciais do banco ficam num arquivo do servidor que o deploy **nunca toca**.

Você configura isto **uma vez**. Depois, todo commit atualiza o site no ar.

---

## ✅ Configuração inicial (uma vez só, ~10 min)

### 1. Criar o banco de dados MySQL (hPanel)
1. hPanel → **Bancos de dados → Gerenciamento de bancos MySQL**.
2. Crie um banco. Anote **nome, usuário e senha** (o Hostinger usa prefixo, ex.:
   `u123456789_studytime` / `u123456789_admin`).

### 2. Pegar os dados de FTP (hPanel)
1. hPanel → **Arquivos → Contas FTP**.
2. Anote: **Hostname/IP do FTP**, **usuário FTP** e **senha FTP**.
   *(Se não tiver senha, use “Alterar senha da conta FTP”.)*

### 3. Cadastrar os segredos no GitHub
No repositório: **Settings → Secrets and variables → Actions → New repository secret**.
Crie **quatro** segredos:

| Nome do secret | Valor |
|----------------|-------|
| `FTP_HOST` | o hostname do FTP (ex.: `ftp.seudominio.com` ou o IP) |
| `FTP_USER` | o usuário FTP |
| `FTP_PASSWORD` | a senha FTP |
| `FTP_REMOTE_DIR` | `public_html/` *(ou `./` se a conta FTP já abrir dentro do public_html)* |

> A senha fica guardada **criptografada no GitHub** — ninguém a vê, nem aparece nos logs.

### 4. Disparar o primeiro deploy
Faça qualquer commit (ou vá em **Actions → Deploy para o Hostinger → Run workflow**).
Acompanhe em **Actions**; quando ficar verde ✅, os arquivos já estão no servidor.

### 5. Configurar o banco no servidor (uma vez)
Como o deploy nunca sobrescreve suas credenciais, crie-as manualmente:
1. hPanel → **Gerenciador de Arquivos → `public_html/api/`**.
2. Copie o arquivo **`config.local.sample.php`** para **`config.local.php`**.
3. Edite `config.local.php` com os dados do banco (passo 1):
   ```php
   <?php
   define('DB_HOST', 'localhost');
   define('DB_NAME', 'u123456789_studytime');
   define('DB_USER', 'u123456789_admin');
   define('DB_PASS', 'sua_senha_do_banco');
   define('JWT_SECRET', 'uma-frase-longa-e-aleatoria');
   ```

### 6. Testar 🎉
- `https://SEU-DOMINIO/api/health` → `{"status":"ok", ...}`
- `https://SEU-DOMINIO/` → cadastre-se, monte um cronograma, resolva uma questão.

---

## 🔁 No dia a dia

A partir daqui é só trabalhar normalmente:

```bash
git add .
git commit -m "minha alteração"
git push
```

O GitHub Actions publica no Hostinger em segundos. Não precisa mexer no hPanel de novo.

---

## 🛠️ Problemas comuns

| Sintoma | Causa | Solução |
|---------|-------|---------|
| Action falha em “FTP-Deploy” | Segredos de FTP errados/ausentes | Revise `FTP_HOST/USER/PASSWORD` |
| Deploy ok, mas site dá 404/403 | Pasta errada | Ajuste o secret `FTP_REMOTE_DIR` (`public_html/` ou `./`) |
| `500` em `/api/health` | Banco não configurado | Crie/edite `public_html/api/config.local.php` (passo 5) |
| Login não funciona | Cabeçalho `Authorization` bloqueado | Confirme que `api/.htaccess` foi enviado |

---

## 📦 Alternativa: upload manual (sem GitHub Actions)

Se preferir não usar o deploy automático, gere o pacote e suba pelo Gerenciador
de Arquivos:

1. Compacte o **conteúdo da pasta `frontend/`** em um `.zip`.
2. hPanel → Gerenciador de Arquivos → `public_html` → envie e **extraia** o zip.
3. Faça os passos **5** e **6** acima.
