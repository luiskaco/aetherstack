# 06 - Backlog & Task Tracking: AetherStack

## Estado de Traspaso (Handover State)
- **Estado Actual:** Sistema operativo, estable y funcional.
- **Acceso:** `AetherStack.bat`; acceso directo opcional con `python generate_icon.py`.
- **Tipo:** Aplicación desktop portable para Windows 10/11 x64.
- **Release:** v1.1.0 (ver `10_RUNBOOK.md` § 5 para repetir el proceso).

---

## Pendiente (revisión de seguridad y buenas prácticas, 2026-11-08)
- [ ] MariaDB `root` sin contraseña: crear un usuario por proyecto (`.env` de Laravel / `wp-config.php`) y avisar en la UI.
- [ ] Verificar integridad (SHA256) de las descargas de Nginx, PHP, MariaDB, Composer y WordPress.
- [ ] Crear `requirements.txt` con `customtkinter` fijado.
- [ ] Reemplazar los `except Exception: pass` por registro en `logs/aetherstack.log`.
- [ ] `core.py` reescribe configuraciones al importarse: moverlo a una función `init()` llamada desde `app.py`.
- [ ] `start.bat` fija PHP 8.4 y `switch-php.bat` usa un enlace `current` que la app no usa: unificar con `state.json`.
- [ ] Tests automáticos de `core.py` (validación de nombres, generación de configs) y completar `docs/09_TESTING.md`.
- [ ] Decidir si la lista de proyectos debe mostrar carpetas con nombres no válidos (hoy se ocultan).

---

## Tareas Completadas
- [x] Revisión de seguridad: Nginx solo en `127.0.0.1` y sin listado de carpetas, validación de nombres de proyecto, eliminación de `os.system`, validación de Ajustes.
- [x] Release **v1.1.0** reproducible con `tools/build_release_zip.py` (lista blanca + base MariaDB vacía + escaneo de datos personales). Se retira el asset de v1.0.0, que incluía datos personales.
- [x] Empaquetado y publicación del **Release Oficial v1.0.0** en GitHub con paquete portable descargable `AetherStack-v1.0.0-portable.zip` (359 MB) y notas de lanzamiento bilingües.
- [x] Reordenación estratégica del `README.md`: sección en **Inglés como idioma principal inicial** para captar la atención de la comunidad global en GitHub, seguida de la versión en Español completa con salto rápido en la cabecera.
- [x] Reordenación estratégica del `README.md`: sección en **Inglés como idioma principal inicial** para captar la atención de la comunidad global en GitHub, seguida de la versión en Español completa con salto rápido en la cabecera.
- [x] Documentación bilingüe integral en `README.md` (Español e Inglés) con selector de idiomas en cabecera, tabla comparativa, guías paso a paso, estructura de carpetas, atajos de HeidiSQL y enlaces completos a `/docs`.
- [x] Integración de **HeidiSQL Portable** v12.22 (el mismo gestor de Laragon) en `bin/heidisql/`:
  - Aplicación de escritorio nativa de Windows, ultra-rápida y sin advertencias de PHP.
  - Modo 100% portable (`portable.lock` y `portable_settings.txt`) preconfigurado con sesión para MariaDB 11 en `127.0.0.1:3307`.
  - Lanzamiento directo desde el Dashboard ("Gestor DB"), panel lateral de MariaDB y botón por proyecto para abrir su BD enfocada.
  - Reemplazo y descarte definitivo del visor web Adminer, manteniendo Nginx limpio.
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
