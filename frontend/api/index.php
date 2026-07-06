<?php
/**
 * Study Time - API REST em PHP (deploy Hostinger)
 * Reimplementa o backend Flask usando PHP + MySQL, mantendo o mesmo
 * contrato de endpoints consumido pelo frontend.
 */

require __DIR__ . '/config.php';
require __DIR__ . '/jwt.php';
require __DIR__ . '/helpers.php';
require __DIR__ . '/db.php';
require __DIR__ . '/enem.php';

// CORS (mesma origem no Hostinger, mas mantido por segurança)
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'];
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
// Mantém só o que vem depois de "/api"
$path = preg_replace('#^.*?/api#', '', rawurldecode($uri));
$path = '/' . trim($path, '/');

// ---------------- Roteamento ----------------
try {
    // ---- Saúde ----
    if ($path === '/health' && $method === 'GET') {
        send_json(['status' => 'ok', 'service' => 'Study Time API (PHP)', 'database' => 'mysql']);
    }

    // ---- Autenticação ----
    if ($path === '/auth/register' && $method === 'POST') {
        return auth_register();
    }
    if ($path === '/auth/login' && $method === 'POST') {
        return auth_login();
    }
    if ($path === '/auth/me') {
        if ($method === 'GET') return auth_me();
        if ($method === 'PUT') return auth_update();
        if ($method === 'DELETE') return auth_delete();
    }

    // ---- Cronograma ----
    if ($path === '/schedules') {
        if ($method === 'GET') return schedules_list();
        if ($method === 'POST') return schedules_create();
    }
    if (preg_match('#^/schedules/(\d+)$#', $path, $m)) {
        if ($method === 'PUT') return schedules_update((int) $m[1]);
        if ($method === 'DELETE') return schedules_delete((int) $m[1]);
    }

    // ---- Questões (ENEM.dev) ----
    if ($path === '/exams' && $method === 'GET') {
        send_json(['exams' => enem_list_exams()]);
    }
    if ($path === '/questions' && $method === 'GET') {
        return questions_list();
    }
    if ($path === '/answer' && $method === 'POST') {
        return questions_answer();
    }

    // ---- Desempenho ----
    if ($path === '/performance/summary' && $method === 'GET') {
        return performance_summary();
    }
    if ($path === '/performance/history' && $method === 'GET') {
        return performance_history();
    }

    // ---- Materiais ----
    if ($path === '/materials' && $method === 'GET') {
        return materials_list();
    }

    error_json('Rota não encontrada: ' . $path, 404);
} catch (Throwable $e) {
    error_json('Erro interno no servidor.', 500);
}

// ============================================================
//  Handlers
// ============================================================

function auth_register()
{
    $d = body();
    $name = trim($d['name'] ?? '');
    $email = strtolower(trim($d['email'] ?? ''));
    $password = $d['password'] ?? '';

    if (mb_strlen($name) < 2) error_json('Informe um nome válido.');
    if (!valid_email($email)) error_json('Informe um e-mail válido.');
    if (strlen($password) < 6) error_json('A senha deve ter ao menos 6 caracteres.');

    $stmt = db()->prepare('SELECT id FROM users WHERE email = ?');
    $stmt->execute([$email]);
    if ($stmt->fetch()) error_json('Este e-mail já está cadastrado.', 409);

    $stmt = db()->prepare(
        'INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, NOW())'
    );
    $stmt->execute([$name, $email, password_hash($password, PASSWORD_DEFAULT)]);
    $id = (int) db()->lastInsertId();

    $user = ['id' => $id, 'name' => $name, 'email' => $email];
    send_json(['token' => make_token($user), 'user' => user_public($user)], 201);
}

function auth_login()
{
    $d = body();
    $email = strtolower(trim($d['email'] ?? ''));
    $password = $d['password'] ?? '';

    $stmt = db()->prepare('SELECT * FROM users WHERE email = ?');
    $stmt->execute([$email]);
    $user = $stmt->fetch();

    if (!$user || !password_verify($password, $user['password_hash'])) {
        error_json('E-mail ou senha incorretos.', 401);
    }
    send_json(['token' => make_token($user), 'user' => user_public($user)]);
}

function auth_me()
{
    $user = require_auth();
    send_json(['user' => user_public($user)]);
}

