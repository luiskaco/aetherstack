"""
AetherStack - Minimalist Local Dev Core Engine
Soporte para gestión y eliminación completa de proyectos (archivos, DB y vhost).
"""
import os
import sys
import subprocess
import time
import socket
import json
import shutil
import tempfile
import stat
import urllib.request
import zipfile
import re
import downloads
import vhosts
import phpini
import hosts
import html

VERSION = "1.2.5"
RELEASES_API = "https://api.github.com/repos/luiskaco/aetherstack/releases/latest"
WORDPRESS_URL = "https://wordpress.org/latest.zip"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
CONF_DIR = os.path.join(BASE_DIR, "conf")
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
STATE_FILE = os.path.join(CONF_DIR, "state.json")
BASE_DIR_SLASH = BASE_DIR.replace("\\", "/")

# Nombres de proyecto permitidos: solo letras, números, guion y guion bajo.
# Evita path traversal, inyección en SQL/Nginx y en comandos de shell.
PROJECT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

def is_valid_project_name(name):
    return isinstance(name, str) and bool(PROJECT_NAME_RE.fullmatch(name))

def get_safe_project_path(project_name):
    """Devuelve la ruta del proyecto si el nombre es válido y queda dentro de la raíz; si no, None."""
    if not is_valid_project_name(project_name):
        return None
    root = os.path.realpath(get_projects_root())
    target = os.path.realpath(os.path.join(root, project_name))
    if os.path.dirname(target) != root:
        return None
    return target

def db_name_for(project_name):
    return f"{project_name.lower().replace('-', '_')}_db"

