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
| **Actualizador** (`updater.py`) | `tests/test_updater.py`: aplica la actualización y conserva `data/`; rechaza hash incorrecto, rutas con `..`, código con errores de sintaxis y paquetes incompletos; vuelve atrás si falla la escritura; rechaza URLs ajenas al repositorio; lista blanca de rutas | ✅ 8 pruebas |
| **Actualización de punta a punta** | Zip de código real aplicado sobre una copia de v1.2.0 en una carpeta aparte | ✅ 23 archivos actualizados, dato de usuario intacto, copia de respaldo creada |
| **Banner con un clic** | Release simulado con assets: botón "Actualizar ahora" / "Update now" y cambio de idioma | ✅ |
| **Pendiente** | Descarga real desde GitHub: solo se puede probar con un release publicado que traiga los assets de código | ⏳ |
