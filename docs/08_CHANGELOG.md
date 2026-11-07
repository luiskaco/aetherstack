# 08 - Changelog: AetherStack

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto adhiere a [Semantic Versioning](https://semver.org/).

---

## [1.0.3] - 2026-11-07

### Mejorado
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