def reload_nginx_if_running():
    if is_process_running("nginx.exe"):
        nginx_dir = os.path.join(BIN_DIR, "nginx")
        nginx_exe = os.path.join(nginx_dir, "nginx.exe")
        subprocess.run([nginx_exe, "-s", "reload", "-p", nginx_dir], cwd=nginx_dir,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def is_safe_projects_dir(path):
    """
    True si `path` puede ser la carpeta de proyectos: existe y no es una raíz de unidad, una carpeta
    del sistema, el perfil del usuario, AetherStack ni una carpeta que lo contenga.
    """
    try:
        real = os.path.normcase(os.path.realpath(path))
    except (OSError, ValueError, TypeError):
        return False
    if not os.path.isdir(real):
        return False
    if os.path.dirname(real) == real:  # raíz de unidad
        return False
    forbidden = [os.environ.get(v) for v in ("SystemRoot", "ProgramFiles", "ProgramFiles(x86)",
                                             "ProgramData", "USERPROFILE")]
    for f in forbidden:
        if f and real == os.path.normcase(os.path.realpath(f)):
            return False
    base = os.path.normcase(os.path.realpath(BASE_DIR))
    if base == real or base.startswith(real + os.sep):  # AetherStack o un ancestro suyo
        return False
    return True

def get_projects_root():
    state = load_state()
    p_dir = state.get("projects_dir")
    if p_dir and is_safe_projects_dir(p_dir):
        return p_dir
    # Carpeta propia dentro de AetherStack (nunca la carpeta padre): es el valor seguro por defecto.
    local_proj = os.path.join(BASE_DIR, "projects")
    os.makedirs(local_proj, exist_ok=True)
    return local_proj

DEFAULT_CONFIG = {
    "php_version": "8.4",
    "nginx_port": 80,
    "mariadb_port": 3307,
    "php_port": 9000,
    "projects_dir": os.path.join(BASE_DIR, "projects"),
    "theme": "dark",
    "language": "es",
    "check_updates": True,
    "vhost_tld": vhosts.DEFAULT_TLD,
    "close_to_tray": True,
    "php_workers": vhosts.DEFAULT_PHP_WORKERS
}

def load_state():
    conf = DEFAULT_CONFIG.copy()
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                conf.update(loaded)
        except Exception:
            pass
    return _sanitize_state(conf)

def _sanitize_state(conf):
    """Descarta valores con tipo o rango inválido (state.json editado a mano): vuelve al valor por defecto."""
    def port_ok(v):
        return isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 65535
    for key in ("nginx_port", "mariadb_port", "php_port"):
        if not port_ok(conf.get(key)):
            conf[key] = DEFAULT_CONFIG[key]
    if not isinstance(conf.get("projects_dir"), str):
        conf["projects_dir"] = DEFAULT_CONFIG["projects_dir"]
    conf["vhost_tld"] = vhosts.normalize_tld(conf.get("vhost_tld"))
    workers = conf.get("php_workers")
    if not (isinstance(workers, int) and not isinstance(workers, bool) and 1 <= workers <= 16):
        conf["php_workers"] = DEFAULT_CONFIG["php_workers"]
    if conf["php_port"] + conf["php_workers"] > 65535:
        conf["php_port"] = DEFAULT_CONFIG["php_port"]
    return conf

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def parse_version(text):
    """Convierte 'v1.2.3' en (1, 2, 3). Devuelve None si no es una versión válida."""
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", str(text or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None

def check_for_update(timeout=5):
    """
    Consulta el último release publicado en GitHub.
    Devuelve {"version", "url"} si hay una versión más nueva que VERSION; si no, None.
    Nunca lanza excepción: sin red o con error de API simplemente devuelve None.
    Solo envía una petición GET anónima, sin datos del usuario.
    """
    if not load_state().get("check_updates", True):
        return None
    try:
        req = urllib.request.Request(RELEASES_API, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "AetherStack-UpdateCheck",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        latest = parse_version(data.get("tag_name"))
        current = parse_version(VERSION)
        url = data.get("html_url", "")
        # Solo se abre una URL de GitHub del propio repositorio
        if latest and current and latest > current and url.startswith("https://github.com/luiskaco/aetherstack/"):
            info = {"version": ".".join(map(str, latest)), "url": url, "code_url": None, "sig_url": None}
            # Actualización con un clic: solo si el release trae el zip de actualización y su firma.
            # El prefijo "AetherStack-update-" es la GENERACIÓN del protocolo: las versiones anteriores
            # buscaban "AetherStack-code-" y por eso ya no ven estos paquetes (que no sabrían instalar).
            for asset in data.get("assets", []):
                name = asset.get("name", "")
                link = asset.get("browser_download_url", "")
                if re.match(r"^AetherStack-update-v[\d.]+\.zip$", name):
                    info["code_url"] = link
                elif re.match(r"^AetherStack-update-v[\d.]+\.zip\.sig$", name):
                    info["sig_url"] = link
            return info
    except Exception:
        pass
    return None

def set_language(lang):
    state = load_state()
    state["language"] = lang
    save_state(state)
    return lang

def get_language():
    state = load_state()
    return state.get("language", "es")

def get_installed_php_versions():
    php_root = os.path.join(BIN_DIR, "php")
    versions = []
    if os.path.exists(php_root):
        for entry in os.scandir(php_root):
            if entry.is_dir() and entry.name.startswith("php-"):
                v = entry.name.replace("php-", "")
                versions.append(v)
    return sorted(versions, key=lambda x: [int(p) if p.isdigit() else p for p in x.split(".")])

def is_port_in_use(port, host='127.0.0.1'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((host, port)) == 0

def _running_process_names():
    """Nombres (en minúsculas) de todos los procesos activos, vía API de Windows (~2 ms, sin lanzar tasklist)."""
    import ctypes
    from ctypes import wintypes

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_void_p),
            ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG),
            ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260),
        ]

    k32 = ctypes.windll.kernel32
    k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]

    TH32CS_SNAPPROCESS = 0x2
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    names = set()
    if not snap or snap == wintypes.HANDLE(-1).value:
        return names
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        ok = k32.Process32FirstW(snap, ctypes.byref(entry))
        while ok:
            names.add(entry.szExeFile.lower())
            ok = k32.Process32NextW(snap, ctypes.byref(entry))
    finally:
        k32.CloseHandle(snap)
    return names

def is_process_running(process_name, _names=None):
    try:
        names = _names if _names is not None else _running_process_names()
        return process_name.lower() in names
    except Exception:
        return False

def get_status():
    state = load_state()
    php_ver = state.get("php_version", "8.4")
    
    procs = _running_process_names()  # una sola consulta por ciclo
    nginx_running = "nginx.exe" in procs and is_port_in_use(state["nginx_port"])
    php_running = "php-cgi.exe" in procs and is_port_in_use(state["php_port"])
    mariadb_running = ("mariadbd.exe" in procs or "mysqld.exe" in procs) and is_port_in_use(state["mariadb_port"])

    return {
        "nginx": {
            "running": nginx_running,
            "port": state["nginx_port"]
        },
        "php": {
            "running": php_running,
            "version": php_ver,
            "port": state["php_port"]
        },
        "mariadb": {
            "running": mariadb_running,
            "port": state["mariadb_port"]
        },
        "all_running": nginx_running and php_running and mariadb_running,
        "config": state
    }

