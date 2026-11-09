"""
AetherStack - Actualizador de código (solo biblioteca estándar).

Descarga el zip "solo código" de un release de GitHub, verifica su SHA256 y reemplaza
únicamente los archivos de la lista blanca. Nunca toca bin/, data/, conf/, logs/ ni projects/.

Seguridad:
  * Solo se descargan URLs del propio repositorio (ALLOWED_URL_PREFIX).
  * Cada release va FIRMADO con Ed25519. La app solo trae la clave pública (RELEASE_PUBLIC_KEY);
    la privada queda en el PC de quien publica. Aunque alguien lograra subir un release al
    repositorio, sin la clave privada la firma no valida y no se instala nada.
  * La firma cubre la versión y el SHA256 del zip: no sirve reutilizar un zip firmado antiguo.
  * Se rechazan rutas con '..' o absolutas (zip-slip) y se ignora todo lo que no esté en la lista blanca.
  * Si el paquete trae algo que esta versión NO sabe instalar, se rechaza entero: instalar a medias
    dejaría código nuevo sin los archivos que necesita y la app no arrancaría.
  * Los .py se compilan antes de reemplazar nada: un zip roto no deja la app inservible.
  * Antes de reemplazar se guarda una copia en .update-backup/ y, si falla algo, se restaura.
"""
import base64
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

import sigverify

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ALLOWED_URL_PREFIX = "https://github.com/luiskaco/aetherstack/releases/download/"
MAX_ZIP_BYTES = 50 * 1024 * 1024

# Clave pública Ed25519 de quien publica los releases (hex). La privada NO está en el repositorio.
RELEASE_PUBLIC_KEY = "7142be68e0685297fdfe9be8598ed6a592ccfdba3cd439c3ac01339736468e60"

# Lista blanca de lo que una actualización puede escribir
CODE_ROOT_FILES = [
    "app.py", "core.py", "i18n.py", "updater.py", "sigverify.py", "downloads.py", "vhosts.py", "phpini.py", "hosts.py", "tray.py", "single_instance.py", "requirements.txt",
    "generate_icon.py", "icon.ico",
    "AetherStack.bat", "start.bat", "stop.bat", "switch-php.bat",
    "LICENSE", "README.md",
]
CODE_TREES = ("docs", "ui")
REQUIRED_FILES = ("app.py", "core.py", "updater.py", "sigverify.py", "downloads.py")


class UpdateError(Exception):
    """Error esperado durante una actualización (mensaje apto para mostrar al usuario)."""


_TOP_LEVEL_PY_RE = re.compile(r"^[A-Za-z0-9_]+\.py$")


def is_allowed_path(rel):
    rel = rel.replace("\\", "/")
    if rel in CODE_ROOT_FILES:
        return True
    # Módulos nuevos en la raíz: así un release futuro puede añadir archivos .py sin romper esta versión
    if _TOP_LEVEL_PY_RE.match(rel):
        return True
    return any(rel.startswith(tree + "/") for tree in CODE_TREES)


def _check_url(url):
    if not isinstance(url, str) or not url.startswith(ALLOWED_URL_PREFIX):
        raise UpdateError("URL de actualización no permitida.")


def _download(url, dest, limit=MAX_ZIP_BYTES):
    _check_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "AetherStack-Updater"})
    size = 0
    with urllib.request.urlopen(req, timeout=30) as resp, open(dest, "wb") as out:
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > limit:
                raise UpdateError("La descarga supera el tamaño máximo permitido.")
            out.write(chunk)


def _sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def signing_message(version, sha256_hex):
    """Debe coincidir con tools/sign_release.py: ata la firma a una versión y a un contenido."""
    return f"aetherstack-code\nversion={version}\nsha256={sha256_hex}\n".encode("ascii")


def verify_signature(zip_path, version, signature_b64):
    """Lanza UpdateError salvo que el zip esté firmado por la clave pública del proyecto."""
    try:
        signature = base64.b64decode(signature_b64.strip(), validate=True)
    except Exception:
        raise UpdateError("El archivo de firma no es válido.")
    message = signing_message(version, _sha256_of(zip_path))
    if not sigverify.verify(bytes.fromhex(RELEASE_PUBLIC_KEY), message, signature):
        raise UpdateError("La firma del paquete no es válida: no se instala. "
                          "Puede estar corrupto o no haber sido publicado por el autor.")


