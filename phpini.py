"""
AetherStack - Ajuste de php.ini (solo biblioteca estándar, sin efectos secundarios).

OPcache guarda el código PHP ya compilado. Con los valores de fábrica (128 MB y 10.000 archivos)
se llena enseguida cuando hay varios sitios WordPress con muchos plugins: PHP vuelve a compilar en
cada petición y los sitios tardan decenas de segundos. Estos valores sirven para unos 16 sitios.
"""
import re

TUNING = {
    "opcache.memory_consumption": "256",
    "opcache.interned_strings_buffer": "32",
    "opcache.max_accelerated_files": "50000",
    # En desarrollo no hace falta comprobar si cada archivo cambió en CADA petición (muy caro en Windows)
    "opcache.revalidate_freq": "2",
    "opcache.validate_timestamps": "1",
    "realpath_cache_size": "4096K",
    "realpath_cache_ttl": "600",
}
MARKER = "; --- AetherStack: ajustes de rendimiento ---"


def tune_php_ini(text, settings=None):
    """
    Devuelve el texto de php.ini con `settings` aplicados. Es idempotente:
    cambia la línea activa si existe y, si no, añade el valor al final dentro de un bloque propio.
    """
    settings = TUNING if settings is None else settings
    missing = []
    for key, value in settings.items():
        pattern = re.compile(r"(?m)^(\s*%s\s*=\s*).*$" % re.escape(key))
        if pattern.search(text):
            text = pattern.sub(lambda m: f"{m.group(1)}{value}", text, count=1)
        else:
            missing.append((key, value))
    if missing:
        block = "\n".join(f"{k}={v}" for k, v in missing)
        if MARKER in text:
            text = text.replace(MARKER, MARKER + "\n" + block, 1)
        else:
            text = text.rstrip("\n") + f"\n\n{MARKER}\n{block}\n"
    return text