def update_mariadb_config():
    state = load_state()
    port = state.get("mariadb_port", 3307)
    
    my_ini_content = f"""[client]
port = {port}
socket = mysql.sock
default-character-set = utf8mb4

[mysqld]
port = {port}
bind-address = 127.0.0.1
socket = mysql.sock
basedir = "{BASE_DIR_SLASH}/bin/mariadb"
datadir = "{BASE_DIR_SLASH}/data/mariadb"
pid-file = "{BASE_DIR_SLASH}/data/mariadb/mysql.pid"
log-error = "{BASE_DIR_SLASH}/logs/mariadb_error.log"

character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

default_storage_engine = InnoDB
max_connections = 100
max_allowed_packet = 64M
innodb_buffer_pool_size = 128M
innodb_file_per_table = 1

# Endurecimiento: sin LOAD DATA LOCAL y con INTO OUTFILE / LOAD_FILE limitados a una carpeta propia
local_infile = 0
secure_file_priv = "{BASE_DIR_SLASH}/data/mariadb-files"
"""
    os.makedirs(os.path.join(DATA_DIR, "mariadb-files"), exist_ok=True)
    my_ini_file = os.path.join(CONF_DIR, "my.ini")
    with open(my_ini_file, "w", encoding="utf-8") as f:
        f.write(my_ini_content)

    data_my_ini = os.path.join(DATA_DIR, "mariadb", "my.ini")
    if os.path.exists(os.path.dirname(data_my_ini)):
        try:
            with open(data_my_ini, "w", encoding="utf-8") as f:
                f.write(f"[mysqld]\ndatadir={BASE_DIR_SLASH}/data/mariadb\n")
        except Exception:
            pass

