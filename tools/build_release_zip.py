"""
AetherStack - Generador del paquete portable de release.

Uso:
    python tools/build_release_zip.py 1.1.0

Principios:
  * Lista blanca: solo se empaqueta lo que está declarado aquí. Nada de data/, logs/,
    conf/state.json, vhosts de usuario, accesos directos .lnk ni perfiles de navegador.
  * La base de datos MariaDB se crea VACÍA con mariadb-install-db en una carpeta temporal.
  * Al final se escanea el zip: si aparece el usuario de Windows, el email de git o el
    nombre del equipo en algún archivo, el build falla y el zip se borra.
"""
import getpass
import hashlib
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import zipfile

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import updater  # lista blanca de código compartida con el actualizador de la app
import sign_release  # firma Ed25519 (clave privada fuera del repositorio)
DIST_DIR = os.path.join(BASE_DIR, "dist")
ROOT_NAME = "aetherstack"

# Archivos sueltos de la raíz que sí se publican (misma lista que el actualizador)
ROOT_FILES = updater.CODE_ROOT_FILES
# Carpetas que se copian completas (con filtros más abajo)
TREES = ["bin", "docs", "ui"]
# Carpetas vacías que deben existir en el paquete
EMPTY_DIRS = ["logs", "downloads", "conf/vhosts", "projects"]

SKIP_DIR_NAMES = {"__pycache__", ".git"}
SKIP_EXTS = {".pyc", ".tmp", ".pid", ".log", ".err", ".pdb"}
# Estado propio de cada instalación: se regenera al primer arranque
SKIP_REL_PREFIXES = ("bin/heidisql/Backups/",)
# Configs que la app reescribe con rutas absolutas del equipo en cada arranque (core.py).
# Se empaquetan con una ruta neutra; se regeneran solas al primer inicio.
REWRITTEN_CONFIGS = ("bin/nginx/conf/nginx.conf",)
REWRITTEN_CONFIG_NAMES = ("php.ini",)
NEUTRAL_ROOT = "C:/aetherstack"


def neutralize_paths(abs_path, rel):
    """Devuelve el contenido del archivo con la ruta del proyecto reemplazada, o None si no aplica."""
    if rel not in REWRITTEN_CONFIGS and not (rel.startswith("bin/php/") and os.path.basename(rel) in REWRITTEN_CONFIG_NAMES):
        return None
    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    base_fwd = BASE_DIR.replace("\\", "/")
    for variant in (base_fwd, BASE_DIR, BASE_DIR.replace("\\", "\\\\")):
        text = text.replace(variant, NEUTRAL_ROOT)
    # La carpeta de proyectos la elige cada usuario en Ajustes y puede estar fuera del proyecto:
    # en el paquete va siempre la carpeta por defecto
    text = re.sub(r'(?m)^(\s*root\s+)"[^"]*";', r'\1"' + NEUTRAL_ROOT + '/projects";', text)
    return text


def run_git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, cwd=BASE_DIR).stdout.strip()
    except OSError:
        return ""


