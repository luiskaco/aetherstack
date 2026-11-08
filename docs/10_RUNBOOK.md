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
1. Verifica que el árbol esté limpio (`git status`) y actualiza `docs/08_CHANGELOG.md`.
2. Genera el paquete con lista blanca y escaneo de datos personales:
   ```cmd
   python tools/build_release_zip.py 1.1.0
   ```
   El build **aborta y borra el zip** si encuentra tu usuario de Windows, tu email de git, el nombre del equipo, `data/`, `logs/`, `state.json`, vhosts o archivos `.lnk`.
3. Prueba el zip en una carpeta nueva: descomprime, arranca el stack y comprueba que Nginx, PHP y MariaDB quedan activos.
4. Crea el tag y publica el asset:
   ```cmd
   git tag v1.1.0
   git push origin main v1.1.0
   gh release create v1.1.0 dist/AetherStack-v1.1.0-portable.zip --title "AetherStack v1.1.0" --notes-file <archivo-de-notas>
   ```
5. Nunca empaquetes a mano la carpeta del proyecto: `data/` contiene bases de datos reales y el perfil del navegador.
