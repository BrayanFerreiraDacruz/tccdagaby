<?php
/**
 * MODELO de configuração do servidor (Hostinger).
 *
 * COPIE este arquivo para "config.local.php" (no mesmo diretório, dentro de
 * public_html/api/) e preencha com os dados reais do seu banco MySQL.
 *
 * O arquivo "config.local.php" NÃO vai para o Git e NÃO é sobrescrito pelo
 * deploy automático — suas credenciais ficam seguras e permanentes.
 */

define('DB_HOST', 'localhost');
define('DB_NAME', 'u123456789_studytime');   // nome gerado no hPanel
define('DB_USER', 'u123456789_admin');        // usuário gerado no hPanel
define('DB_PASS', 'SUA_SENHA_DO_BANCO');
define('JWT_SECRET', 'coloque-aqui-uma-frase-bem-longa-e-aleatoria');
