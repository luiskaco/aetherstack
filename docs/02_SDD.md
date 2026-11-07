# 02 - System Design Document (SDD): AetherStack

## 1. Arquitectura General
AetherStack sigue una arquitectura desacoplada y orientada a procesos portables sobre el sistema operativo Windows.

```
┌────────────────────────────────────────────────────────┐
│          AetherStack App (Material Design 3)          │
│                [app.py / CustomTkinter]                │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│            Core Engine Orchestrator [core.py]          │
└───────┬───────────────────┼────────────────────┬───────┘
        │                   │                    │
        ▼                   ▼                    ▼
┌──────────────┐    ┌──────────────┐     ┌──────────────┐
│  Nginx 1.28  │    │  PHP FastCGI │     │ MariaDB 11.8 │
│  [Port: 80]  │    │ (8.4 / 8.5)  │     │ [Port: 3307] │
└───────┬──────┘    └───────┬──────┘     └───────┬──────┘
        │                   │                    │
        ▼                   ▼                    ▼
┌───────────────────────────────────────────────────────┐
│     Carpeta de Proyectos Local (ej. D:\LabIA)        │
│          [Laravel Apps / WordPress Sites]             │
└───────────────────────────────────────────────────────┘
```

---

## 2. Componentes Clave

1. **`app.py`:** Interfaz gráfica nativa con tokens de diseño Material 3, hilos en segundo plano para evitar bloqueos y comunicación directa con el motor.
2. **`core.py`:** Administra el ciclo de vida de los procesos (`start`, `stop`, `switch_php`), la detección de puertos, la creación de Virtual Hosts Nginx y la gestión de bases de datos.
3. **`conf/nginx.conf`:** Enrutador maestro con directivas optimizadas para Laravel (`public/`) y WordPress (URLs amigables / permalinks).
4. **`conf/my.ini`:** Configuración de MariaDB con juego de caracteres `utf8mb4_unicode_ci` y puerto aislado `3307`.