function auth_update()
{
    $user = require_auth();
    $d = body();

    $name = trim($d['name'] ?? '');
    $email = strtolower(trim($d['email'] ?? ''));
    $password = $d['password'] ?? '';

    $fields = [];
    $params = [];

    if ($name !== '') {
        if (mb_strlen($name) < 2) error_json('Informe um nome válido.');
        $fields[] = 'name = ?';
        $params[] = $name;
    }
    if ($email !== '' && $email !== $user['email']) {
        if (!valid_email($email)) error_json('Informe um e-mail válido.');
        $stmt = db()->prepare('SELECT id FROM users WHERE email = ?');
        $stmt->execute([$email]);
        if ($stmt->fetch()) error_json('Este e-mail já está em uso.', 409);
        $fields[] = 'email = ?';
        $params[] = $email;
    }
    if ($password !== '') {
        if (strlen($password) < 6) error_json('A senha deve ter ao menos 6 caracteres.');
        $fields[] = 'password_hash = ?';
        $params[] = password_hash($password, PASSWORD_DEFAULT);
    }

    if ($fields) {
        $params[] = $user['id'];
        $stmt = db()->prepare('UPDATE users SET ' . implode(', ', $fields) . ' WHERE id = ?');
        $stmt->execute($params);
    }

    $stmt = db()->prepare('SELECT id, name, email, created_at FROM users WHERE id = ?');
    $stmt->execute([$user['id']]);
    send_json(['user' => user_public($stmt->fetch())]);
}

function auth_delete()
{
    $user = require_auth();
    $stmt = db()->prepare('DELETE FROM users WHERE id = ?');
    $stmt->execute([$user['id']]);
    send_json(['message' => 'Conta excluída com sucesso.']);
}

function user_public(array $u): array
{
    return [
        'id' => (int) $u['id'],
        'name' => $u['name'],
        'email' => $u['email'],
        'created_at' => $u['created_at'] ?? null,
    ];
}

// ---- Cronograma ----
function validate_schedule(array $d)
{
    $title = trim($d['title'] ?? '');
    if ($title === '') return [null, 'Informe um título para o bloco de estudo.'];

    if (!isset($d['weekday']) || !is_numeric($d['weekday'])) return [null, 'Dia da semana inválido.'];
    $weekday = (int) $d['weekday'];
    if ($weekday < 0 || $weekday > 6) return [null, 'Dia da semana inválido.'];

    $start = trim($d['start_time'] ?? '');
    $end = trim($d['end_time'] ?? '');
    $re = '/^([01]\d|2[0-3]):[0-5]\d$/';
    if (!preg_match($re, $start) || !preg_match($re, $end)) {
        return [null, 'Horário inválido (use o formato HH:MM).'];
    }
    if ($end <= $start) return [null, 'O horário de término deve ser após o de início.'];

    return [[
        'title' => $title,
        'discipline' => trim($d['discipline'] ?? '') ?: null,
        'weekday' => $weekday,
        'start_time' => $start,
        'end_time' => $end,
        'notes' => trim($d['notes'] ?? '') ?: null,
    ], null];
}

function schedule_public(array $s): array
{
    return [
        'id' => (int) $s['id'],
        'title' => $s['title'],
        'discipline' => $s['discipline'],
        'weekday' => (int) $s['weekday'],
        'start_time' => $s['start_time'],
        'end_time' => $s['end_time'],
        'notes' => $s['notes'],
        'created_at' => $s['created_at'],
    ];
}

function schedules_list()
{
    $user = require_auth();
    $stmt = db()->prepare(
        'SELECT * FROM schedules WHERE user_id = ? ORDER BY weekday, start_time'
    );
    $stmt->execute([$user['id']]);
    send_json(['schedules' => array_map('schedule_public', $stmt->fetchAll())]);
}

function schedules_create()
{
    $user = require_auth();
    [$fields, $err] = validate_schedule(body());
    if ($err) error_json($err);

    $stmt = db()->prepare(
        'INSERT INTO schedules (user_id, title, discipline, weekday, start_time, end_time, notes, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, NOW())'
    );
    $stmt->execute([
        $user['id'], $fields['title'], $fields['discipline'], $fields['weekday'],
        $fields['start_time'], $fields['end_time'], $fields['notes'],
    ]);
    $id = (int) db()->lastInsertId();
    $stmt = db()->prepare('SELECT * FROM schedules WHERE id = ?');
    $stmt->execute([$id]);
    send_json(['schedule' => schedule_public($stmt->fetch())], 201);
}

function schedules_update(int $id)
{
    $user = require_auth();
    $stmt = db()->prepare('SELECT * FROM schedules WHERE id = ? AND user_id = ?');
    $stmt->execute([$id, $user['id']]);
    if (!$stmt->fetch()) error_json('Cronograma não encontrado.', 404);

    [$fields, $err] = validate_schedule(body());
    if ($err) error_json($err);

    $stmt = db()->prepare(
        'UPDATE schedules SET title = ?, discipline = ?, weekday = ?, start_time = ?, end_time = ?, notes = ?
         WHERE id = ? AND user_id = ?'
    );
    $stmt->execute([
        $fields['title'], $fields['discipline'], $fields['weekday'],
        $fields['start_time'], $fields['end_time'], $fields['notes'], $id, $user['id'],
    ]);
    $stmt = db()->prepare('SELECT * FROM schedules WHERE id = ?');
    $stmt->execute([$id]);
    send_json(['schedule' => schedule_public($stmt->fetch())]);
}

