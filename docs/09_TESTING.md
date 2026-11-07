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
