<?php
/**
 * AetherStack - Database Manager (Adminer Wrapper)
 * Auto-login para MariaDB local en 127.0.0.1:3307
 */

session_start();

$driver = 'server'; // MySQL driver identifier in Adminer
$server = '127.0.0.1:3307';
$username = 'root';
$password = '';

// Pre-configurar sesión para auto-login instantáneo si no hay parámetros
if (!isset($_GET['server'])) {
    $_GET['server'] = $server;
}
if (!isset($_GET['username'])) {
    $_GET['username'] = $username;
}

if (!isset($_SESSION['pwds'][$driver][$server][$username])) {
    $_SESSION['pwds'][$driver][$server][$username] = $password;
}

function adminer_object() {
    class AetherAdminer extends Adminer {
        function name() {
            return '<span style="color:#38BDF8;font-weight:700;font-size:16px;">⚡ AetherStack</span> <span style="color:#94A3B8;font-size:13px;">DB</span>';
        }

        function credentials() {
            return array('127.0.0.1:3307', 'root', '');
        }

        function login($login, $password) {
            // Permitir conexión root local sin contraseña
            return true;
        }

        function permanentLogin($i = false) {
            return "aetherstack_db_key";
        }
    }
    return new AetherAdminer;
}

include __DIR__ . '/adminer.php';
