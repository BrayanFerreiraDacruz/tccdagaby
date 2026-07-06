<?php
/**
 * Utilitários: resposta JSON, leitura do corpo, autenticação.
 */

function send_json($data, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

function error_json(string $message, int $status = 400): void
{
    send_json(['error' => $message], $status);
}

/** Lê o corpo JSON da requisição como array associativo. */
function body(): array
{
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

/** Retorna o cabeçalho Authorization (compatível com vários servidores). */
function auth_header(): string
{
    $headers = [];
    if (function_exists('getallheaders')) {
        $headers = getallheaders();
    }
    foreach ($headers as $k => $v) {
        if (strtolower($k) === 'authorization') {
            return $v;
        }
    }
    return $_SERVER['HTTP_AUTHORIZATION']
        ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION']
        ?? '';
}

/** Exige login. Retorna o usuário autenticado ou encerra com 401. */
function require_auth(): array
{
    $header = auth_header();
    if (stripos($header, 'Bearer ') !== 0) {
        error_json('Token ausente. Faça login novamente.', 401);
    }
    $token = trim(substr($header, 7));
    $payload = jwt_decode($token);
    if (!$payload || !isset($payload['sub'])) {
        error_json('Sessão expirada. Faça login novamente.', 401);
    }

    $stmt = db()->prepare('SELECT id, name, email, created_at FROM users WHERE id = ?');
    $stmt->execute([$payload['sub']]);
    $user = $stmt->fetch();
    if (!$user) {
        error_json('Usuário não encontrado.', 401);
    }
    return $user;
}

function make_token(array $user): string
{
    return jwt_encode([
        'sub' => (int) $user['id'],
        'email' => $user['email'],
        'iat' => time(),
        'exp' => time() + JWT_EXP_HOURS * 3600,
    ]);
}

function valid_email(string $email): bool
{
    return (bool) filter_var($email, FILTER_VALIDATE_EMAIL);
}
