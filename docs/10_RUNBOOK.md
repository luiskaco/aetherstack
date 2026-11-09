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
1. Verifica que el árbol esté limpio (`git status`), actualiza `docs/08_CHANGELOG.md` y sube `VERSION` en `core.py` al número del release. Sin esto, los usuarios verían el aviso de actualización aunque ya estén al día.
2. Genera el paquete con lista blanca y escaneo de datos personales:
   ```cmd
   python tools/build_release_zip.py 1.2.1
   ```
   Genera seis archivos en `dist/`: el paquete portable completo y su `.sha256`, el zip liviano `AetherStack-code-vX.Y.Z.zip` (solo código), su `.sha256` y su firma `.sig`. Publica también el `.sha256` del portable para que quien lo descargue a mano pueda comprobarlo. El zip de código y la firma alimentan el botón "Actualizar ahora" de la app. Si falta la firma, la app solo muestra "Ver novedades". El build se niega a terminar si no encuentra tu clave de firma.
   El build **aborta y borra el zip** si encuentra tu usuario de Windows, tu email de git, el nombre del equipo, `data/`, `logs/`, `state.json`, vhosts o archivos `.lnk`.
3. Prueba el zip en una carpeta nueva: descomprime, arranca el stack y comprueba que Nginx, PHP y MariaDB quedan activos.
4. Crea el tag y publica el asset:
   ```cmd
   git tag v1.2.1
   git push origin main v1.2.1
   gh release create v1.2.1 dist/AetherStack-v1.2.1-portable.zip dist/AetherStack-code-v1.2.1.zip dist/AetherStack-code-v1.2.1.zip.sha256 dist/AetherStack-code-v1.2.1.zip.sig --title "AetherStack v1.2.1" --notes-file <archivo-de-notas>
   ```
   **Importante:** los cuatro assets deben llevar exactamente esos nombres. La app los reconoce por el patrón `AetherStack-code-vX.Y.Z.zip` y `.zip.sig`. Mantén publicado el `.sha256`: las instalaciones v1.2.1 solo lo conocen a él.
   La actualización con un clic solo cambia código. Si un release cambia los binarios de `bin/` (Nginx, PHP, MariaDB), hay que avisar en las notas de que se debe descargar el paquete portable.
5. Nunca empaquetes a mano la carpeta del proyecto: `data/` contiene bases de datos reales y el perfil del navegador.

---

## 6. Clave de firma de releases
- **Dónde está:** `~/.aetherstack-signing/release.key` (carpeta personal de Windows, permisos solo para tu usuario). Nunca dentro del repositorio. Se puede usar otra ruta con la variable `AETHERSTACK_SIGNING_KEY`.
- **Copia de seguridad:** guarda una copia en tu gestor de contraseñas. Si la pierdes no puedes firmar nuevos releases, y las instalaciones existentes rechazarían los que firmes con una clave nueva: tendrías que publicar a mano una versión con la clave pública nueva y pedir a la comunidad que la descargue.
- **Si se filtra:** genera otra (`python tools/sign_release.py init` tras mover la anterior), cambia `RELEASE_PUBLIC_KEY` en `updater.py`, publica la versión nueva a mano y avisa a la comunidad. Quien tenga la clave vieja podría firmar releases falsos para las instalaciones antiguas.
- **Ver la clave pública:** `python tools/sign_release.py pubkey`. Debe coincidir con `RELEASE_PUBLIC_KEY` en `updater.py`.
