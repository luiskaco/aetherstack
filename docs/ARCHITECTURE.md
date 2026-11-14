# Arquitectura: AetherStack

## Diseño del sistema


### 1. Arquitectura General
AetherStack sigue una arquitectura desacoplada y orientada a procesos portables sobre el sistema operativo Windows.

```
┌────────────────────────────────────────────────────────┐
│          AetherStack App (Material Design 3)          │
│                [app.py / CustomTkinter]                │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│            Core Engine Orchestrator [core.py]          │
└───────┬───────────────────┼────────────────────┬───────┘
        │                   │                    │
        ▼                   ▼                    ▼
┌──────────────┐    ┌──────────────┐     ┌──────────────┐
│  Nginx 1.28  │    │  PHP FastCGI │     │ MariaDB 11.8 │
│  [Port: 80]  │    │ (8.4 / 8.5)  │     │ [Port: 3307] │
└───────┬──────┘    └───────┬──────┘     └───────┬──────┘
        │                   │                    │
        ▼                   ▼                    ▼
┌───────────────────────────────────────────────────────┐
│   Carpeta de Proyectos Local (configurable)          │
│          [Laravel Apps / WordPress Sites]             │
└───────────────────────────────────────────────────────┘
```

---

### 2. Componentes Clave

1. **`app.py`:** Interfaz gráfica nativa con tokens de diseño Material 3, hilos en segundo plano para evitar bloqueos y comunicación directa con el motor.
2. **`core.py`:** Administra el ciclo de vida de los procesos (`start`, `stop`, `switch_php`), la detección de puertos, la creación de Virtual Hosts Nginx y la gestión de bases de datos.
3. **`conf/nginx.conf`:** Enrutador maestro con directivas optimizadas para Laravel (`public/`) y WordPress (URLs amigables / permalinks).
4. **`conf/my.ini`:** Configuración de MariaDB con juego de caracteres `utf8mb4_unicode_ci` y puerto aislado `3307`.

## Especificaciones técnicas


### 1. Runtimes y Binarios

| Componente | Versión | Tipo / Compilación | Ruta Relativa |
|---|---|---|---|
| **Nginx** | 1.28.3 | Windows x86/x64 | `bin/nginx/nginx.exe` |
| **PHP 8.4** | 8.4.27 | NTS Visual C++ 2022 x64 | `bin/php/php-8.4/php.exe` |
| **PHP 8.5** | 8.5.12 | NTS Visual C++ 2022 x64 | `bin/php/php-8.5/php.exe` |
| **MariaDB** | 11.8.8 | Win64 AMD64 | `bin/mariadb/mariadbd.exe` |
| **Composer** | 2.x | Phar Portable | `bin/composer/composer.phar` |

---

### 2. Puertos y Protocolos

- **Puerto HTTP Web:** `80` (personalizable en `state.json`)
- **Puerto PHP FastCGI:** `9000` (`127.0.0.1:9000`)
- **Puerto MariaDB (MySQL):** `3307` (`127.0.0.1:3307`)

---

### 3. Extensiones PHP Preactivadas
- `curl`, `mbstring`, `openssl`, `pdo_mysql`, `mysqli`
- `gd`, `intl`, `zip`, `fileinfo`, `exif`
- `pdo_sqlite`, `sqlite3`, `bz2`
- `Zend OPcache` (aceleración en memoria)
