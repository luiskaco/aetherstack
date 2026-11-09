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