function schedules_delete(int $id)
{
    $user = require_auth();
    $stmt = db()->prepare('DELETE FROM schedules WHERE id = ? AND user_id = ?');
    $stmt->execute([$id, $user['id']]);
    if ($stmt->rowCount() === 0) error_json('Cronograma não encontrado.', 404);
    send_json(['message' => 'Bloco de estudo removido.']);
}

// ---- Questões ----
function questions_list()
{
    $year = (int) ($_GET['year'] ?? 2023);
    $discipline = $_GET['discipline'] ?? null;
    $language = $_GET['language'] ?? null;
    $limit = min((int) ($_GET['limit'] ?? 10), 30);
    $offset = max((int) ($_GET['offset'] ?? 0), 0);
    send_json(enem_get_questions($year, $discipline ?: null, $language ?: null, $limit, $offset));
}

function questions_answer()
{
    $user = require_auth();
    $d = body();
    $year = (int) ($d['year'] ?? 0);
    $index = (int) ($d['index'] ?? 0);
    $chosen = strtoupper(trim($d['chosen'] ?? ''));
    $language = $d['language'] ?? null;

    if (!$year || !$index) error_json('Ano ou questão inválidos.');
    if (!in_array($chosen, ['A', 'B', 'C', 'D', 'E'], true)) error_json('Alternativa inválida.');

    $q = enem_get_single($year, $index, $language ?: null);
    $correct = $q['correctAlternative'] ?? null;
    $is_correct = ($chosen === $correct) ? 1 : 0;

    $stmt = db()->prepare(
        'INSERT INTO attempts (user_id, year, question_index, discipline, language, chosen, correct, is_correct, answered_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW())'
    );
    $stmt->execute([
        $user['id'], $year, $index, $q['discipline'] ?? null, $q['language'] ?? null,
        $chosen, $correct, $is_correct,
    ]);

    send_json(['is_correct' => (bool) $is_correct, 'correct' => $correct, 'chosen' => $chosen]);
}

// ---- Desempenho ----
function performance_summary()
{
    $user = require_auth();
    $labels = [
        'linguagens' => 'Linguagens e Códigos',
        'ciencias-humanas' => 'Ciências Humanas',
        'ciencias-natureza' => 'Ciências da Natureza',
        'matematica' => 'Matemática',
    ];

    $stmt = db()->prepare('SELECT * FROM attempts WHERE user_id = ?');
    $stmt->execute([$user['id']]);
    $attempts = $stmt->fetchAll();

    $total = count($attempts);
    $correct = 0;
    $byDisc = [];
    foreach ($attempts as $a) {
        if ($a['is_correct']) $correct++;
        $key = $a['discipline'] ?: 'outros';
        if (!isset($byDisc[$key])) $byDisc[$key] = ['total' => 0, 'correct' => 0];
        $byDisc[$key]['total']++;
        if ($a['is_correct']) $byDisc[$key]['correct']++;
    }

    $disciplines = [];
    foreach ($byDisc as $key => $v) {
        $disciplines[] = [
            'discipline' => $key,
            'label' => $labels[$key] ?? ucfirst($key),
            'total' => $v['total'],
            'correct' => $v['correct'],
            'accuracy' => $v['total'] ? round($v['correct'] / $v['total'] * 100, 1) : 0.0,
        ];
    }
    usort($disciplines, fn($a, $b) => $b['total'] <=> $a['total']);

    send_json([
        'total' => $total,
        'correct' => $correct,
        'wrong' => $total - $correct,
        'accuracy' => $total ? round($correct / $total * 100, 1) : 0.0,
        'disciplines' => $disciplines,
    ]);
}

function performance_history()
{
    $user = require_auth();
    $stmt = db()->prepare(
        'SELECT * FROM attempts WHERE user_id = ? ORDER BY answered_at DESC LIMIT 50'
    );
    $stmt->execute([$user['id']]);
    $history = array_map(function ($a) {
        return [
            'id' => (int) $a['id'],
            'year' => (int) $a['year'],
            'question_index' => (int) $a['question_index'],
            'discipline' => $a['discipline'],
            'language' => $a['language'],
            'chosen' => $a['chosen'],
            'correct' => $a['correct'],
            'is_correct' => (bool) $a['is_correct'],
            'answered_at' => $a['answered_at'],
        ];
    }, $stmt->fetchAll());
    send_json(['history' => $history]);
}

// ---- Materiais ----
function materials_list()
{
    send_json(['materials' => require __DIR__ . '/materials_data.php']);
}
