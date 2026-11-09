# 07 - Decisiones de Arquitectura (ADR): AetherStack

## ADR-001: Releases firmados con Ed25519 y verificador propio sin dependencias
- **Fecha:** 2026-11-09
- **Estado:** Aceptada

**Contexto.** La app se actualiza sola descargando un zip de código desde GitHub Releases. Un SHA256 publicado junto al zip solo detecta corrupción: quien publicara un release (por ejemplo, con la cuenta de GitHub comprometida) podría subir un zip malicioso con su propio hash y la app lo instalaría.

**Decisión.** Cada zip de código se firma con Ed25519. La clave privada vive en el PC del autor, fuera del repositorio. La app incluye solo la clave pública y no instala nada cuya firma no valide. El mensaje firmado incluye la versión y el SHA256 del zip, por lo que no sirve reutilizar un zip firmado antiguo.

**Alternativas.**
- Solo SHA256: no protege frente a un release publicado por un tercero. Descartada.
- Biblioteca `cryptography`: más auditada, pero añade una dependencia de `pip` que las instalaciones existentes no tienen; el actualizador dejaría de funcionar para quien no la instale. Descartada.
- **Elegida:** verificador de referencia del RFC 8032 en Python estándar (`sigverify.py`, ~100 líneas), validado con los vectores oficiales y contra `cryptography` en las pruebas.

**Consecuencias.**
- (+) Un tercero que suba un release no puede lograr que se instale.
- (+) Sin dependencias nuevas.
- (-) Hay que custodiar la clave privada; si se pierde o se filtra hay que publicar una versión a mano con otra clave (ver `10_RUNBOOK.md` § 6).
- (-) Las instalaciones v1.2.1 actualizan con el esquema anterior (solo SHA256) una única vez, para recibir el verificador.
- Límite: la firma no protege si se compromete el PC del autor.

## ADR-002: El actualizador rechaza paquetes que no sabe instalar por completo
- **Fecha:** 2026-11-09
- **Estado:** Aceptada

**Contexto.** El actualizador instala solo archivos de una lista blanca. En v1.2.2 y v1.2.3 se añadieron archivos nuevos en la raíz (`sigverify.py`, `downloads.py`); las versiones anteriores los ignoraban en silencio y el código nuevo, ya instalado, no arrancaba. Mis pruebas aplicaban el actualizador nuevo en vez del de la versión ya instalada, por eso no se detectó antes de publicar.

**Decisión.**
1. Si un paquete contiene cualquier ruta que la versión instalada no puede instalar, se rechaza completo con un mensaje claro (nunca instalación parcial).
2. Los módulos `.py` de la raíz se aceptan por patrón, de modo que los releases futuros puedan añadirlos.
3. `tests/test_compat.py` valida el paquete actual contra el `updater.py` real de las versiones publicadas.
4. Una versión incompatible con un clic se retira de la actualización automática borrando los assets de código de su release; el portable completo permanece.

**Consecuencias.** (+) Una actualización fallida deja la app intacta y explica qué hacer. (-) Añadir archivos nuevos que versiones antiguas no admiten exige un release intermedio o que esos usuarios bajen el portable.
