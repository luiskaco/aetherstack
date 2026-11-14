# AGENTS.md

Lo esencial de este proyecto para cualquier persona o IA que trabaje en él
(estándar abierto [AGENTS.md](https://agents.md)). Cómo trabajar lo decide cada
uno; lo de acá vale para todos.

## Qué es

AetherStack: entorno de desarrollo local portable y libre para Windows 10/11 x64, hecho para desarrolladores PHP, WordPress y Laravel. Alternativa a Laragon y XAMPP. Corre Nginx, PHP y MariaDB sin instalación invasiva, con una app de escritorio para manejarlos.

## Stack y comandos

- **Stack:** Python 3.12+ con CustomTkinter (interfaz, Material Design 3). Binarios portables en `bin/`: Nginx, PHP 8.4 y 8.5, MariaDB, Composer y HeidiSQL.
- **Instalar:** `python -m pip install -r requirements.txt` · **Dev:** `AetherStack.bat` · **Test:** `python -m unittest discover -s tests -v`
- **Release:** seguir `docs/RUNBOOK.md` § 5; no hay build aparte (el release es un zip de código firmado).

## Estructura

- `app.py` — interfaz de escritorio. `core.py` — motor: procesos, puertos, virtual hosts y bases de datos.
- `updater.py`, `sigverify.py` — actualización con un clic y verificación de la firma.
- `conf/` — configuración; `conf/state.json` guarda el estado. `bin/` y `data/` no se versionan.
- `tests/` — pruebas. `tools/` — empaquetado y firma de releases. `docs/` — documentación.

## No negociable

- Nunca se versionan secretos ni credenciales: la clave privada de firma de releases vive en el PC del autor, fuera del repo.
- Los datos personales de usuarios o clientes no salen del entorno previsto.
- **Compatibilidad del actualizador:** cada versión instala solo los archivos que conoce. Un archivo nuevo en la raíz puede dejar rota a una instalación que actualiza con un clic. Antes de publicar, correr los tests (`test_compat.py`) y seguir la regla de `docs/RUNBOOK.md` § 5 (ADR-002).
- MariaDB escucha en el puerto 3307 y todo queda en `127.0.0.1`: el 3306 suele estar ocupado por Docker o WSL (ADR-004).
- Solo se listan y se pueden borrar proyectos WordPress y Laravel (ADR-005).

## Para continuar

1. Leer **Dónde quedó** en `docs/02_TASKS.md` y el índice de
   `docs/03_DECISIONS.md`: lo ya decidido no se vuelve a decidir.
2. Al cerrar una tarea, sacarla de `docs/02_TASKS.md` y dejar una línea en
   `docs/04_CHANGELOG.md`.
