# AetherStack ⚡

> **The weightless local PHP stack.**
> Entorno de desarrollo local moderno, ultraligero y portable para Windows (Laravel, WordPress y proyectos PHP).

---

## 🚀 Características

- **Cero licencias / Sin mensajes molestos:** 100% libre, portable e independiente.
- **Doble motor PHP actualizado:** Soporte nativo para **PHP 8.4** y **PHP 8.5** con cambio en caliente con 1 clic.
- **Nginx Web Server:** Servidor de alto rendimiento configurado con FastCGI y reescritura de URLs para Laravel (`/public`) y WordPress.
- **MariaDB portable:** Base de datos lista en el puerto `3307` (sin colisionar con Docker u otros servicios).
- **Composer integrado:** Herramienta oficial de dependencias PHP lista para usar.
- **Creación rápida de proyectos:**
  - **Laravel:** Descarga con Composer, crea base de datos automática y configura `.env`.
  - **WordPress:** Descarga última versión oficial, crea base de datos y genera `wp-config.php`.
- **UI Minimalista:** Panel de control nativo en modo oscuro con indicadores de estado de servicios en tiempo real.

---

## 📂 Estructura del Proyecto

```text
D:\LabIA\aetherstack\
├── bin\               # Binarios portables (Nginx, PHP 8.4, PHP 8.5, MariaDB, Composer)
├── conf\              # Configuraciones maestras (nginx.conf, my.ini, vhosts)
├── data\              # Almacenamiento local de bases de datos MariaDB
├── logs\              # Logs de errores y accesos
├── app.py             # Interfaz gráfica minimalista en modo oscuro
├── core.py            # Motor de orquestación de servicios y creación de proyectos
├── AetherStack.bat    # Lanzador de la aplicación gráfica
├── start.bat          # Script para levantar todos los servicios vía CLI
└── stop.bat           # Script para detener todos los servicios limpiamente
```

---

## 🛠️ Uso

### 1. Iniciar con Interfaz Gráfica
Haz doble clic en:
```bash
AetherStack.bat
```

### 2. Iniciar / Detener por línea de comandos
```bash
# Levantar Nginx + PHP + MariaDB
start.bat

# Detener todos los servicios
stop.bat
```

### 3. Tus Proyectos
Todos tus proyectos se almacenan en `D:\LabIA\` y son accesibles automáticamente desde:
- `http://localhost/<tu-proyecto>/`
- O vía Virtual Host local: `http://<tu-proyecto>.local`
