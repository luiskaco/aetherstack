# Tareas

> Solo lo abierto. Al cerrar una tarea, se borra de acá y deja una línea en
> `04_CHANGELOG.md`. El avance va en los commits, no acá.
> Como mucho 10 abiertas: si hay más, cerrar o descartar antes de sumar otra.

## Dónde quedó

- **Última actualización:** 2026-11-14
- **Dónde quedó:** v1.2.6 publicada, estable. App de escritorio portable para Windows 10/11 x64 (`AetherStack.bat`). La migración desde Laragon está hecha: los 16 sitios responden desde `developOrange\web`. Rama `docs/migrate-docs`: migración de `docs/` a la estructura nueva.
- **Próximo paso:** T-01 (el `taskkill` mata procesos ajenos). Para publicar un release, seguir `RUNBOOK.md` § 5.
- **Bloqueos:** ninguno. Falta desinstalar Laragon, que decide el usuario conservando `respaldo-laragon-2026-11-09`.

## Abiertas

- [ ] **T-01 — `taskkill /IM` mata procesos ajenos con el mismo nombre** · auditoría 2026-11-10
  Hecho cuando: `core.py` y `stop.bat` cierran solo los procesos cuya ruta de ejecutable está dentro de AetherStack.
- [ ] **T-02 — MariaDB `root` sin contraseña**
  Hecho cuando: cada proyecto tiene su propio usuario (en el `.env` de Laravel o el `wp-config.php`) y la interfaz avisa del riesgo.
- [ ] **T-03 — Los `except Exception: pass` esconden errores**
  Hecho cuando: cada uno registra el error en `logs/aetherstack.log`.
- [ ] **T-04 — `core.py` reescribe configuraciones al importarse**
  Hecho cuando: esa lógica vive en una función `init()` que llama `app.py`, y importar `core` no toca archivos.
- [ ] **T-05 — Dos fuentes de verdad para la versión de PHP**
  Hecho cuando: `start.bat` y `switch-php.bat` usan `state.json` como la app, y desaparece el enlace `current` que la app no usa (hoy `start.bat` fija PHP 8.4).
- [ ] **T-06 — Ampliar los tests de `core.py`**
  Hecho cuando: hay pruebas de la validación de nombres y de la generación de configuraciones, y `TESTING.md` lista qué requisito cubre cada una. Corren con `python -m unittest discover -s tests -v`.
- [ ] **T-07 — Cerrar la migración desde Laragon**
  Hecho cuando: se decide qué hacer con `PorUnPeruSkeletonHTML` (sitio estático sin virtual host, AetherStack solo adopta WordPress y Laravel) y con las bases `observatorioweb` y `pluginglobal` sin proyecto; se borra a mano `*.salvage.sql` si ya no hace falta; y se desinstala Laragon cuando el usuario lo decida.
- [ ] **T-08 — Carpetas con nombres no válidos en la lista de proyectos**
  Hecho cuando: se decide si la lista las muestra (hoy se ocultan).
- [ ] **T-09 — Ideas a futuro**
  Hecho cuando: se decide cuáles se hacen: HTTPS local automático con certificados SSL, Node.js y NPM en la terminal integrada, exportar una base a `.sql` desde la pestaña de proyectos, y un manifiesto para Scoop o winget (paso 3 de las actualizaciones automáticas).
