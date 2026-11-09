# 08 - Changelog: AetherStack

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto adhiere a [Semantic Versioning](https://semver.org/).

---

## [1.2.4] - 2026-11-09

### Corregido
- **La actualización con un clic podía dejar la app sin arrancar.** El actualizador de cada versión solo instala una lista fija de archivos; si el release nuevo traía un archivo nuevo (`sigverify.py` en v1.2.2, `downloads.py` en v1.2.3), las versiones anteriores lo ignoraban y el código nuevo fallaba con `ModuleNotFoundError`. Se retiraron los archivos de actualización de los releases v1.2.2 y v1.2.3; quien tenga v1.2.1 o v1.2.2 debe descargar el paquete portable completo.
- El actualizador ahora **rechaza el paquete entero** si trae algo que esa versión no sabe instalar, con un mensaje que pide bajar el portable, en vez de instalar a medias.
- Los módulos `.py` nuevos de la raíz se aceptan sin cambiar la lista, para que los próximos releases puedan añadirlos sin romper esta versión.

### Añadido
- `tests/test_compat.py`: comprueba el paquete actual contra la lista de archivos del `updater.py` real de las versiones publicadas. Habría detectado este error antes de publicar.

---

## [1.2.3] - 2026-11-09

### Seguridad
- **Descarga de WordPress verificada:** se comprueba contra el hash que publica wordpress.org (`latest.zip.sha1`, por HTTPS) antes de usarla. Se descarta cualquier archivo que no coincida. Nginx, PHP, MariaDB y Composer no se descargan en ejecución: vienen dentro del paquete portable.
- Límite de tamaño y de tiempo en las descargas, y solo HTTPS.
- Cada release publica también el `.sha256` del paquete portable, para comprobarlo a mano.

### Corregido
- Si la descarga de WordPress se cortaba, el zip incompleto quedaba guardado y se reutilizaba siempre, rompiendo la creación de proyectos. Ahora se escribe en un archivo temporal y solo se guarda si es válido.
- La copia en caché de WordPress ya no se queda para siempre en la primera versión descargada: se renueva cuando wordpress.org publica una nueva. Sin internet se usa la copia local si está íntegra.

### Añadido
- `requirements.txt` con las dependencias fijadas (`customtkinter`, `pillow`) y su instalación en el README.
- Si faltan las dependencias, la app muestra un aviso con el comando a ejecutar en vez de cerrarse sin explicación.
- Pruebas automáticas de las descargas verificadas (11 casos).

---

## [1.2.2] - 2026-11-09

### Seguridad
- **Releases firmados (Ed25519):** la app solo instala actualizaciones firmadas con la clave del autor. La clave privada vive fuera del repositorio; la app lleva solo la pública. La firma cubre la versión y el contenido, así que ni un release publicado por un tercero ni un zip antiguo reutilizado se instalan.
- Verificador de firmas propio, sin dependencias nuevas (`sigverify.py`), validado con los vectores oficiales del RFC 8032 y contra la biblioteca `cryptography`.
- Herramienta `tools/sign_release.py` para crear la clave y firmar; el build genera el `.sig` y se niega a terminar sin él.

---

## [1.2.1] - 2026-11-09

### Añadido
- **Actualización con un clic:** si el release trae el zip de código y su SHA256, el aviso muestra "Actualizar ahora". La app descarga, verifica la integridad, reemplaza solo el código y se reinicia. No toca `bin/`, `data/`, `conf/`, `logs/` ni `projects/`.
- Copia de respaldo en `.update-backup/` y vuelta atrás automática si algo falla. Rechaza rutas peligrosas, código con errores de sintaxis y URLs ajenas al repositorio.
- El build genera además `AetherStack-code-vX.Y.Z.zip` y su `.sha256`.
- Primeras pruebas automáticas (`tests/test_updater.py`).

---

## [1.2.0] - 2026-11-09

### Añadido
- **Aviso de actualización:** al abrir, la app consulta en segundo plano el último release de GitHub y, si hay una versión más nueva, muestra un aviso con botón "Ver novedades". No descarga ni instala nada por sí sola.
- **Página de inicio por defecto:** `http://localhost` muestra una bienvenida con la lista de proyectos en vez de `403 Forbidden`. Se regenera sola al crear o eliminar proyectos y nunca pisa un `index` propio del usuario. Sigue sin haber listado de carpetas.
- La versión actual (`VERSION` en `core.py`) se muestra en el título de la ventana.
- Se puede desactivar con `"check_updates": false` en `conf/state.json`.

---

## [1.1.1] - 2026-11-08

### Rendimiento
- El estado de los servicios se consulta con la API de Windows (instantánea de procesos) en lugar de lanzar `tasklist` varias veces: `get_status()` pasa de ~970 ms a ~13 ms.
- Antes, la interfaz se congelaba cerca de 1 s cada 3 s al refrescar el estado; ahora no hay pausas perceptibles.
- El arranque de la interfaz baja de ~4,2 s a ~2,5 s. El resto es dibujado de widgets de customtkinter.

### Interfaz
- Mejor contraste: el texto azul pasa de `#2563EB` (3,4:1) a `#60A5FA` (7:1) y el texto de los badges OFFLINE/STANDBY se aclara (12:1).
- El título de la tabla de proyectos pasa a ser solo "Mis Proyectos" / "My Projects".

---

## [1.1.0] - 2026-11-08

### Seguridad
- **Nginx solo en local:** el servidor y los virtual hosts escuchan en `127.0.0.1` (antes en todas las interfaces, accesibles desde la red local). Se desactiva el listado de carpetas (`autoindex`) y se bloquea el acceso web a la carpeta de AetherStack (código, `data/`, `logs/`).
- **Validación de nombres de proyecto** (`^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`) y comprobación de que la ruta queda dentro de la carpeta de proyectos. Evita path traversal al crear/eliminar e inyección en SQL, en la config de Nginx y en comandos de shell.
- Se eliminan los `os.system` de la interfaz: carpetas con `os.startfile`, URLs con `webbrowser` y terminal con `subprocess` (sin shell).
- Ajustes: se validan los puertos (1-65535 y distintos) y que la carpeta de proyectos exista.
- Los vhosts antiguos que escuchaban en todas las interfaces se migran a `127.0.0.1` automáticamente.

### Cambiado
- La carpeta de proyectos por defecto en instalaciones nuevas es `aetherstack/projects` (antes, la carpeta padre de donde se descomprimía).
- Los proyectos con nombres fuera de la regla anterior no aparecen en la lista.
- `conf/state.json`, `conf/nginx.conf`, `conf/my.ini` y `AetherStack.lnk` dejan de versionarse: se generan en el primer arranque o con `python generate_icon.py`.

### Corregido
- Nginx no arrancaba en una copia nueva: faltaban `bin/nginx/temp` y `bin/nginx/logs`. Ahora se crean solos.

### Release
- Nuevo `tools/build_release_zip.py`: lista blanca, base MariaDB vacía generada en el momento y escaneo de datos personales que aborta el build.
- **El asset de v1.0.0 incluía el perfil del navegador y las bases de datos del autor; se retira y se sustituye por v1.1.0.**

---

## [1.0.8] - 2026-11-08

### Añadido
- Documentación completa bilingüe en `README.md` con **Inglés como sección principal superior** (English-first) para máxima visibilidad internacional en GitHub y versión en **Español** accesible inmediatamente a continuación:
  - Selector de idioma con anclas de salto rápido en la cabecera (`English 🇺🇸` / `Español 🇪🇸`).
  - Tabla comparativa de rendimiento frente a Laragon, Docker Desktop y XAMPP en ambos idiomas.
  - Guías de inicio rápido, conmutador PHP 8.1 a 8.5, base de datos MariaDB en puerto 3307, integración con HeidiSQL Portable y matriz de `/docs`.

## [1.0.7] - 2026-11-07

### Añadido
- Integración de **HeidiSQL Portable v12.22** (el gestor oficial de Laragon) en `bin/heidisql/`:
  - Aplicación de escritorio nativa de Windows con interfaz profesional moderna, edición de celdas en cuadrícula tipo hoja de cálculo, diseñador de tablas y creador visual de esquemas.
  - Asistente de importación y exportación de archivos `.sql` y copias de seguridad con barra de progreso.
  - Editor de consultas SQL de alto rendimiento con autocompletado y resaltado de sintaxis.
  - Modo 100% portable (`portable_settings.txt`) preconfigurado en modo oscuro (`Windows10 Dark`) con conexión directa a MariaDB en `127.0.0.1:3307`.
  - Conexión instantánea desde el botón **"Gestor DB"**, botón en el panel de MariaDB y botón por proyecto para enfocar su base de datos específica.

### Eliminado
- Descarte del visor web Adminer, eliminando advertencias de PHP y manteniendo Nginx optimizado y libre de puertos secundarios.

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