def iter_tree(rel_root):
    abs_root = os.path.join(BASE_DIR, rel_root)
    for cur, dirs, files in os.walk(abs_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
        for name in files:
            if os.path.splitext(name)[1].lower() in SKIP_EXTS:
                continue
            abs_path = os.path.join(cur, name)
            rel = os.path.relpath(abs_path, BASE_DIR).replace("\\", "/")
            if rel.startswith(SKIP_REL_PREFIXES):
                continue
            yield abs_path, rel


def make_clean_datadir(target):
    exe = os.path.join(BASE_DIR, "bin", "mariadb", "mariadb-install-db.exe")
    if not os.path.exists(exe):
        sys.exit("No se encontró bin/mariadb/mariadb-install-db.exe")
    res = subprocess.run([exe, f"--datadir={target}"], capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit("Falló mariadb-install-db:\n" + res.stderr)
    scrub_hostname_accounts(target)


def scrub_hostname_accounts(datadir):
    """install-db crea cuentas root@<nombre-del-equipo>; se eliminan para no publicar el hostname."""
    mdir = os.path.join(BASE_DIR, "bin", "mariadb")
    port = "3399"
    server = subprocess.Popen(
        [os.path.join(mdir, "mariadbd.exe"), f"--datadir={datadir}", f"--port={port}",
         "--bind-address=127.0.0.1", "--console"],
        cwd=mdir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        sql = ("DELETE FROM mysql.global_priv WHERE Host NOT IN ('localhost','127.0.0.1','::1');"
               "DELETE FROM mysql.proxies_priv WHERE Host NOT IN ('localhost','127.0.0.1','::1');"
               "OPTIMIZE TABLE mysql.global_priv, mysql.proxies_priv;"
               "FLUSH PRIVILEGES;")
        res = None
        for _ in range(40):
            time.sleep(0.5)
            res = subprocess.run([os.path.join(mdir, "mariadb.exe"), "-h", "127.0.0.1", "-P", port,
                                  "-u", "root", "-e", sql], capture_output=True, text=True)
            if res.returncode == 0:
                break
        else:
            sys.exit("No se pudo limpiar la base temporal:\n" + (res.stderr if res else ""))
        subprocess.run([os.path.join(mdir, "mariadb-admin.exe"), "-h", "127.0.0.1", "-P", port,
                        "-u", "root", "shutdown"], capture_output=True, text=True)
        server.wait(timeout=60)
        # Tras un apagado limpio los logs de Aria no hacen falta y conservan el hostname
        for name in os.listdir(datadir):
            if name.startswith("aria_log"):
                os.remove(os.path.join(datadir, name))
    finally:
        if server.poll() is None:
            server.kill()


def scan_for_leaks(zip_path):
    """Falla si el zip contiene datos personales o rutas que nunca deben publicarse."""
    needles = {
        "usuario de Windows": getpass.getuser(),
        "email de git": run_git("config", "user.email"),
        "nombre del equipo": socket.gethostname(),
    }
    forbidden_names = ("edge_profile", "state.json", ".lnk", "/logs/", "/vhosts/")
    problems = []
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            name = info.filename
            for bad in forbidden_names:
                if bad in name and not name.endswith(".gitkeep"):
                    problems.append(f"archivo prohibido: {name}")
            if info.file_size > 60_000_000:
                continue
            data = z.read(info)
            for label, value in needles.items():
                if not value:
                    continue
                for enc in ("utf-8", "utf-16-le"):
                    if value.encode(enc, "ignore").lower() in data.lower():
                        problems.append(f"{label} dentro de {name}")
                        break
    return problems


def build_code_zip(version):
    """Zip liviano solo con código (lo usa la actualización con un clic) y su firma Ed25519."""
    out_zip = os.path.join(DIST_DIR, f"AetherStack-update-v{version}.zip")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name in updater.CODE_ROOT_FILES:
            zf.write(os.path.join(BASE_DIR, name), f"{ROOT_NAME}/{name}")
        for tree in updater.CODE_TREES:
            for abs_path, rel in iter_tree(tree):
                zf.write(abs_path, f"{ROOT_NAME}/{rel}")
    problems = scan_for_leaks(out_zip)
    if problems:
        os.remove(out_zip)
        print("BUILD DE CÓDIGO ABORTADO. Se encontró:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    h = hashlib.sha256()
    with open(out_zip, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    # La firma es obligatoria: sin ella la app no ofrece "Actualizar ahora"
    sig_file = sign_release.sign_zip(out_zip, version)
    if sign_release.public_key_from_seed(sign_release.load_seed()).hex() != updater.RELEASE_PUBLIC_KEY:
        os.remove(sig_file)
        sys.exit("La clave de firma no coincide con RELEASE_PUBLIC_KEY de updater.py.")
    print(f"OK: {out_zip}\n    {os.path.getsize(out_zip) // 1024} KB, SHA256 {h.hexdigest()}\n    firma: {sig_file}")


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python tools/build_release_zip.py <version>   (ej. 1.1.0)")
    version = sys.argv[1].lstrip("v")
    os.makedirs(DIST_DIR, exist_ok=True)
    out_zip = os.path.join(DIST_DIR, f"AetherStack-v{version}-portable.zip")
    if os.path.exists(out_zip):
        os.remove(out_zip)

    start = time.time()
    count = 0
    with tempfile.TemporaryDirectory() as tmp, \
            zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        # 1. Carpetas vacías
        for d in EMPTY_DIRS:
            zf.writestr(f"{ROOT_NAME}/{d}/.gitkeep", "")

        # 2. Archivos de la raíz
        for name in ROOT_FILES:
            zf.write(os.path.join(BASE_DIR, name), f"{ROOT_NAME}/{name}")
            count += 1

        # 3. Árboles completos
        for tree in TREES:
            for abs_path, rel in iter_tree(tree):
                neutral = neutralize_paths(abs_path, rel)
                if neutral is not None:
                    zf.writestr(f"{ROOT_NAME}/{rel}", neutral)
                else:
                    zf.write(abs_path, f"{ROOT_NAME}/{rel}")
                count += 1

        # 4. Base de datos MariaDB vacía
        clean = os.path.join(tmp, "mariadb")
        print("Creando base de datos MariaDB vacía...")
        make_clean_datadir(clean)
        for cur, dirs, files in os.walk(clean):
            for name in files:
                ext = os.path.splitext(name)[1].lower()
                if ext in (".err", ".pid", ".pem", ".log") or name == "my.ini":
                    continue
                abs_path = os.path.join(cur, name)
                rel = os.path.relpath(abs_path, clean).replace("\\", "/")
                zf.write(abs_path, f"{ROOT_NAME}/data/mariadb/{rel}")
                count += 1

    print("Escaneando el paquete en busca de datos personales...")
    problems = scan_for_leaks(out_zip)
    if problems:
        os.remove(out_zip)
        print("BUILD ABORTADO. Se encontró:")
        for p in problems:
            print("  -", p)
        sys.exit(1)

    size_mb = os.path.getsize(out_zip) // (1024 * 1024)
    print(f"OK: {out_zip}\n    {count} archivos, {size_mb} MB, {int(time.time() - start)} s, sin fugas detectadas")
    # Hash del paquete completo, para quien lo descargue a mano y quiera comprobarlo
    h = hashlib.sha256()
    with open(out_zip, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    with open(out_zip + ".sha256", "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{h.hexdigest()}  {os.path.basename(out_zip)}\n")
    build_code_zip(version)


if __name__ == "__main__":
    main()
