# Requisitos (PRD): AetherStack

## 1. Visión del Producto
AetherStack es un entorno de desarrollo local ultraligero, 100% libre y portable para Windows, diseñado para desarrolladores PHP que buscan reemplazar herramientas lentas o con modelos de licencia invasivos (como Laragon o XAMPP).

---

## 2. Requisitos Funcionales (RF)

| ID | Requisito | Criterios de Aceptación |
|---|---|---|
| **RF-01** | Stack Web Completo | Nginx Web Server, PHP 8.4, PHP 8.5 y MariaDB portables sin instalación invasiva. |
| **RF-02** | Selector PHP en Caliente | Alternar entre PHP 8.4 y 8.5 de forma instantánea sin reiniciar manualmente los servicios. |
| **RF-03** | Creador Rápido de Laravel | Creación de proyecto vía Composer, configuración automática de base de datos en MariaDB y generación de `.env` y virtual host local. |
| **RF-04** | Creador Rápido de WordPress | Descarga y descompresión del núcleo oficial de WordPress, creación de base de datos y configuración automática de `wp-config.php`. |
| **RF-05** | Filtro Estricto de Proyectos | La pestaña "Mis Proyectos" solo lista aplicaciones verificadas de Laravel y WordPress, omitiendo carpetas o utilidades genéricas. |
| **RF-06** | Eliminación Integral | Opción de eliminar un proyecto borrando los archivos en disco, la base de datos asociada en MariaDB y su archivo Virtual Host. |
| **RF-07** | Configuración Global | Modal para cambiar la carpeta de proyectos raíz y los puertos de escucha de Nginx y MariaDB. |

---

## 3. Requisitos No Funcionales (RNF)

| ID | Requisito | Criterios de Aceptación |
|---|---|---|
| **RNF-01** | Cero Licencias / Mensajes | 100% código abierto y libre. Sin avisos de donación, licencias ni telemetría. |
| **RNF-02** | Rendimiento y Portabilidad | Todos los binarios residen en `bin/`. Consumo de RAM inferior a 120 MB en reposo. |
| **RNF-03** | Interfaz Material Design 3 | UI nativa basada en especificaciones de Material You / M3 en modo oscuro. |
| **RNF-04** | Compatibilidad de Puertos | MariaDB por defecto en puerto `3307` para evitar colisiones con Docker Desktop o WSL. |
