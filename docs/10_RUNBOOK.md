# 10 - Runbook & Operations: AetherStack

## 1. Operación Diaria

### Iniciar la Suite
- Haz doble clic en el acceso directo de tu Escritorio: **AetherStack**.
- O ejecuta:
  ```bash
  D:\LabIA\aetherstack\AetherStack.bat
  ```

### Iniciar por Consola (Headless / sin ventana)
```bash
cd D:\LabIA\aetherstack
start.bat
```

### Detener Todos los Servicios
```bash
cd D:\LabIA\aetherstack
stop.bat
```

---

## 2. Diagnóstico y Logs

Si algún servicio no responde, revisa los logs en `D:\LabIA\aetherstack\logs\`:
- **Nginx:** `logs/nginx_error.log`
- **PHP:** `logs/php_error.log`
- **MariaDB:** `logs/mariadb_error.log`

---

## 3. Respaldo y Migración
Para mover AetherStack a otra máquina o disco:
1. Copia la carpeta completa `D:\LabIA\aetherstack`.
2. Las bases de datos se encuentran intactas en `data/mariadb/`.
3. Todo es 100% portable y no requiere instalación en el registro de Windows.
