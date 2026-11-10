"""
AetherStack - Gestión de un bloque propio en el archivo hosts de Windows.

Los dominios de desarrollo (frutiflex.test...) no existen en ningún DNS: Windows los resuelve
porque están en `hosts`. AetherStack mantiene UN bloque delimitado por marcas y no toca el resto
del archivo. Escribir `hosts` exige permisos de administrador: se pide con el aviso de Windows (UAC).
"""
import base64
import hashlib
import os
import re
import subprocess
import tempfile

POWERSHELL_EXE = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "drivers", "etc", "hosts")
BEGIN = "# >>> AetherStack (bloque administrado automaticamente, no editar a mano) >>>"
END = "# <<< AetherStack <<<"
_DOMAIN_RE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$")
_BLOCK_RE = re.compile(r"(?:\r?\n)?" + re.escape(BEGIN) + r".*?" + re.escape(END) + r"[ \t]*(?:\r?\n)?", re.S)


def clean_domains(domains):
    """Dominios válidos, en minúsculas y sin repetir. Descarta todo lo que no parezca un nombre de host."""
    out = []
    for d in domains:
        d = str(d or "").strip().lower()
        if _DOMAIN_RE.match(d) and d not in out:
            out.append(d)
    return sorted(out)


def render_block(domains, newline="\n"):
    lines = [BEGIN] + [f"127.0.0.1 {d}" for d in clean_domains(domains)] + [END]
    return newline.join(lines)


def remove_block(text):
    return _BLOCK_RE.sub("\n" if "\n" in text else "", text, count=1) if BEGIN in text else text


def apply_block(text, domains):
    """Devuelve `text` con el bloque de AetherStack actualizado. Idempotente; si no hay dominios, lo quita."""
    newline = "\r\n" if "\r\n" in text else "\n"
    base = remove_block(text).rstrip("\r\n")
    if not clean_domains(domains):
        return base + newline if base else ""
    return base + newline + newline + render_block(domains, newline) + newline


def read_hosts(path=HOSTS_PATH):
    with open(path, "r", encoding="utf-8", errors="surrogateescape", newline="") as f:
        return f.read()


def current_domains(text):
    m = re.search(re.escape(BEGIN) + r"(.*?)" + re.escape(END), text, re.S)
    if not m:
        return []
    return clean_domains(l.split()[1] for l in m.group(1).splitlines() if l.strip().startswith("127.0.0.1") and len(l.split()) > 1)


def _is_admin_writable(path):
    """
    True si el proceso actual puede escribir en `path`. Se prueba abriéndolo de verdad:
    en Windows os.access(W_OK) solo mira el atributo de solo lectura y no los permisos.
    """
    try:
        with open(path, "r+b"):
            return True
    except OSError:
        return False


def write_hosts(new_text, path=HOSTS_PATH, backup_dir=None):
    """
    Escribe `hosts`. Devuelve "updated", "cancelled" (el usuario rechazó el aviso de Windows) o "error".
    Antes de la primera modificación guarda una copia en backup_dir/hosts.backup.
    """
    if backup_dir:
        try:
            os.makedirs(backup_dir, exist_ok=True)
            backup = os.path.join(backup_dir, "hosts.backup")
            if not os.path.exists(backup):
                with open(backup, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
                    f.write(read_hosts(path))
        except OSError:
            pass
    if _is_admin_writable(path):
        with open(path, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
            f.write(new_text)
        return "updated"
    # Sin permisos: se escribe en un archivo temporal y un PowerShell elevado lo copia sobre hosts.
    # El script viaja codificado en Base64 (sin problemas de comillas) y deja el resultado en un registro.
    fd, tmp = tempfile.mkstemp(prefix="aetherstack-hosts-", suffix=".txt")
    os.close(fd)
    log = tmp + ".log"
    try:
        with open(tmp, "w", encoding="utf-8", errors="surrogateescape", newline="") as f:
            f.write(new_text)
        if "'" in tmp or "'" in path:
            return "error"
        sha = hashlib.sha256(new_text.encode("utf-8", errors="surrogateescape")).hexdigest()
        encoded = encode_script(elevated_copy_script(tmp, path, log, sha))
        outer = ("try { Start-Process -FilePath '" + POWERSHELL_EXE + "' -Verb RunAs -Wait -WindowStyle Hidden "
                 "-ArgumentList '-NoProfile','-EncodedCommand','" + encoded + "' -ErrorAction Stop; exit 0 } "
                 "catch { if ($_.Exception.Message -match 'cancel') { exit 2 } else { exit 1 } }")
        res = subprocess.run([POWERSHELL_EXE, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", outer],
                             capture_output=True, text=True, timeout=180)
        if res.returncode == 2:
            return "cancelled"
        if res.returncode != 0:
            return "error"
        try:
            with open(log, "r", encoding="utf-8-sig", errors="replace") as f:
                if f.read().strip() != "OK":
                    return "error"
        except OSError:
            return "error"
    except (subprocess.TimeoutExpired, OSError):
        return "error"
    finally:
        for leftover in (tmp, log):
            try:
                os.remove(leftover)
            except OSError:
                pass
    try:
        return "updated" if read_hosts(path) == new_text else "error"
    except OSError:
        return "error"


def elevated_copy_script(tmp, path, log, expected_sha256=None):
    """
    Script que ejecuta el PowerShell elevado: copia `tmp` sobre `path` y deja OK o el error en `log`.
    Con `expected_sha256` comprueba antes que el temporal no fue cambiado por otro proceso.
    """
    check = ""
    if expected_sha256:
        check = (f"if ((Get-FileHash -LiteralPath '{tmp}' -Algorithm SHA256).Hash -ne '{expected_sha256}') "
                 "{ throw 'El archivo temporal cambio antes de aplicarse' }; ")
    return ("$ErrorActionPreference='Stop'\n"
            f"try {{ {check}Copy-Item -LiteralPath '{tmp}' -Destination '{path}' -Force; "
            f"Set-Content -LiteralPath '{log}' -Value 'OK' -Encoding ASCII }}\n"
            f"catch {{ Set-Content -LiteralPath '{log}' -Value ('ERROR: ' + $_.Exception.Message) -Encoding UTF8 }}\n")


def encode_script(script):
    """Formato de -EncodedCommand: Base64 de UTF-16 little-endian."""
    return base64.b64encode(script.encode("utf-16-le")).decode("ascii")


def sync(domains, path=HOSTS_PATH, backup_dir=None):
    """
    Deja en `hosts` exactamente `domains` dentro del bloque de AetherStack.
    Devuelve "unchanged", "updated", "cancelled" o "error".
    """
    current = read_hosts(path)
    wanted = apply_block(current, domains)
    if wanted == current:
        return "unchanged"
    return write_hosts(wanted, path, backup_dir)
