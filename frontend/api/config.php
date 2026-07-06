<?php
/**
 * Study Time - Configuração do backend PHP (deploy Hostinger)
 * ------------------------------------------------------------
 * Edite os dados do MySQL abaixo com os do seu Hostinger:
 *   hPanel  ->  Bancos de dados  ->  Gerenciamento de bancos MySQL
 * Lá você cria o banco, o usuário e a senha, e copia os valores aqui.
 */

// ---- Banco de dados MySQL (Hostinger) ----
// Basta editar os valores padrão abaixo com os dados do seu Hostinger.
// (Opcionalmente aceita variáveis de ambiente de mesmo nome.)
define('DB_HOST', getenv('DB_HOST') ?: 'localhost');       // no Hostinger geralmente é "localhost"
define('DB_NAME', getenv('DB_NAME') ?: 'SEU_BANCO_AQUI');  // ex.: u123456789_studytime
define('DB_USER', getenv('DB_USER') ?: 'SEU_USUARIO_AQUI'); // ex.: u123456789_admin
define('DB_PASS', getenv('DB_PASS') !== false ? getenv('DB_PASS') : 'SUA_SENHA_AQUI');
define('DB_CHARSET', 'utf8mb4');

// ---- Segurança ----
// Troque por uma frase secreta longa e aleatória (assina os tokens de login).
define('JWT_SECRET', 'troque-esta-frase-secreta-bem-longa-e-aleatoria-2026');
define('JWT_EXP_HOURS', 24 * 7);

// ---- API oficial de questões do ENEM ----
define('ENEM_API_BASE', 'https://api.enem.dev/v1');

// Fuso horário
date_default_timezone_set('America/Sao_Paulo');
