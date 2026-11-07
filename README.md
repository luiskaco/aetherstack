<div align="center">

# ⚡ AetherStack

**High-Performance, Weightless Local Development Suite for Windows**  
*Entorno de desarrollo local moderno, ultraligero y portable para PHP, Laravel y WordPress.*

[![PHP Versions](https://img.shields.io/badge/PHP-8.1%20%7C%208.2%20%7C%208.3%20%7C%208.4%20%7C%208.5-777BB4?style=for-the-badge&logo=php&logoColor=white)](https://www.php.net/)
[![Nginx](https://img.shields.io/badge/Nginx-1.28%20Stable-009639?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org/)
[![MariaDB](https://img.shields.io/badge/MariaDB-11.8%20LTS%20(Port%203307)-C0765A?style=for-the-badge&logo=mariadb&logoColor=white)](https://mariadb.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11%20x64-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com)

</div>

---

## 📋 Tabla de Contenidos

1. [Visión General](#-visión-general)
2. [¿Por qué AetherStack?](#-por-qué-aetherstack)
3. [Componentes del Stack](#-componentes-del-stack)
4. [Características Principales](#-características-principales)
5. [Estructura del Proyecto](#-estructura-del-proyecto)
6. [Guía de Inicio Rápido](#-guía-de-inicio-rápido)
7. [Gestión de Proyectos](#-gestión-de-proyectos)
8. [Configuración de Base de Datos](#-configuración-de-base-de-datos)
9. [Terminal de Desarrollo Integrada](#-terminal-de-desarrollo-integrada)
10. [Documentación Técnica Oficial](#-documentación-técnica-oficial)

---

## 🌟 Visión General

**AetherStack** nace como una alternativa moderna, minimalista y de alto rendimiento a herramientas tradicionales como Laragon, XAMPP y Docker Desktop. Diseñado específicamente para desarrolladores que trabajan con **Laravel**, **WordPress** y aplicaciones PHP contemporáneas sobre Windows, ofrece una experiencia libre de anuncios, donaciones intrusivas, instaladores pesados y dependencias externas.

Todo el stack es **100% portable y autocontenido**, sin escribir en el Registro de Windows ni ensuciar las variables de entorno del sistema operativo.

---

## ⚡ ¿Por qué AetherStack?

| Criterio | AetherStack ⚡ | Laragon 🐘 | Docker Desktop 🐳 | XAMPP 📦 |
| :--- | :---: | :---: | :---: | :---: |
| **Tiempo de Arranque** | **< 1.0 segundo** | ~3-5 segundos | ~30-60 segundos | ~5-10 segundos |
| **Consumo de Memoria (RAM)** | **< 95 MB** | ~180-250 MB | ~2.5 GB - 4.5 GB | ~250-400 MB |
| **Ventanas emergentes / Donaciones** | **0 (Totalmente limpio)** | Frecuentes | Notificaciones | Ninguno |
| **Conflictos de Puerto (MySQL)** | **Sin conflicto (3307)** | Ocupa 3306 | Ocupa 3306 | Ocupa 3306 |
| **Conmutador de PHP** | **8.1, 8.2, 8.3, 8.4, 8.5** | Manual | Vía Dockerfile | Manual complejo |
| **Portabilidad** | **100% Autocontenido** | Semi-portable | No portable | Instalador fijo |

---

## 🧩 Componentes del Stack

| Servicio | Versión / Detalle | Puerto | Protocolo |
| :--- | :--- | :---: | :--- |
| **Nginx** | 1.28.0 Mainline optimizado para Windows | `80` | HTTP / FastCGI Proxy |
| **PHP Engine** | 8.1, 8.2, 8.3, 8.4 y 8.5 (NTS x64) | `9000` | FastCGI Daemon |
| **MariaDB** | 11.8.x LTS Portable Edition | `3307` | TCP/IP (Evita colisión con 3306) |
| **Composer** | 2.8.x Portable PHAR con cache aislada | CLI | CLI Package Manager |
| **Aether Console** | Cliente de escritorio nativo (Dark SaaS UI) | GUI | Python CustomTkinter 5.2+ |

---

## 🚀 Características Principales

### 1. Conmutador Multi-Versión de PHP en Caliente
Permite alternar entre **PHP 8.1, 8.2, 8.3, 8.4 y 8.5** con un solo clic desde el menú desplegable de la interfaz. El servicio FastCGI se reinicia automáticamente en segundo plano sin interrumpir Nginx ni recargar la ventana.

### 2. Scaffolders Automatizados en 1 Clic
- **Laravel:** Descarga la última versión vía Composer, genera la base de datos asociada en MariaDB (`<nombre>_db`), configura automáticamente el archivo `.env` (puerto `3307`, credenciales y host) y emite el Virtual Host con `/public` como DocumentRoot.
- **WordPress:** Descarga el núcleo oficial en español, crea la base de datos en MariaDB, genera el archivo `wp-config.php` preconfigurado con claves únicas y registra el Virtual Host correspondiente.

### 3. Filtro Estricto y Detección Reactiva de Proyectos
La sección "Mis Proyectos" escanea periódicamente el directorio raíz (`D:\LabIA`) y lista de forma exclusiva proyectos válidos de **WordPress** (presencia de `wp-config.php` o estructura WP) y **Laravel** (presencia del ejecutable `artisan`). 
Cualquier carpeta creada, eliminada o renombrada directamente desde el Explorador de Windows o la consola se sincroniza en pantalla en menos de 3 segundos sin recarga manual.

### 4. Eliminación Completa y Asíncrona
Al eliminar un proyecto desde la interfaz:
- Se purga la base de datos asociada en MariaDB.
- Se retira el archivo de Virtual Host en Nginx y se recarga el servidor web.
- Se elimina la carpeta de archivos en disco (manejando atributos de solo lectura y bloqueos de Git).
- La fila desaparece de inmediato en segundo plano sin congelar la interfaz ni mostrar alertas modales intrusivas.

### 5. Barra de Navegación de Directorio
La barra superior muestra permanentemente la ruta activa de proyectos (`📁 Ruta de Proyectos: D:\LabIA`) con un botón de acceso directo para abrir el Explorador de Windows al instante.

---

## 📂 Estructura del Proyecto

```text
D:\LabIA\aetherstack\
├── bin/                       # Binarios portables del ecosistema
│   ├── composer/              # Composer PHAR y script de ejecución
│   ├── mariadb/               # Motor y utilitarios cliente de MariaDB 11.8
│   ├── nginx/                 # Servidor web Nginx 1.28
│   └── php/                   # Versiones de PHP aisladas
│       ├── php-8.1/           # PHP 8.1 NTS + extensiones + php.ini
│       ├── php-8.2/           # PHP 8.2 NTS + extensiones + php.ini
│       ├── php-8.3/           # PHP 8.3 NTS + extensiones + php.ini
│       ├── php-8.4/           # PHP 8.4 NTS + extensiones + php.ini
│       └── php-8.5/           # PHP 8.5 Development Preview
├── conf/                      # Archivos de configuración maestros
│   ├── my.ini                 # Configuración de MariaDB (puerto 3307, buffer 256M)
│   ├── nginx.conf             # Servidor maestro Nginx con upstream a FastCGI
│   ├── state.json             # Estado persistente del stack y rutas
│   └── vhosts/                # Virtual Hosts autogenerados (*.conf)
├── data/                      # Almacenamiento físico de bases de datos MariaDB
├── docs/                      # Suite de documentación formal (/docs)
├── logs/                      # Registro centralizado de logs (Nginx, PHP, MariaDB)
├── AetherStack.bat            # Lanzador optimizado para la aplicación gráfica
├── app.py                     # Interfaz de escritorio moderna (SaaS Dark Theme)
├── core.py                    # Motor de orquestación, sockets y procesos
├── start.bat                  # Script de arranque headless por consola
└── stop.bat                   # Script de apagado limpio por consola
```

---

## 🛠️ Guía de Inicio Rápido

### Acceso Directo de Escritorio
Al instalar AetherStack se genera un acceso directo oficial en el Escritorio de Windows con icono propio:
- **Nombre:** `AetherStack`
- **Destino:** Ejecuta `AetherStack.bat` en segundo plano sin dejar consolas CMD residuales.

### Control por Línea de Comandos
Si preferís operar el stack sin interfaz gráfica:
```cmd
:: Iniciar todos los servicios (Nginx, PHP FastCGI, MariaDB)
D:\LabIA\aetherstack\start.bat

:: Detener todos los procesos de forma limpia
D:\LabIA\aetherstack\stop.bat
```

---

## 🌐 Gestión de Proyectos

Todos los proyectos se ubican en la carpeta raíz configurada (por defecto `D:\LabIA`).

Cada proyecto cuenta con dos métodos de acceso HTTP inmediato:
1. **Acceso directo por subdirectorio:**
   ```text
   http://localhost/<nombre-proyecto>/
   ```
2. **Acceso por Virtual Host local:**
   ```text
   http://<nombre-proyecto>.local
   ```

*Nota para Laravel:* Nginx redirige automáticamente la raíz hacia la carpeta interna `/public`.

---

## 🗄️ Configuración de Base de Datos

MariaDB se encuentra preinicializado y configurado en un puerto independiente para garantizar compatibilidad total con Docker Desktop, WSL o servicios MySQL previos:

- **Host:** `127.0.0.1` (o `localhost`)
- **Puerto:** `3307`
- **Usuario:** `root`
- **Contraseña:** *(vacía / sin contraseña por defecto)*
- **Juego de caracteres predeterminado:** `utf8mb4`
- **Cotejamiento (Collation):** `utf8mb4_unicode_ci`

Podés conectarte desde cualquier cliente visual estándar (HeidiSQL, DBeaver, TablePlus, VS Code Database Client o PhpStorm) apuntando al puerto **3307**.

---

## 💻 Terminal de Desarrollo Integrada

Al pulsar el botón **Terminal** dentro de los accesos rápidos de la interfaz, se despliega una consola de comandos `cmd.exe` con el entorno completamente configurado:
- El directorio de trabajo inicia directamente en `D:\LabIA`.
- La variable `PATH` se precarga con los binarios de la versión activa de PHP, Composer y el cliente CLI de MariaDB.
- Podés ejecutar directamente comandos globales como:
  ```bash
  php -v
  composer create-project ...
  mariadb -u root -P 3307
  php artisan migrate
  ```

---

## 📚 Documentación Técnica Oficial

El proyecto cuenta con una especificación técnica formal y auditada dentro del directorio [`docs/`](file:///D:/LabIA/aetherstack/docs/):

| Documento | Título | Descripción |
| :--- | :--- | :--- |
| [`01_PROJECT_PRD.md`](file:///D:/LabIA/aetherstack/docs/01_PROJECT_PRD.md) | Requisitos del Producto | Especificación de requisitos funcionales y no funcionales. |
| [`02_SDD.md`](file:///D:/LabIA/aetherstack/docs/02_SDD.md) | Diseño del Sistema | Arquitectura de componentes, topología de puertos y ciclo de vida. |
| [`03_SYSTEM_SPEC.md`](file:///D:/LabIA/aetherstack/docs/03_SYSTEM_SPEC.md) | Especificaciones Técnicas | Parámetros de runtime, binarios, flags y directivas de configuración. |
| [`04_DATA_MODEL.md`](file:///D:/LabIA/aetherstack/docs/04_DATA_MODEL.md) | Modelo de Datos | Esquema de persistencia interna (`state.json`, vhosts, tablas del sistema). |
| [`05_ARCHITECTURE.md`](file:///D:/LabIA/aetherstack/docs/05_ARCHITECTURE.md) | Decisiones de Arquitectura | Fundamentos arquitectónicos (FastCGI, puerto 3307, UI nativa). |
| [`06_TASKS.md`](file:///D:/LabIA/aetherstack/docs/06_TASKS.md) | Backlog Activo | Registro de hitos completados y estado de traspaso del proyecto. |
| [`07_DECISIONS.md`](file:///D:/LabIA/aetherstack/docs/07_DECISIONS.md) | ADRs (Architecture Records) | Registro histórico de decisiones técnicas y trade-offs evaluados. |
| [`08_CHANGELOG.md`](file:///D:/LabIA/aetherstack/docs/08_CHANGELOG.md) | Registro de Cambios | Historial de versiones bajo el estándar Keep a Changelog. |
| [`09_TESTING.md`](file:///D:/LabIA/aetherstack/docs/09_TESTING.md) | Estrategia de Pruebas | Suite de verificación de puertos, procesos, FastCGI y scaffolders. |
| [`10_RUNBOOK.md`](file:///D:/LabIA/aetherstack/docs/10_RUNBOOK.md) | Manual de Operaciones | Procedimientos de mantenimiento, solución de problemas y respaldos. |

---

## 📄 Licencia

Este proyecto está liberado bajo la licencia **MIT**. Eres libre de usarlo, modificarlo y distribuirlo para proyectos personales o comerciales sin restricciones.
