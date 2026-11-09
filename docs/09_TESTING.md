# 09 - Testing & Verification: AetherStack

## 1. Estrategia de Pruebas

| Requisito | Prueba Ejecutada | Resultado |
|---|---|---|
| **RF-01 (Nginx + PHP)** | Solicitud HTTP a script de prueba con `phpinfo()` | ✅ Código 200, PHP ejecutando en FastCGI. |
| **RF-02 (Multi-PHP)** | Cambio en caliente de 8.4 a 8.5 vía UI / CLI | ✅ Respuesta `AETHER_PHP_VERSION: 8.5.12`. |
| **RF-03 (MariaDB)** | Conexión PDO desde PHP y comando `SHOW DATABASES` | ✅ Conexión exitosa en puerto `3307`. |
| **RF-04 (WordPress)** | Creación de proyecto de prueba `Hola` | ✅ Base de datos `hola_db` creada y `wp-config.php` generado. |
| **RF-05 (Filtro Proyectos)** | Detección de proyectos en la carpeta raíz | ✅ Solo detecta proyectos WordPress y Laravel; ignora carpetas no web. |
| **RF-06 (Borrado Proyectos)** | Borrado de proyecto de prueba con DB | ✅ Carpeta, base de datos y vhost eliminados. |
| **RNF-03 (UI M3)** | Apertura nativa con CustomTkinter | ✅ Sin deadlocks COM, renderizado instantáneo. |

---

## 2. Pruebas automáticas
Se ejecutan con la biblioteca estándar, sin dependencias:
```cmd
python -m unittest discover -s tests -v
```

| Requisito | Prueba | Resultado |
|---|---|---|
| **Actualizador y firmas** (`updater.py`, `sigverify.py`) | `tests/test_updater.py`: vector oficial RFC 8032; aplica una actualización firmada y conserva `data/`; rechaza firma de otra clave, zip alterado tras firmar, zip viejo reutilizado con otra versión, firma ausente o basura, rutas con `..` y código con errores aunque estén firmados; vuelve atrás si falla la escritura; rechaza URLs ajenas; lista blanca de rutas | ✅ 14 pruebas |
| **Verificador vs. referencia** | 25 rondas de claves y mensajes aleatorios contra la biblioteca `cryptography` (firmas idénticas, verificación cruzada, casos negativos) | ✅ |
| **Firma real** | Zip firmado con la clave del autor aplicado sobre una copia de v1.2.1; misma firma con otra versión declarada | ✅ aceptado / ✅ rechazado |
| **Actualización de punta a punta** | Zip de código real aplicado sobre una copia de v1.2.0 en una carpeta aparte | ✅ 23 archivos actualizados, dato de usuario intacto, copia de respaldo creada |
| **Banner con un clic** | Release simulado con assets: botón "Actualizar ahora" / "Update now" y cambio de idioma | ✅ |
| **Descarga real (v1.2.1)** | `check_for_update` + `download_and_apply` contra los assets publicados en GitHub, sobre una copia de v1.2.0 | ✅ 23 archivos actualizados, datos intactos, `core.py` pasó a 1.2.1 |
| **Descargas verificadas** (`downloads.py`) | `tests/test_downloads.py`: descarga y verificación, hash distinto descartado sin dejar archivos, reutiliza caché, renueva si cambió el hash oficial, reemplaza una caché corrupta, sin red (con caché íntegra / sin caché / con caché corrupta), rechaza HTTP, límite de tamaño | ✅ 11 pruebas |
| **WordPress real** | Descarga real de wordpress.org verificada (35 MB), segunda vez reutiliza la caché; proyecto WordPress creado de punta a punta con el stack real y borrado después | ✅ |
| **Dependencias ausentes** | `app.py` sin `customtkinter`: aviso con el comando de instalación y salida limpia | ✅ |
| **Bandeja y copia única** (`tray.py`, `single_instance.py`) | `tests/test_tray.py`: estado del stack, color por estado, icono distinguible a 16 px y con esquinas transparentes, bloqueo de copia única y aviso entre copias | ✅ 6 pruebas |
| **Bandeja con la app real** | App abierta de verdad: icono visible y verde con el stack activo, menú correcto, la X oculta la ventana (no la destruye), una segunda copia la muestra, salir desde la bandeja pregunta | ✅ |
| **Copia única con procesos reales** | Dos lanzamientos con `pythonw.exe app.py` | ✅ un solo proceso y una sola ventana |
| **Ajuste de php.ini** (`phpini.py`) | `tests/test_phpini.py`: reemplaza valores existentes, no toca otros ajustes, añade los que faltan en un solo bloque marcado, idempotente, respeta líneas comentadas | ✅ 6 pruebas |
| **Rendimiento real (16 sitios)** | Portadas de los sitios más lentos antes/después de ajustar OPcache y el pool de PHP | ✅ de 30-120 s a 2-5 s |
