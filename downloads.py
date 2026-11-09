"""
AetherStack - Descargas verificadas (solo biblioteca estándar).

Descarga un archivo y comprueba su hash contra el que publica el propio proveedor
(por HTTPS) antes de dejarlo en su sitio. Nunca queda un archivo a medias ni alterado:
se escribe en un .part y solo se renombra si el hash y el zip son correctos.

Límite honesto: el hash viene del mismo sitio que el archivo. Protege contra descargas
cortadas o corruptas y contra intermediarios (HTTPS), no contra un proveedor comprometido.
"""
import hashlib
import os
import re
import urllib.request
import zipfile

USER_AGENT = "AetherStack-Downloader"
_HEX_LEN = {"sha1": 40, "sha256": 64}


class DownloadError(Exception):
    """Error esperado de descarga o verificación (mensaje apto para mostrar al usuario)."""


def _require_https(url):
    if not isinstance(url, str) or not url.startswith("https://"):
        raise DownloadError("Solo se permiten descargas por HTTPS.")


def _open(url, timeout, opener):
    _require_https(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return (opener or urllib.request.urlopen)(req, timeout=timeout)


def fetch_text(url, limit=4096, timeout=15, opener=None):
    with _open(url, timeout, opener) as resp:
        data = resp.read(limit + 1)
    if len(data) > limit:
        raise DownloadError("La respuesta es más grande de lo esperado.")
    return data.decode("utf-8", errors="ignore")


def download_file(url, dest, limit, timeout=60, opener=None):
    size = 0
    with _open(url, timeout, opener) as resp, open(dest, "wb") as out:
        while True:
            chunk = resp.read(256 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > limit:
                raise DownloadError("La descarga supera el tamaño máximo permitido.")
            out.write(chunk)


def file_hash(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def zip_ok(path):
    try:
        with zipfile.ZipFile(path) as z:
            return z.testzip() is None
    except (zipfile.BadZipFile, OSError):
        return False


def parse_hash(text, algo):
    m = re.search(r"\b([0-9a-fA-F]{%d})\b" % _HEX_LEN[algo], text or "")
    return m.group(1).lower() if m else None


def ensure_verified_zip(url, hash_url, dest, algo="sha1", limit=200 * 1024 * 1024,
                        progress_cb=None, opener=None):
    """
    Devuelve la ruta de un zip verificado en `dest`:
      * Si la copia local coincide con el hash oficial actual, se reutiliza.
      * Si el hash oficial cambió (versión nueva) o no hay copia, se descarga de nuevo.
      * Sin red, se reutiliza la copia local solo si es un zip íntegro.
    Lanza DownloadError si no se puede garantizar un archivo correcto.
    """
    expected = None
    try:
        expected = parse_hash(fetch_text(hash_url, opener=opener), algo)
    except DownloadError:
        raise
    except Exception:
        expected = None  # sin red o servidor caído

    if os.path.exists(dest):
        if expected is None:
            if zip_ok(dest):
                return dest
        elif file_hash(dest, algo) == expected and zip_ok(dest):
            return dest

    if expected is None:
        raise DownloadError("No se pudo descargar ni verificar el archivo. Revisa tu conexión a internet.")

    if progress_cb:
        progress_cb("Descargando WordPress oficial...")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    part = dest + ".part"
    try:
        try:
            download_file(url, part, limit, opener=opener)
        except DownloadError:
            raise
        except Exception as exc:
            raise DownloadError(f"No se pudo descargar el archivo: {exc}")
        if file_hash(part, algo) != expected:
            raise DownloadError("La descarga no coincide con el hash oficial: se descartó por seguridad.")
        if not zip_ok(part):
            raise DownloadError("El archivo descargado no es un zip válido.")
        os.replace(part, dest)
    finally:
        if os.path.exists(part):
            try:
                os.remove(part)
            except OSError:
                pass
    return dest
