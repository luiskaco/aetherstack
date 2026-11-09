# 10 - Runbook & Operations: AetherStack

## 1. Operación Diaria

### Iniciar la Suite
- Haz doble clic en `AetherStack.bat`, o en el acceso directo del Escritorio si lo creaste con `python generate_icon.py`.
- O ejecuta desde la carpeta del proyecto:
  ```cmd
  AetherStack.bat
  ```

### Iniciar por Consola (Headless / sin ventana)
```cmd
start.bat
```

### Detener Todos los Servicios
```cmd
stop.bat
```

---

## 2. Diagnóstico y Logs

Si algún servicio no responde, revisa los registros en la carpeta `logs/`:
- **Nginx:** `logs/nginx_error.log`
- **PHP:** `logs/php_error.log`
- **MariaDB:** `logs/mariadb_error.log`

---

## 3. Respaldo y Migración
Para mover AetherStack a otra máquina o disco:
1. Copia la carpeta completa `aetherstack/`.
2. Las bases de datos se encuentran intactas en `data/mariadb/`.
3. Todo es 100% portable y no requiere instalación en el registro de Windows.

---

## 4. Seguridad de Red (Verificación)
Con el stack iniciado, nada debe responder desde otra máquina de la red:
```cmd
netstat -ano | findstr LISTENING | findstr ":80 :3307 :9000"
```
Las tres líneas deben mostrar `127.0.0.1:<puerto>`. Si aparece `0.0.0.0` o `[::]`, detén el stack y revisa `conf/nginx.conf` y `conf/my.ini`.

---

## 5. Publicar un Release
0. **Regla de compatibilidad (obligatoria).** El actualizador de cada versión instala solo los archivos que conoce. Si el release trae un archivo nuevo en la raíz que las versiones anteriores no aceptan, quien actualice con un clic quedará con la app rota. Antes de publicar corre `python -m unittest discover -s tests`: `test_compat.py` lo comprueba contra el `updater.py` real de las versiones de `SUPPORTED_ONE_CLICK_FROM`. Tras publicar, añade la versión nueva a esa lista y, para las que ya no sean compatibles, retira los assets de actualización (`AetherStack-update-*`) de su release con `gh release delete-asset`. Si un cambio es incompatible con las versiones instaladas (archivos nuevos, otro formato de firma), **cambia el prefijo de los assets** (`AetherStack-update-` → otro) en `core.py` y en el build: las versiones antiguas buscan el prefijo viejo y dejan de ver el paquete, así que no pueden romperse. Nunca publiques un paquete de actualización que alguna versión instalada no sepa instalar entero.
1. Verifica que el árbol esté limpio (`git status`), actualiza `docs/08_CHANGELOG.md` y sube `VERSION` en `core.py` al número del release. Sin esto, los usuarios verían el aviso de actualización aunque ya estén al día.
2. Genera el paquete con lista blanca y escaneo de datos personales:
   ```cmd
   python tools/build_release_zip.py 1.2.1
   ```
   Genera cuatro archivos en `dist/`: el paquete portable completo y su `.sha256`, y el zip liviano `AetherStack-update-vX.Y.Z.zip` (solo código) con su firma `.sig`. Publica también el `.sha256` del portable para que quien lo descargue a mano pueda comprobarlo. El zip de actualización y la firma alimentan el botón "Actualizar ahora" de la app. Si falta la firma, la app solo muestra "Ver novedades". El build se niega a terminar si no encuentra tu clave de firma.
   El build **aborta y borra el zip** si encuentra tu usuario de Windows, tu email de git, el nombre del equipo, `data/`, `logs/`, `state.json`, vhosts o archivos `.lnk`.
3. Prueba el zip en una carpeta nueva: descomprime, arranca el stack y comprueba que Nginx, PHP y MariaDB quedan activos.
4. Crea el tag y publica el asset:
   ```cmd
   git tag v1.2.1
   git push origin main v1.2.1
   gh release create v1.2.1 dist/AetherStack-v1.2.1-portable.zip dist/AetherStack-v1.2.1-portable.zip.sha256 dist/AetherStack-update-v1.2.1.zip dist/AetherStack-update-v1.2.1.zip.sig --title "AetherStack v1.2.1" --notes-file <archivo-de-notas>
   ```
   **Importante:** los assets deben llevar exactamente esos nombres. La app reconoce la actualización por el patrón `AetherStack-update-vX.Y.Z.zip` y `.zip.sig`.
   La actualización con un clic solo cambia código. Si un release cambia los binarios de `bin/` (Nginx, PHP, MariaDB), hay que avisar en las notas de que se debe descargar el paquete portable.
5. Nunca empaquetes a mano la carpeta del proyecto: `data/` contiene bases de datos reales y el perfil del navegador.

---

