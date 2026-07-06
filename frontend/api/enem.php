<?php
/**
 * Integração com a API oficial ENEM.dev (questões reais do ENEM).
 * Faz cache em arquivos temporários para reduzir latência e requisições.
 */

function enem_cache_dir(): string
{
    $dir = sys_get_temp_dir() . '/studytime_enem';
    if (!is_dir($dir)) {
        @mkdir($dir, 0777, true);
    }
    return $dir;
}

function enem_cache_get(string $key)
{
    $file = enem_cache_dir() . '/' . md5($key) . '.json';
    if (is_file($file) && (time() - filemtime($file) < 1800)) {
        $data = json_decode(file_get_contents($file), true);
        if ($data !== null) {
            return $data;
        }
    }
    return null;
}

function enem_cache_set(string $key, $value): void
{
    $file = enem_cache_dir() . '/' . md5($key) . '.json';
    @file_put_contents($file, json_encode($value));
}

function enem_http_get(string $url)
{
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 15,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_USERAGENT => 'StudyTime/1.0',
        ]);
        $res = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($res === false) {
            error_json('Falha de conexão com a API ENEM.dev.', 502);
        }
    } else {
        $res = @file_get_contents($url);
        $code = 200;
        if ($res === false) {
            error_json('Falha de conexão com a API ENEM.dev.', 502);
        }
    }

    if ($code === 429) {
        error_json('Limite de requisições atingido. Tente novamente em instantes.', 502);
    }
    if ($code < 200 || $code >= 300) {
        error_json("A API ENEM.dev retornou status $code.", 502);
    }
    return json_decode($res, true);
}

function enem_list_exams()
{
    $cached = enem_cache_get('exams');
    if ($cached !== null) {
        return $cached;
    }
    $data = enem_http_get(ENEM_API_BASE . '/exams');
    enem_cache_set('exams', $data);
    return $data;
}

function enem_all_questions(int $year, ?string $language): array
{
    $key = "all:$year:" . ($language ?? 'default');
    $cached = enem_cache_get($key);
    if ($cached !== null) {
        return $cached;
    }

    $questions = [];
    $offset = 0;
    $limit = 50;
    while (true) {
        $url = ENEM_API_BASE . "/exams/$year/questions?limit=$limit&offset=$offset";
        if ($language) {
            $url .= '&language=' . urlencode($language);
        }
        $data = enem_http_get($url);
        $batch = $data['questions'] ?? [];
        $questions = array_merge($questions, $batch);
        $meta = $data['metadata'] ?? [];
        if (empty($meta['hasMore']) || empty($batch)) {
            break;
        }
        $offset += $limit;
    }

    enem_cache_set($key, $questions);
    return $questions;
}

/** Remove o gabarito antes de enviar a questão ao frontend. */
function enem_strip_answer(array $q): array
{
    unset($q['correctAlternative']);
    $q['alternatives'] = array_map(function ($a) {
        return [
            'letter' => $a['letter'] ?? null,
            'text' => $a['text'] ?? null,
            'file' => $a['file'] ?? null,
        ];
    }, $q['alternatives'] ?? []);
    return $q;
}

function enem_get_questions(int $year, ?string $discipline, ?string $language, int $limit, int $offset): array
{
    $all = enem_all_questions($year, $language);
    if ($discipline) {
        $all = array_values(array_filter($all, fn($q) => ($q['discipline'] ?? null) === $discipline));
    }
    $total = count($all);
    $page = array_slice($all, $offset, $limit);
    return [
        'metadata' => [
            'year' => $year,
            'discipline' => $discipline,
            'language' => $language,
            'limit' => $limit,
            'offset' => $offset,
            'total' => $total,
            'hasMore' => ($offset + $limit) < $total,
        ],
        'questions' => array_map('enem_strip_answer', $page),
    ];
}

function enem_get_single(int $year, int $index, ?string $language): array
{
    $key = "q:$year:$index:" . ($language ?? 'default');
    $cached = enem_cache_get($key);
    if ($cached === null) {
        $url = ENEM_API_BASE . "/exams/$year/questions/$index";
        if ($language) {
            $url .= '?language=' . urlencode($language);
        }
        $cached = enem_http_get($url);
        enem_cache_set($key, $cached);
    }
    return $cached;
}
