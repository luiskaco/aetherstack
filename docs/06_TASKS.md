# 06 - Backlog & Task Tracking: AetherStack

## Estado de Traspaso (Handover State)
- **Estado Actual:** Sistema operativo, estable y funcional.
- **Acceso:** Disponible en el Escritorio con icono propio (`AetherStack.lnk`).
- **Tipo:** Aplicación desktop portable para Windows 10/11 x64.

---

## Tareas Completadas
- [x] Portabilidad total y plug-and-play: resolución dinámica de rutas relativas a `BASE_DIR` en scripts batch (`%~dp0`), `nginx.conf`, `my.ini` (MariaDB) y `php.ini`, permitiendo mover la suite a cualquier PC o pendrive sin fallos de configuración.
- [x] Internacionalización (i18n): soporte completo para Español (ES) e Inglés (EN) con botón de alternancia en la barra superior (`🌐 EN` / `🌐 ES`) y persistencia en configuración.
- [x] Condición preventiva de creación: bloqueo estricto en UI y lógica core para impedir crear proyectos si el stack de servicios (Nginx, PHP, MariaDB) no está activo.
- [x] Descarga e integración de Nginx 1.28 portable.
- [x] Soporte para múltiples versiones de PHP: 8.1, 8.2, 8.3, 8.4 y 8.5 con selector dinámico tipo dropdown en caliente.
- [x] Descarga y configuración de MariaDB 11.8 (puerto 3307).
- [x] Configuración de Composer portable.
- [x] Motor de creación rápida de proyectos Laravel (Composer + DB + .env).
- [x] Motor de creación rápida de WordPress (Core oficial + DB + wp-config.php).
- [x] Generación de icono `.ico` y acceso directo en el Escritorio.
- [x] Filtro estricto en "Mis Proyectos" para mostrar solo Laravel y WordPress.
- [x] Función de eliminación completa de proyectos (archivos, DB y Virtual Host).
- [x] Recarga automática inmediata de la lista de proyectos al eliminar o crear un proyecto.
- [x] Detección reactiva de cambios en disco en segundo plano y buscador en tiempo real.
- [x] Rediseño a **Material Design 3 (M3 Dark Theme)**.
- [x] Centrado dinámico de ventanas modales respecto a la ventana principal.
- [x] Modales oscuros integrados para confirmaciones y alertas (reemplazo de MessageBox Win32).
- [x] Portabilidad completa de documentación técnica y `README.md` con rutas relativas y captura de interfaz.
- [x] Documentación oficial en `/docs`.

---

## Backlog Futuro (Opcional)
- [ ] Soporte para certificados SSL locales (HTTPS automático).
- [ ] Soporte para Node.js / NPM dentro de la terminal integrada de desarrollo.
- [ ] Exportador de base de datos a `.sql` desde la pestaña de proyectos.