def _plan_members(zf):
    """Devuelve [(miembro, ruta_relativa)] solo con lo permitido; rechaza rutas peligrosas."""
    plan = []
    unsupported = []
    for info in zf.infolist():
        if info.is_dir():
            continue
        parts = info.filename.replace("\\", "/").split("/")
        if len(parts) < 2:
            continue  # nada fuera de la carpeta raíz del paquete
        rel = "/".join(parts[1:])
        if rel.startswith("/") or ".." in rel.split("/") or re.match(r"^[A-Za-z]:", rel):
            raise UpdateError(f"El paquete contiene una ruta no válida: {info.filename}")
        if is_allowed_path(rel):
            plan.append((info, rel))
        else:
            unsupported.append(rel)
    if unsupported:
        shown = ", ".join(unsupported[:3]) + ("..." if len(unsupported) > 3 else "")
        raise UpdateError("Esta actualización incluye archivos que tu versión no puede instalar sola "
                          f"({shown}). Descarga el paquete portable completo desde la página del release.")
    names = {rel for _, rel in plan}
    missing = [f for f in REQUIRED_FILES if f not in names]
    if missing:
        raise UpdateError("El paquete está incompleto, faltan: " + ", ".join(missing))
    return plan


def _dest_inside_base(rel):
    base = os.path.realpath(BASE_DIR)
    dest = os.path.realpath(os.path.join(base, rel))
    if os.path.commonpath([base, dest]) != base:
        raise UpdateError(f"Ruta fuera de la carpeta de la aplicación: {rel}")
    return dest


def apply_update_from_files(zip_path, version, signature_b64):
    """
    Verifica la firma y aplica un zip de código ya descargado. Devuelve la lista de archivos cambiados.
    Si algo falla, deja la instalación como estaba.
    """
    verify_signature(zip_path, version, signature_b64)

    try:
        zf = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile:
        raise UpdateError("El paquete descargado no es un zip válido.")

    with zf:
        plan = _plan_members(zf)
        contents = {}
        for info, rel in plan:
            data = zf.read(info)
            if rel.endswith(".py"):
                try:
                    compile(data, rel, "exec")
                except SyntaxError as exc:
                    raise UpdateError(f"El paquete trae código inválido en {rel}: {exc.msg}")
            contents[rel] = data

    backup_dir = os.path.join(BASE_DIR, ".update-backup")
    shutil.rmtree(backup_dir, ignore_errors=True)
    os.makedirs(backup_dir, exist_ok=True)

    created, written = [], []
    try:
        for rel, data in contents.items():
            dest = _dest_inside_base(rel)
            if os.path.exists(dest):
                saved = os.path.join(backup_dir, rel)
                os.makedirs(os.path.dirname(saved), exist_ok=True)
                shutil.copy2(dest, saved)
            else:
                created.append(dest)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            tmp = dest + ".new"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, dest)
            written.append(rel)
    except Exception as exc:
        for rel in contents:
            try:
                os.remove(os.path.join(BASE_DIR, rel) + ".new")
            except OSError:
                pass
        # Vuelta atrás: restaura lo guardado y borra lo que se había creado
        for rel in written:
            saved = os.path.join(backup_dir, rel)
            dest = os.path.join(BASE_DIR, rel)
            if os.path.exists(saved):
                shutil.copy2(saved, dest)
        for dest in created:
            try:
                if os.path.exists(dest):
                    os.remove(dest)
            except OSError:
                pass
        raise UpdateError(f"No se pudo aplicar la actualización; se restauró la versión anterior. ({exc})")
    return written


def download_and_apply(code_url, sig_url, version):
    """Descarga el zip de código y su firma, y aplica la actualización si la firma es válida."""
    _check_url(code_url)
    _check_url(sig_url)
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, "code.zip")
        sig_path = os.path.join(tmp, "code.zip.sig")
        try:
            _download(sig_url, sig_path, limit=4096)
            _download(code_url, zip_path)
        except UpdateError:
            raise
        except Exception as exc:
            raise UpdateError(f"No se pudo descargar la actualización: {exc}")
        with open(sig_path, "r", encoding="ascii", errors="ignore") as f:
            return apply_update_from_files(zip_path, version, f.read(4096))


def restart_app():
    """Lanza una instancia nueva de la app; quien llama debe cerrar la actual."""
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "app.py")], cwd=BASE_DIR,
                     creationflags=flags, close_fds=True)
