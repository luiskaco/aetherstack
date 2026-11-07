# 03 - System Specification: AetherStack

## 1. Runtimes y Binarios

| Componente | Versión | Tipo / Compilación | Ruta Relativa |
|---|---|---|---|
| **Nginx** | 1.28.3 | Windows x86/x64 | `bin/nginx/nginx.exe` |
| **PHP 8.4** | 8.4.27 | NTS Visual C++ 2022 x64 | `bin/php/php-8.4/php.exe` |
| **PHP 8.5** | 8.5.12 | NTS Visual C++ 2022 x64 | `bin/php/php-8.5/php.exe` |
| **MariaDB** | 11.8.8 | Win64 AMD64 | `bin/mariadb/mariadbd.exe` |
| **Composer** | 2.x | Phar Portable | `bin/composer/composer.phar` |

---

## 2. Puertos y Protocolos

- **Puerto HTTP Web:** `80` (personalizable en `state.json`)
- **Puerto PHP FastCGI:** `9000` (`127.0.0.1:9000`)
- **Puerto MariaDB (MySQL):** `3307` (`127.0.0.1:3307`)

---

## 3. Extensiones PHP Preactivadas
- `curl`, `mbstring`, `openssl`, `pdo_mysql`, `mysqli`
- `gd`, `intl`, `zip`, `fileinfo`, `exif`
- `pdo_sqlite`, `sqlite3`, `bz2`
- `Zend OPcache` (aceleración en memoria)
