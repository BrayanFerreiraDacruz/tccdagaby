<?php
/**
 * Study Time - Configuração do backend PHP (deploy Hostinger)
 * ------------------------------------------------------------
 * As credenciais REAIS do servidor ficam em "config.local.php" (criado uma
 * única vez no Hostinger, NÃO versionado e NÃO sobrescrito pelo deploy).
 * Os valores abaixo são apenas padrão/desenvolvimento.
 */

// Carrega as credenciais do servidor, se existirem (produção).
if (file_exists(__DIR__ . '/config.local.php')) {
    require __DIR__ . '/config.local.php';
}

// ---- Banco de dados MySQL ----
if (!defined('DB_HOST')) define('DB_HOST', getenv('DB_HOST') ?: 'localhost');
if (!defined('DB_NAME')) define('DB_NAME', getenv('DB_NAME') ?: 'SEU_BANCO_AQUI');
if (!defined('DB_USER')) define('DB_USER', getenv('DB_USER') ?: 'SEU_USUARIO_AQUI');
if (!defined('DB_PASS')) define('DB_PASS', getenv('DB_PASS') !== false ? getenv('DB_PASS') : 'SUA_SENHA_AQUI');
if (!defined('DB_CHARSET')) define('DB_CHARSET', 'utf8mb4');

// ---- Segurança ----
if (!defined('JWT_SECRET')) {
    define('JWT_SECRET', getenv('JWT_SECRET') ?: 'troque-esta-frase-secreta-bem-longa-e-aleatoria-2026');
}
if (!defined('JWT_EXP_HOURS')) define('JWT_EXP_HOURS', 24 * 7);

// ---- API oficial de questões do ENEM ----
if (!defined('ENEM_API_BASE')) define('ENEM_API_BASE', 'https://api.enem.dev/v1');

date_default_timezone_set('America/Sao_Paulo');
