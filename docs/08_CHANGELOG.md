# 08 - Changelog: AetherStack

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto adhiere a [Semantic Versioning](https://semver.org/).

---

## [1.0.6] - 2026-11-07

### Añadido
- Visor y gestor completo de bases de datos integrado con **Adminer** en `tools/adminer/`:
  - Capacidad completa para crear, ver, modificar, importar y exportar tablas y bases de datos (`.sql` y `.sql.gz`).
  - Auto-login transparente preconfigurado a MariaDB en `127.0.0.1:3307` con usuario `root`.
  - Tema oscuro a medida (`adminer.css`) integrado con la paleta de colores de AetherStack (Slate 900 y acentos neón).
  - Exposición web directa en puerto dedicado `http://localhost:3308` y alias `/aether-db/`.
  - Botón de acceso rápido **"Gestor DB"** (`🗄`) en la sección de Acceso Rápido del Dashboard.
  - Botón **"Abrir Gestor Web"** en el panel lateral de detalles de MariaDB Server.
  - Botón directo de base de datos (`🗄`) en cada fila de proyecto de "Mis Proyectos" para abrir directamente la BD correspondiente (`<nombre>_db`).
  - Protección preventiva: alerta al usuario si intenta abrir el gestor mientras el stack se encuentra apagado.

## [1.0.5] - 2026-11-07

### Añadido
- Formato de icono nativo DIB (BMP) en `icon.ico` para compatibilidad completa con Windows Shell, evitando la degradación al icono genérico de Python en el Escritorio.
- Notificación automática al Shell de Windows (`SHChangeNotify`) al crear o actualizar accesos directos, refrescando de inmediato la caché de iconos del explorador.
- Icono oficial integrado en todas las ventanas modales secundarias (creación de proyectos, confirmaciones y alertas).

### Mejorado
- Portabilidad física plug-and-play total: bases de datos (`data/mariadb/`), configuraciones de Nginx (`nginx.conf`, vhosts), PHP (`php.ini`) y MariaDB (`my.ini`) resueltas dinámicamente con rutas relativas a la carpeta del proyecto, permitiendo transferir la suite a otra PC o unidad USB manteniendo todas las bases de datos intactas.

## [1.0.4] - 2026-11-07

### Añadido
- Soporte multilingüe completo con módulo de internacionalización (`i18n.py`) para **Español (ES)** e **Inglés (EN)**.
- Botón toggle de idioma en la barra superior (`🌐 EN` / `🌐 ES`) junto al control maestro del stack, con alternancia instantánea sin reiniciar la aplicación.
- Persistencia del idioma preferido en `state.json` (`"language": "es"` / `"en"`).
- Traducción integral de toda la suite: tarjetas de servicios, accesos rápidos, tabla de proyectos, panel de detalles del stack, diálogos de creación, confirmaciones de eliminación, modales de configuración y alertas del sistema.

## [1.0.3] - 2026-11-07

### Mejorado
- Condición preventiva en creación de proyectos: bloqueo en UI y validación en `core.py` si el stack de servicios no está activo, evitando proyectos incompletos o fallos de base de datos en MariaDB.
- Centrado dinámico de modales de creación de proyecto y configuración en relación a la ventana principal de la aplicación.
- Modales nativos de confirmación y alertas con diseño dark premium integrado (`CTkLabel`, `CTkButton`), eliminando los diálogos estándar Win32.
- Documentación 100% portable: reemplazo de rutas absolutas por rutas relativas en todos los documentos técnicos y `README.md`.
- Incorporación de vista previa gráfica (`preview.png`) de la consola en el `README.md`.

## [1.0.2] - 2026-11-07

### Añadido
- Soporte para versiones de PHP inferiores a 8.4: integración completa de **PHP 8.1, PHP 8.2 y PHP 8.3** (junto con 8.4 y 8.5).
- Selector dinámico de PHP con menú desplegable (`CTkOptionMenu`) en la tarjeta FastCGI que detecta automáticamente cualquier versión instalada en `bin/php/`.
- Conmutación en caliente en segundo plano sin reiniciar Nginx ni la interfaz.

## [1.0.1] - 2026-11-07

### Mejorado
- Recarga automática inmediata de la sección "Mis Proyectos" al eliminar un proyecto, sin requerir clics adicionales.
- Ejecución asíncrona no bloqueante de la eliminación física y de bases de datos.
- Sincronización automática periódica cada 3 segundos que detecta altas y bajas de carpetas directamente en disco.
- Filtro reactivo en la barra de búsqueda en tiempo real.
- Robustez en eliminación de carpetas bloqueadas o con atributos de solo lectura en Windows.

## [1.0.0] - 2026-11-07

### Añadido
- Motor central portable con Nginx 1.28, PHP 8.4 y PHP 8.5.
- Selector de versiones de PHP en caliente sin reinicios forzados.
- MariaDB configurado de forma independiente en puerto `3307`.
- Creador automatizado de proyectos Laravel (Composer + `.env` + DB).
- Creador automatizado de sitios WordPress con `wp-config.php` preconfigurado.
- Pestaña "Mis Proyectos" con filtro estricto (únicamente WordPress y Laravel).
- Funcionalidad de eliminación de proyectos (archivos, DB y Virtual Host).
- Menú modal de Configuración Global para modificar carpeta de proyectos y puertos.
- Icono `.ico` personalizado y acceso directo en el Escritorio de Windows.
- Interfaz gráfica rediseñada bajo **Material Design 3 (M3 Dark Theme)**.
- Documentación técnica completa en `/docs`.
