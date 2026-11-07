# 05 - Architecture & Decisions (ADR): AetherStack

## ADR-001: Elección de CustomTkinter vs PyWebView
- **Contexto:** La primera versión de PyWebView sufrió cuelgues recurrentes por deadlocks en llamadas recursivas a COM (`CoreWebView2Controller recursion deadlock`).
- **Decisión:** Migrar la UI a **CustomTkinter** con especificación **Material Design 3**.
- **Consecuencias:** 100% estabilidad nativa, arranque instantáneo en menos de 200 ms y estética moderna sin depender de procesos auxiliares de navegador.

---

## ADR-002: Puerto MariaDB en 3307
- **Contexto:** El usuario tiene Docker Desktop / WSL activo, el cual ya ocupa el puerto `3306`.
- **Decisión:** Configurar MariaDB portable por defecto en el puerto `3307`.
- **Consecuencias:** Cero conflictos de arranque; los scripts de Laravel (`.env`) y WordPress (`wp-config.php`) se configuran automáticamente apuntando a `127.0.0.1:3307`.

---

## ADR-003: Filtro Estricto de Proyectos
- **Contexto:** En la carpeta `D:\LabIA` conviven bots de Python, repositorios de n8n y utilidades.
- **Decisión:** La pestaña "Mis Proyectos" inspecciona las carpetas y solo lista aquellas que contienen `artisan` (Laravel) o archivos del núcleo de WordPress.
- **Consecuencias:** Una vista despejada, limpia y enfocada solo en proyectos web.
