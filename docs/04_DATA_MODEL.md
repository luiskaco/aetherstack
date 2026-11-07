# 04 - Data Model & Persistence: AetherStack

## 1. Persistencia de Configuración
La configuración de usuario y estado del entorno se guarda en `conf/state.json`:

```json
{
  "php_version": "8.4",
  "nginx_port": 80,
  "mariadb_port": 3307,
  "php_port": 9000,
  "projects_dir": "D:\\LabIA"
}
```

---

## 2. Bases de Datos de Proyectos
- **Almacenamiento físico:** `data/mariadb/` (aislado del sistema operativo).
- **Convención de nomenclatura:**
  - Proyecto: `nombre-proyecto`
  - Base de datos creada: `nombre_proyecto_db`
- **Credenciales por defecto:**
  - Host: `127.0.0.1`
  - Puerto: `3307`
  - Usuario: `root`
  - Contraseña: `""` (vacía para desarrollo local)