## 6. Clave de firma de releases
- **Dónde está:** `~/.aetherstack-signing/release.key` (carpeta personal de Windows, permisos solo para tu usuario). Nunca dentro del repositorio. Se puede usar otra ruta con la variable `AETHERSTACK_SIGNING_KEY`.
- **Copia de seguridad:** guarda una copia en tu gestor de contraseñas. Si la pierdes no puedes firmar nuevos releases, y las instalaciones existentes rechazarían los que firmes con una clave nueva: tendrías que publicar a mano una versión con la clave pública nueva y pedir a la comunidad que la descargue.
- **Si se filtra:** genera otra (`python tools/sign_release.py init` tras mover la anterior), cambia `RELEASE_PUBLIC_KEY` en `updater.py`, publica la versión nueva a mano y avisa a la comunidad. Quien tenga la clave vieja podría firmar releases falsos para las instalaciones antiguas.
- **Ver la clave pública:** `python tools/sign_release.py pubkey`. Debe coincidir con `RELEASE_PUBLIC_KEY` en `updater.py`.

---

## 7. Migrar desde Laragon
Probado con el proyecto piloto `frutiflex`. Laragon no se modifica en ningún paso.

1. **Cierra Laragon** (puertos 80 y 3306 libres). Sus archivos de `www` no se copian: en Ajustes apunta AetherStack a esa carpeta (o muévela después, mismo disco = instantáneo).
2. **Exporta cada base con el MySQL de Laragon** (no se puede copiar la carpeta de datos: MySQL 8.4 y MariaDB 11.8 son distintos por dentro). Levanta su `mysqld` con su `my.ini`, exporta y apágalo con `mysqladmin shutdown`:
   ```cmd
   mysqldump --user=root --host=127.0.0.1 --port=3306 --single-transaction --routines --triggers --events --default-character-set=utf8mb4 --no-tablespaces --result-file=nombre.sql nombre_bd
   ```
   En PowerShell escribe `--host=127.0.0.1`; con `-h127.0.0.1` el punto corta el argumento. Los volcados contienen datos de clientes: guárdalos fuera del repositorio.
3. **Ajustes de AetherStack:** carpeta de proyectos = `C:/laragon/www`, puerto de MariaDB = `3306` (así no cambia ningún `wp-config.php`) y `vhost_tld` = `test`.
4. **Importa** con el mismo nombre de base que usa el `wp-config.php`: `CREATE DATABASE ... utf8mb4_0900_ai_ci` (MariaDB 11.8 la entiende) y `mariadb --database=nombre < nombre.sql`.
5. **Adopta los proyectos y escribe los dominios en `hosts`:** Ajustes > "Importar proyectos y hosts" (equivale a `core.adopt_existing_projects()` + `core.sync_hosts()`). Windows pedirá permiso de administrador; AetherStack solo escribe su propio bloque y guarda `conf/hosts.backup`. Para quitar el bloque, ejecuta `hosts.apply_block(texto, [])` o borra las líneas entre las marcas `# >>> AetherStack` y `# <<< AetherStack <<<`. Después comprueba `http://nombre.test` (portada, `wp-login.php`, API REST). Los dominios `.test` ya están en el archivo `hosts` porque Laragon los añadió.
6. **Revisa los sitios uno a uno** (portada, `wp-login.php`). Si un sitio viejo llena `logs/php_error.log` con `Duplicate entry '0' for key 'PRIMARY'`, sus tablas perdieron el `AUTO_INCREMENT` (le pasaba a `legacy-panasa` en Laragon: 25 tablas de WooCommerce y Action Scheduler). No lo causa la migración. Se repara solo en la copia de AetherStack con `ALTER TABLE ... MODIFY col <tipo> NOT NULL AUTO_INCREMENT`, sin tocar las dos claves naturales de WooCommerce (`wp_wc_order_stats`, `wp_wc_product_meta_lookup`). Si una tabla tiene una fila con id 0, hazlo con `SET SESSION sql_mode=CONCAT(@@sql_mode,',NO_AUTO_VALUE_ON_ZERO')`.
7. **Rendimiento:** AetherStack ajusta OPcache y `realpath_cache` en cada arranque (`phpini.py`). Si un sitio tarda decenas de segundos, mira primero la CPU de los `php-cgi`: con la caché llena PHP recompila todo en cada petición.
8. **Mover `www` a la carpeta definitiva** (probado el 2026-11-09; falló por un proceso que retenía la carpeta). Antes: cierra Laragon, terminales, editores y sesiones de Claude con carpetas dentro de `www`; si el movimiento da "Acceso denegado", hay un proceso retenido (busca en `Win32_Process` líneas de comandos que mencionen la ruta). Pasos: detener el stack; la carpeta destino debe estar vacía (o contener solo el `index.html` que genera AetherStack); renombrar `www` al destino (mismo disco = instantáneo); `core.update_global_config({"projects_dir": <destino>})`; `core.adopt_existing_projects()` para regenerar los virtual hosts con la ruta nueva (los dominios del `hosts` no cambian); iniciar el stack y verificar los sitios. Si algo falla, el movimiento se revierte renombrando de vuelta.
9. Solo cuando `www` ya esté movida y los sitios verificados desde la ruta nueva, desinstala Laragon. Antes de hacerlo, conserva `respaldo-laragon-*` (copia de las bases) hasta estar seguro de que no la necesitas.