def update_php_configs():
    log_path = f"{BASE_DIR_SLASH}/logs/php_error.log"
    php_root = os.path.join(BIN_DIR, "php")
    if os.path.exists(php_root):
        import re
        for entry in os.scandir(php_root):
            if entry.is_dir() and entry.name.startswith("php-"):
                ini_file = os.path.join(entry.path, "php.ini")
                if os.path.exists(ini_file):
                    try:
                        with open(ini_file, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        new_content = re.sub(r'error_log\s*=\s*".*?"', f'error_log = "{log_path}"', content)
                        new_content = phpini.tune_php_ini(new_content)
                        with open(ini_file, "w", encoding="utf-8") as f:
                            f.write(new_content)
                    except Exception:
                        pass

def sync_vhosts_paths():
    fastcgi_target = f'include "{BASE_DIR_SLASH}/bin/nginx/conf/fastcgi_params";'
    vhosts_dir = os.path.join(CONF_DIR, "vhosts")
    if os.path.exists(vhosts_dir):
        import re
        for entry in os.scandir(vhosts_dir):
            if entry.is_file() and entry.name.endswith(".conf"):
                try:
                    with open(entry.path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    new_content = re.sub(r'include\s+"[^"]*fastcgi_params";', fastcgi_target, content)
                    # Migra vhosts antiguos que escuchaban en todas las interfaces
                    new_content = re.sub(r'(?m)^(\s*)listen\s+(\d+);', r'\1listen 127.0.0.1:\2;', new_content)
                    if new_content != content:
                        with open(entry.path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                except Exception:
                    pass

DEFAULT_INDEX_MARKER = "<!-- aetherstack-default-index -->"
DEFAULT_INDEX_TEXT = {
    "es": {"title": "Tu entorno local está funcionando", "sub": "Nginx, PHP y MariaDB responden correctamente.",
           "projects": "Tus proyectos", "empty": "Todavía no hay proyectos. Crea uno de WordPress o Laravel desde AetherStack.",
           "stack": "Stack", "open": "Abrir"},
    "en": {"title": "Your local environment is running", "sub": "Nginx, PHP and MariaDB are responding correctly.",
           "projects": "Your projects", "empty": "No projects yet. Create a WordPress or Laravel project from AetherStack.",
           "stack": "Stack", "open": "Open"},
}

def build_default_index():
    """Página de bienvenida estática de http://localhost. Solo lista proyectos con nombre válido."""
    state = load_state()
    lang = state.get("language", "es")
    tx = DEFAULT_INDEX_TEXT.get(lang, DEFAULT_INDEX_TEXT["es"])
    items = []
    for p in list_projects():
        rel = f"{p['name']}/public/" if p["type"] == "Laravel" else f"{p['name']}/"
        items.append(
            f'<a class="row" href="/{html.escape(rel, quote=True)}"><span>{html.escape(p["name"])}</span>'
            f'<span class="tag">{html.escape(p["type"])}</span><span class="go">{tx["open"]} →</span></a>'
        )
    body = "\n".join(items) if items else f'<p class="empty">{html.escape(tx["empty"])}</p>'
    stack = f'Nginx · PHP {html.escape(str(state.get("php_version", "")))} · MariaDB :{html.escape(str(state.get("mariadb_port", "")))}'
    return f"""<!DOCTYPE html>
{DEFAULT_INDEX_MARKER}
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AetherStack</title>
<style>
:root{{color-scheme:dark}}
*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;background:#0B0F19;color:#F8FAFC;font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;display:grid;place-items:center;padding:24px}}
main{{width:100%;max-width:640px}}
.logo{{width:56px;height:56px;border-radius:16px;background:#2563EB;display:grid;place-items:center;font-size:28px;margin-bottom:20px}}
h1{{font-size:1.6rem;margin:0 0 6px}}
.sub{{color:#94A3B8;margin:0 0 28px}}
h2{{font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:#94A3B8;margin:0 0 10px}}
.row{{display:flex;align-items:center;gap:12px;padding:12px 16px;margin-bottom:8px;background:#161F30;border:1px solid #1E293B;border-radius:12px;color:#F8FAFC;text-decoration:none}}
.row:hover,.row:focus-visible{{border-color:#2563EB;outline:none}}
.row span:first-child{{flex:1;font-weight:600}}
.tag{{font-size:.75rem;color:#60A5FA}}
.go{{font-size:.85rem;color:#CBD5E1}}
.empty{{color:#CBD5E1;background:#161F30;border:1px dashed #334155;border-radius:12px;padding:16px;margin:0}}
footer{{margin-top:28px;color:#94A3B8;font-size:.8rem}}
</style></head><body><main>
<div class="logo">⚡</div>
<h1>{html.escape(tx["title"])}</h1>
<p class="sub">{html.escape(tx["sub"])}</p>
<h2>{html.escape(tx["projects"])}</h2>
{body}
<footer>AetherStack v{VERSION} · {tx["stack"]}: {stack}</footer>
</main></body></html>
"""

def write_default_index():
    """
    Crea/actualiza index.html en la carpeta de proyectos para que localhost no devuelva 403.
    Nunca pisa un index propio del usuario: solo se reescribe si lleva nuestra marca.
    """
    try:
        root = get_projects_root()
        for name in ("index.php", "index.htm"):
            if os.path.exists(os.path.join(root, name)):
                return
        target = os.path.join(root, "index.html")
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8", errors="ignore") as f:
                if DEFAULT_INDEX_MARKER not in f.read(512):
                    return
        content = build_default_index()
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                if f.read() == content:
                    return
        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    except Exception:
        pass

def ensure_runtime_dirs():
    """Nginx y los logs necesitan estas carpetas; las carpetas vacías no viajan en un zip."""
    for d in (LOGS_DIR, os.path.join(BIN_DIR, "nginx", "temp"), os.path.join(BIN_DIR, "nginx", "logs")):
        try:
            os.makedirs(d, exist_ok=True)
        except OSError:
            pass

def php_ports(state):
    return vhosts.php_worker_ports(state["php_port"], state.get("php_workers"))

def start_php_workers(state, php_cgi, php_ini, php_dir):
    """Levanta un php-cgi por puerto del pool (solo los que no estén ya activos)."""
    os.environ["PHP_FCGI_MAX_REQUESTS"] = "0"
    for port in php_ports(state):
        if not is_port_in_use(port):
            # Sin shell: los argumentos van como lista. DETACHED_PROCESS hace que el proceso sobreviva
            # si se cierra la ventana de la app (el stack sigue activo, ver icono de la bandeja).
            subprocess.Popen([php_cgi, "-b", f"127.0.0.1:{port}", "-c", php_ini], cwd=php_dir,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             creationflags=getattr(subprocess, "DETACHED_PROCESS", 0)
                             | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))

def update_nginx_config():
    ensure_runtime_dirs()
    write_default_index()
    state = load_state()
    proj_dir = get_projects_root().replace("\\", "/")

    # Si AetherStack vive dentro de la carpeta de proyectos, su propio código,
    # datos y logs no deben ser servidos por el servidor web.
    protect_block = ""
    try:
        rel_self = os.path.relpath(BASE_DIR, get_projects_root()).replace("\\", "/")
        if not rel_self.startswith("..") and rel_self != "." and not os.path.isabs(rel_self):
            protect_block = f'location ^~ "/{rel_self}/" {{ return 404; }}'
    except ValueError:
        pass  # unidades distintas en Windows: no está dentro de la raíz

    php_servers = vhosts.render_upstream_servers(php_ports(state))
    nginx_conf_content = f"""# AetherStack - Nginx Master Configuration
worker_processes  auto;

error_log  "{BASE_DIR_SLASH}/logs/nginx_error.log" warn;
pid        "{BASE_DIR_SLASH}/logs/nginx.pid";

events {{
    worker_connections  1024;
}}

http {{
    include       "{BASE_DIR_SLASH}/bin/nginx/conf/mime.types";
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  "{BASE_DIR_SLASH}/logs/nginx_access.log"  main;

    sendfile        on;
    tcp_nopush     on;
    tcp_nodelay    on;
    keepalive_timeout  65;
    types_hash_max_size 2048;

    client_max_body_size 128M;

    # Con varios proyectos, el valor por defecto (32) hace que Nginx no recargue
    server_names_hash_bucket_size 128;

    gzip  on;
    gzip_disable "msie6";
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    upstream php_cgi {{
{php_servers}
        keepalive 16;
    }}

    # Servidor por defecto: cualquier Host desconocido (p. ej. DNS rebinding) se corta sin servir nada
    server {{
        listen       127.0.0.1:{state['nginx_port']} default_server;
        server_name  _;
        return 444;
    }}

    server {{
        listen       127.0.0.1:{state['nginx_port']};
        server_name  localhost;

        root   "{proj_dir}";
        index  index.php index.html index.htm;

        {protect_block}

        # Archivos que no deben salir por HTTP en el acceso /proyecto (logs, volcados, bases, dependencias)
        location ~* ^/[^/]+/(storage|database|vendor|bootstrap/cache)/ {{ deny all; }}
        location ~* \\.(sql|log|sqlite|sqlite3|bak)$ {{ deny all; }}
        location ~* /composer\\.(json|lock)$ {{ deny all; }}

        location / {{
            autoindex off;
            try_files $uri $uri/ /index.php?$query_string;
        }}

        location ~ \\.php$ {{
            try_files $uri =404;
            fastcgi_split_path_info ^(.+\\.php)(/.+)$;
            fastcgi_pass   php_cgi;
            fastcgi_index  index.php;
            fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
            include        "{BASE_DIR_SLASH}/bin/nginx/conf/fastcgi_params";
            fastcgi_read_timeout 300;
        }}

        location ~ /\\. {{
            deny all;
        }}
    }}

    include "{BASE_DIR_SLASH}/conf/vhosts/*.conf";
}}
"""
    with open(os.path.join(CONF_DIR, "nginx.conf"), "w", encoding="utf-8") as f:
        f.write(nginx_conf_content)

    nginx_dest = os.path.join(BIN_DIR, "nginx", "conf", "nginx.conf")
    try:
        with open(nginx_dest, "w", encoding="utf-8") as f:
            f.write(nginx_conf_content)
    except Exception:
        pass

def update_global_config(new_config):
    state = load_state()
    state.update(new_config)
    save_state(state)
    update_mariadb_config()
    update_nginx_config()
    update_php_configs()
    sync_vhosts_paths()
    
    if is_process_running("nginx.exe"):
        nginx_dir = os.path.join(BIN_DIR, "nginx")
        nginx_exe = os.path.join(nginx_dir, "nginx.exe")
        subprocess.run([nginx_exe, "-s", "reload", "-p", nginx_dir], cwd=nginx_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    return get_status()

def start_services(php_version=None):
    state = load_state()
    if php_version:
        state["php_version"] = php_version
        save_state(state)

    update_mariadb_config()
    update_nginx_config()
    update_php_configs()
    sync_vhosts_paths()

    php_ver = state.get("php_version", "8.4")
    nginx_dir = os.path.join(BIN_DIR, "nginx")
    nginx_exe = os.path.join(nginx_dir, "nginx.exe")
    
    php_dir = os.path.join(BIN_DIR, "php", f"php-{php_ver}")
    php_cgi = os.path.join(php_dir, "php-cgi.exe")
    php_ini = os.path.join(php_dir, "php.ini")
    
    mariadb_dir = os.path.join(BIN_DIR, "mariadb")
    mariadbd_exe = os.path.join(mariadb_dir, "mariadbd.exe")
    mariadb_ini = os.path.join(CONF_DIR, "my.ini")

    # 1. MariaDB
    if not is_port_in_use(state["mariadb_port"]):
        cmd = f'start /b "" "{mariadbd_exe}" --defaults-file="{mariadb_ini}"'
        subprocess.Popen(cmd, shell=True, cwd=mariadb_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. PHP FastCGI
    start_php_workers(state, php_cgi, php_ini, php_dir)

    # 3. Nginx
    if not is_port_in_use(state["nginx_port"]):
        cmd = f'start /b "" "{nginx_exe}" -p "{nginx_dir}"'
        subprocess.Popen(cmd, shell=True, cwd=nginx_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(1.2)
    return get_status()

def stop_services():
    nginx_dir = os.path.join(BIN_DIR, "nginx")
    nginx_exe = os.path.join(nginx_dir, "nginx.exe")
    try:
        subprocess.run([nginx_exe, "-s", "stop", "-p", nginx_dir], cwd=nginx_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
    except Exception:
        pass

    for proc in ["nginx.exe", "php-cgi.exe", "mariadbd.exe", "mysqld.exe"]:
        try:
            subprocess.run(f"taskkill /F /IM {proc} /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    time.sleep(0.5)
    return get_status()

def switch_php(version):
    if version not in get_installed_php_versions():
        return get_status()
    state = load_state()
    state["php_version"] = version
    save_state(state)
    
    subprocess.run("taskkill /F /IM php-cgi.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    
    php_dir = os.path.join(BIN_DIR, "php", f"php-{version}")
    php_cgi = os.path.join(php_dir, "php-cgi.exe")
    php_ini = os.path.join(php_dir, "php.ini")
    start_php_workers(state, php_cgi, php_ini, php_dir)
    time.sleep(0.8)
    return get_status()

def create_database(db_name):
    if not re.fullmatch(r"[a-z0-9_]{1,70}", db_name or ""):
        return False, "Nombre de base de datos inválido."
    state = load_state()
    mariadb_dir = os.path.join(BIN_DIR, "mariadb")
    mariadb_cli = os.path.join(mariadb_dir, "mariadb.exe")
    cmd = f'CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
    try:
        res = subprocess.run(
            [mariadb_cli, "-h", "127.0.0.1", "-P", str(state["mariadb_port"]), "-u", "root", "-e", cmd],
            cwd=mariadb_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return res.returncode == 0, f"Base de datos '{db_name}' creada en MariaDB."
    except Exception as e:
        return False, str(e)

def drop_database(db_name):
    if not re.fullmatch(r"[a-z0-9_]{1,70}", db_name or ""):
        return False
    state = load_state()
    mariadb_dir = os.path.join(BIN_DIR, "mariadb")
    mariadb_cli = os.path.join(mariadb_dir, "mariadb.exe")
    cmd = f'DROP DATABASE IF EXISTS `{db_name}`;'
    try:
        res = subprocess.run(
            [mariadb_cli, "-h", "127.0.0.1", "-P", str(state["mariadb_port"]), "-u", "root", "-e", cmd],
            cwd=mariadb_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return res.returncode == 0
    except Exception:
        return False

def create_virtual_host(project_name, is_laravel=False):
    if not is_valid_project_name(project_name):
        raise ValueError("Nombre de proyecto inválido.")
    state = load_state()
    proj_dir = get_projects_root().replace("\\", "/")
    vhost_file = os.path.join(CONF_DIR, "vhosts", f"{project_name}.conf")
    doc_root = f"{proj_dir}/{project_name}/public" if is_laravel else f"{proj_dir}/{project_name}"
    fastcgi_params = f"{BASE_DIR_SLASH}/bin/nginx/conf/fastcgi_params"
    
    content = vhosts.render_vhost(project_name, doc_root, state["nginx_port"], fastcgi_params,
                                  state.get("vhost_tld"))
    with open(vhost_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    reload_nginx_if_running()

def adopt_existing_projects():
    """
    Crea el virtual host de cada proyecto WordPress/Laravel que ya está en la carpeta de proyectos
    (por ejemplo, venidos de Laragon). No toca sus archivos ni sus bases de datos.
    Devuelve [(nombre, dominio)].
    """
    state = load_state()
    adopted = []
    for p in list_projects():
        create_virtual_host(p["name"], is_laravel=(p["type"] == "Laravel"))
        adopted.append((p["name"], vhosts.domain_for(p["name"], state.get("vhost_tld"))))
    return adopted

def project_domains():
    """Dominios de desarrollo de los proyectos detectados (ej. frutiflex.test)."""
    tld = load_state().get("vhost_tld")
    return [vhosts.domain_for(p["name"], tld) for p in list_projects()]

def sync_hosts():
    """
    Deja en el archivo hosts de Windows los dominios de los proyectos, dentro de un bloque propio.
    Devuelve "unchanged", "updated", "cancelled" (el usuario rechazó el aviso de Windows) o "error".
    """
    try:
        return hosts.sync(project_domains(), backup_dir=CONF_DIR)
    except Exception:
        return "error"

def _hosts_note():
    """Registra el dominio del proyecto nuevo en hosts; devuelve un aviso si no se pudo."""
    result = sync_hosts()
    if result in ("cancelled", "error"):
        return (" Aviso: no se pudo registrar el dominio en el archivo hosts de Windows; "
                "usa Ajustes > Importar proyectos y hosts para activarlo.")
    return ""

def list_projects():
    state = load_state()
    proj_root = get_projects_root()
    port = state.get("nginx_port", 80)
    port_str = f":{port}" if port != 80 else ""

    projects = []
    if not os.path.exists(proj_root):
        return projects

    for entry in os.scandir(proj_root):
        # Solo carpetas con nombre seguro (ver PROJECT_NAME_RE); el resto se ignora.
        if not (entry.is_dir() and entry.name.lower() != "aetherstack"
                and is_valid_project_name(entry.name)):
            continue

        folder_path = entry.path

        # Detección estricta de Laravel (presencia de artisan)
        is_laravel = os.path.exists(os.path.join(folder_path, "artisan"))

        # Detección estricta de WordPress (archivos de núcleo WP)
        is_wp = any(
            os.path.exists(os.path.join(folder_path, f))
            for f in ("wp-config.php", "wp-config-sample.php", "wp-settings.php", "wp-load.php")
        )

        # Solo incluir si es estrictamente Laravel o WordPress
        if not (is_laravel or is_wp):
            continue

        p_type = "Laravel" if is_laravel else "WordPress"
        url_sub = f"http://localhost{port_str}/{entry.name}/public" if is_laravel else f"http://localhost{port_str}/{entry.name}"
        url_vhost = f"http://{vhosts.domain_for(entry.name, state.get('vhost_tld'))}{port_str}"

        projects.append({
            "name": entry.name,
            "type": p_type,
            "path": folder_path,
            "url": url_sub,
            "vhost": url_vhost,
            "db_name": db_name_for(entry.name)
        })
    return projects

def delete_project(project_name, delete_db=True):
    target_dir = get_safe_project_path(project_name)
    if target_dir is None:
        return False, f"Nombre de proyecto inválido: '{project_name}'."

    if not os.path.exists(target_dir):
        return False, f"La carpeta '{project_name}' no existe."

    base = os.path.normcase(os.path.realpath(BASE_DIR))
    if os.path.normcase(target_dir) == base or base.startswith(os.path.normcase(target_dir) + os.sep):
        return False, f"'{project_name}' contiene AetherStack: no se puede eliminar."
    is_project = os.path.exists(os.path.join(target_dir, "artisan")) or any(
        os.path.exists(os.path.join(target_dir, f))
        for f in ("wp-config.php", "wp-config-sample.php", "wp-settings.php", "wp-load.php"))
    if not is_project:
        return False, f"'{project_name}' no es un proyecto WordPress ni Laravel: no se elimina."

    # 1. Eliminar base de datos si se solicitó
    db_note = ""
    if delete_db:
        db_name = db_name_for(project_name)
        # "mi-sitio" y "mi_sitio" comparten base: si otro proyecto usa la misma, no se borra
        shared = [p["name"] for p in list_projects()
                  if p["name"] != project_name and db_name_for(p["name"]) == db_name]
        if shared:
            db_note = f" La base '{db_name}' se conservó porque también la usa '{shared[0]}'."
        else:
            drop_database(db_name)

    # 2. Eliminar Virtual Host
    vhost_file = os.path.join(CONF_DIR, "vhosts", f"{project_name}.conf")
    if os.path.exists(vhost_file):
        try:
            os.remove(vhost_file)
            reload_nginx_if_running()
        except OSError:
            pass

    # 3. Eliminar directorio de archivos con soporte para archivos de solo lectura y Git
    def _handle_remove_readonly(func, path, _):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except OSError:
            pass

    try:
        shutil.rmtree(target_dir, onerror=_handle_remove_readonly)
    except OSError:
        pass

    # Fallback por si Windows retiene algún descriptor de archivo brevemente
    if os.path.exists(target_dir):
        time.sleep(0.5)
        try:
            shutil.rmtree(target_dir, onerror=_handle_remove_readonly)
        except OSError:
            pass

    if not os.path.exists(target_dir):
        return True, f"Proyecto '{project_name}' eliminado completamente.{db_note}"
    return False, f"No se pudo eliminar completamente la carpeta '{project_name}' (bloqueo en Windows)."

def create_project_laravel(project_name, progress_cb=None):
    target_dir = get_safe_project_path(project_name)
    if target_dir is None:
        return False, "Nombre inválido: usa solo letras, números, guion (-) y guion bajo (_)."
    status = get_status()
    if not status["all_running"]:
        return False, "No se puede crear el proyecto: los servicios del stack (Nginx, PHP o MariaDB) no están en ejecución."

    state = load_state()
    proj_root = get_projects_root()
    php_ver = state.get("php_version", "8.4")
    php_exe = os.path.join(BIN_DIR, "php", f"php-{php_ver}", "php.exe")
    composer_phar = os.path.join(BIN_DIR, "composer", "composer.phar")

    if os.path.exists(target_dir):
        return False, f"La carpeta '{project_name}' ya existe en {proj_root}."

    if progress_cb: progress_cb("Descargando e instalando Laravel con Composer...")
    cmd = [php_exe, composer_phar, "create-project", "laravel/laravel", target_dir, "--prefer-dist", "--no-interaction"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        return False, f"Error en Composer: {res.stderr}"

    db_name = db_name_for(project_name)
    if progress_cb: progress_cb(f"Creando base de datos '{db_name}'...")
    create_database(db_name)

    env_file = os.path.join(target_dir, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            env_content = f.read()
        env_content = env_content.replace("DB_HOST=127.0.0.1", f"DB_HOST=127.0.0.1\nDB_PORT={state['mariadb_port']}")
        env_content = env_content.replace("DB_PORT=3306", f"DB_PORT={state['mariadb_port']}")
        env_content = env_content.replace("DB_DATABASE=laravel", f"DB_DATABASE={db_name}")
        env_content = env_content.replace("DB_USERNAME=root", "DB_USERNAME=root")
        env_content = env_content.replace("DB_PASSWORD=", "DB_PASSWORD=")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)

    create_virtual_host(project_name, is_laravel=True)
    return True, f"Proyecto Laravel '{project_name}' listo en {target_dir}." + _hosts_note()

def create_project_wordpress(project_name, progress_cb=None):
    target_dir = get_safe_project_path(project_name)
    if target_dir is None:
        return False, "Nombre inválido: usa solo letras, números, guion (-) y guion bajo (_)."
    status = get_status()
    if not status["all_running"]:
        return False, "No se puede crear el proyecto: los servicios del stack (Nginx, PHP o MariaDB) no están en ejecución."

    state = load_state()
    proj_root = get_projects_root()
    if os.path.exists(target_dir):
        return False, f"La carpeta '{project_name}' ya existe en {proj_root}."

    # Descarga verificada contra el hash oficial de wordpress.org (ver downloads.py)
    try:
        wp_zip = downloads.ensure_verified_zip(
            WORDPRESS_URL, WORDPRESS_URL + ".sha1",
            os.path.join(BASE_DIR, "downloads", "wordpress-latest.zip"),
            algo="sha1", progress_cb=progress_cb)
    except downloads.DownloadError as exc:
        return False, f"No se pudo obtener WordPress: {exc}"

    if progress_cb: progress_cb("Descomprimiendo archivos de WordPress...")
    os.makedirs(os.path.join(BASE_DIR, "downloads"), exist_ok=True)
    temp_extract = tempfile.mkdtemp(prefix="temp_wp_", dir=os.path.join(BASE_DIR, "downloads"))
    with zipfile.ZipFile(wp_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_extract)
    
    shutil.move(os.path.join(temp_extract, "wordpress"), target_dir)
    shutil.rmtree(temp_extract, ignore_errors=True)

    db_name = db_name_for(project_name)
    if progress_cb: progress_cb(f"Creando base de datos '{db_name}'...")
    create_database(db_name)

    wp_sample = os.path.join(target_dir, "wp-config-sample.php")
    wp_config = os.path.join(target_dir, "wp-config.php")
    if os.path.exists(wp_sample):
        with open(wp_sample, "r", encoding="utf-8") as f:
            cfg = f.read()
        cfg = cfg.replace("database_name_here", db_name)
        cfg = cfg.replace("username_here", "root")
        cfg = cfg.replace("password_here", "")
        cfg = cfg.replace("localhost", f"127.0.0.1:{state['mariadb_port']}")
        with open(wp_config, "w", encoding="utf-8") as f:
            f.write(cfg)

    create_virtual_host(project_name, is_laravel=False)
    return True, f"WordPress '{project_name}' listo con base de datos '{db_name}'." + _hosts_note()

def open_db_manager(db_name=None):
    """Abre el gestor de base de datos HeidiSQL Portable conectado a MariaDB."""
    state = load_state()
    port = state.get("mariadb_port", 3307)
    heidisql_exe = os.path.join(BIN_DIR, "heidisql", "heidisql.exe")

    if os.path.exists(heidisql_exe):
        args = [
            heidisql_exe,
            "-h=127.0.0.1",
            f"-P={port}",
            "-u=root",
        ]
        if db_name:
            args.append(f"-d={db_name}")
        try:
            subprocess.Popen(args, cwd=os.path.dirname(heidisql_exe))
            return True
        except Exception:
            pass
    return False

# Sincronización automática de rutas portables en cada carga de módulo
try:
    update_mariadb_config()
    update_nginx_config()
    update_php_configs()
    sync_vhosts_paths()
except Exception:
    pass


