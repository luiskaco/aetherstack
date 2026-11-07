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
import stat
import urllib.request
import zipfile

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
CONF_DIR = os.path.join(BASE_DIR, "conf")
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
STATE_FILE = os.path.join(CONF_DIR, "state.json")

DEFAULT_CONFIG = {
    "php_version": "8.4",
    "nginx_port": 80,
    "mariadb_port": 3307,
    "php_port": 9000,
    "projects_dir": "D:\\\\LabIA",
    "theme": "dark"
}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

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

def is_process_running(process_name):
    try:
        output = subprocess.check_output(
            f'tasklist /FI "IMAGENAME eq {process_name}" /NH',
            shell=True, text=True, stderr=subprocess.DEVNULL
        )
        return process_name.lower() in output.lower()
    except Exception:
        return False

def get_status():
    state = load_state()
    php_ver = state.get("php_version", "8.4")
    
    nginx_running = is_process_running("nginx.exe") and is_port_in_use(state["nginx_port"])
    php_running = is_process_running("php-cgi.exe") and is_port_in_use(state["php_port"])
    mariadb_running = (is_process_running("mariadbd.exe") or is_process_running("mysqld.exe")) and is_port_in_use(state["mariadb_port"])

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

def update_nginx_config():
    state = load_state()
    proj_dir = state.get("projects_dir", "D:\\LabIA").replace("\\", "/")
    
    nginx_conf_content = f"""# AetherStack - Nginx Master Configuration
worker_processes  auto;

error_log  "D:/LabIA/aetherstack/logs/nginx_error.log" warn;
pid        "D:/LabIA/aetherstack/logs/nginx.pid";

events {{
    worker_connections  1024;
}}

http {{
    include       "D:/LabIA/aetherstack/bin/nginx/conf/mime.types";
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  "D:/LabIA/aetherstack/logs/nginx_access.log"  main;

    sendfile        on;
    tcp_nopush     on;
    tcp_nodelay    on;
    keepalive_timeout  65;
    types_hash_max_size 2048;

    client_max_body_size 128M;

    gzip  on;
    gzip_disable "msie6";
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    upstream php_cgi {{
        server 127.0.0.1:{state['php_port']};
        keepalive 16;
    }}

    server {{
        listen       {state['nginx_port']};
        server_name  localhost;

        root   "{proj_dir}";
        index  index.php index.html index.htm;

        location / {{
            autoindex on;
            try_files $uri $uri/ /index.php?$query_string;
        }}

        location ~ \\.php$ {{
            try_files $uri =404;
            fastcgi_split_path_info ^(.+\\.php)(/.+)$;
            fastcgi_pass   php_cgi;
            fastcgi_index  index.php;
            fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
            include        "D:/LabIA/aetherstack/bin/nginx/conf/fastcgi_params";
            fastcgi_read_timeout 300;
        }}

        location ~ /\\. {{
            deny all;
        }}
    }}

    include "D:/LabIA/aetherstack/conf/vhosts/*.conf";
}}
"""
    with open(os.path.join(CONF_DIR, "nginx.conf"), "w", encoding="utf-8") as f:
        f.write(nginx_conf_content)

def update_global_config(new_config):
    state = load_state()
    state.update(new_config)
    save_state(state)
    update_nginx_config()
    
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

    update_nginx_config()

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
    if not is_port_in_use(state["php_port"]):
        os.environ["PHP_FCGI_MAX_REQUESTS"] = "0"
        cmd = f'start /b "" "{php_cgi}" -b 127.0.0.1:{state["php_port"]} -c "{php_ini}"'
        subprocess.Popen(cmd, shell=True, cwd=php_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
    state = load_state()
    state["php_version"] = version
    save_state(state)
    
    subprocess.run("taskkill /F /IM php-cgi.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    
    php_dir = os.path.join(BIN_DIR, "php", f"php-{version}")
    php_cgi = os.path.join(php_dir, "php-cgi.exe")
    php_ini = os.path.join(php_dir, "php.ini")
    os.environ["PHP_FCGI_MAX_REQUESTS"] = "0"
    cmd = f'start /b "" "{php_cgi}" -b 127.0.0.1:{state["php_port"]} -c "{php_ini}"'
    subprocess.Popen(cmd, shell=True, cwd=php_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    return get_status()

def create_database(db_name):
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
    state = load_state()
    proj_dir = state.get("projects_dir", "D:\\LabIA").replace("\\", "/")
    vhost_file = os.path.join(CONF_DIR, "vhosts", f"{project_name}.conf")
    doc_root = f"{proj_dir}/{project_name}/public" if is_laravel else f"{proj_dir}/{project_name}"
    
    raw_template = """# Virtual host para {name}
server {{
    listen {port};
    server_name {name}.local;

    root "{root}";
    index index.php index.html;

    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}

    location ~ \\.php$ {{
        try_files $uri =404;
        fastcgi_split_path_info ^(.+\\.php)(/.+)$;
        fastcgi_pass php_cgi;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include "D:/LabIA/aetherstack/bin/nginx/conf/fastcgi_params";
        fastcgi_read_timeout 300;
    }}

    location ~ /\\. {{
        deny all;
    }}
}}
"""
    content = raw_template.format(name=project_name, root=doc_root, port=state["nginx_port"])
    with open(vhost_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    if is_process_running("nginx.exe"):
        nginx_dir = os.path.join(BIN_DIR, "nginx")
        nginx_exe = os.path.join(nginx_dir, "nginx.exe")
        subprocess.run([nginx_exe, "-s", "reload", "-p", nginx_dir], cwd=nginx_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def list_projects():
    state = load_state()
    proj_root = state.get("projects_dir", "D:\\LabIA")
    port = state.get("nginx_port", 80)
    port_str = f":{port}" if port != 80 else ""

    projects = []
    if not os.path.exists(proj_root):
        return projects

    for entry in os.scandir(proj_root):
        if entry.is_dir() and entry.name.lower() != "aetherstack" and not entry.name.startswith("."):
            folder_path = entry.path
            
            # Detección estricta de Laravel (presencia de artisan o composer con laravel)
            is_laravel = os.path.exists(os.path.join(folder_path, "artisan"))
            
            # Detección estricta de WordPress (archivos de núcleo WP)
            is_wp = (
                os.path.exists(os.path.join(folder_path, "wp-config.php")) or
                os.path.exists(os.path.join(folder_path, "wp-config-sample.php")) or
                os.path.exists(os.path.join(folder_path, "wp-settings.php")) or
                os.path.exists(os.path.join(folder_path, "wp-load.php"))
            )
            
            # Solo incluir si es estrictamente Laravel o WordPress
            if not (is_laravel or is_wp):
                continue
                
            p_type = "Laravel" if is_laravel else "WordPress"
            url_sub = f"http://localhost{port_str}/{entry.name}/public" if is_laravel else f"http://localhost{port_str}/{entry.name}"
            url_vhost = f"http://{entry.name}.local{port_str}"

            projects.append({
                "name": entry.name,
                "type": p_type,
                "path": folder_path,
                "url": url_sub,
                "vhost": url_vhost,
                "db_name": f"{entry.name.lower().replace('-', '_')}_db"
            })
    return projects

    for entry in os.scandir(proj_root):
        if entry.is_dir() and entry.name.lower() != "aetherstack" and not entry.name.startswith("."):
            folder_path = entry.path
            is_laravel = os.path.exists(os.path.join(folder_path, "artisan")) or os.path.exists(os.path.join(folder_path, "public", "index.php"))
            is_wp = os.path.exists(os.path.join(folder_path, "wp-config.php")) or os.path.exists(os.path.join(folder_path, "wp-settings.php"))
            
            p_type = "Laravel" if is_laravel else ("WordPress" if is_wp else "PHP / Web")
            url_sub = f"http://localhost{port_str}/{entry.name}/public" if is_laravel else f"http://localhost{port_str}/{entry.name}"
            url_vhost = f"http://{entry.name}.local{port_str}"

            projects.append({
                "name": entry.name,
                "type": p_type,
                "path": folder_path,
                "url": url_sub,
                "vhost": url_vhost,
                "db_name": f"{entry.name.lower().replace('-', '_')}_db"
            })
    return projects

def delete_project(project_name, delete_db=True):
    state = load_state()
    proj_root = state.get("projects_dir", "D:\\LabIA")
    target_dir = os.path.join(proj_root, project_name)

    if not os.path.exists(target_dir):
        return False, f"La carpeta '{project_name}' no existe."

    # 1. Eliminar base de datos si se solicitó
    if delete_db:
        db_name = f"{project_name.lower().replace('-', '_')}_db"
        drop_database(db_name)

    # 2. Eliminar Virtual Host
    vhost_file = os.path.join(CONF_DIR, "vhosts", f"{project_name}.conf")
    if os.path.exists(vhost_file):
        try:
            os.remove(vhost_file)
            if is_process_running("nginx.exe"):
                nginx_dir = os.path.join(BIN_DIR, "nginx")
                nginx_exe = os.path.join(nginx_dir, "nginx.exe")
                subprocess.run([nginx_exe, "-s", "reload", "-p", nginx_dir], cwd=nginx_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # 3. Eliminar directorio de archivos con soporte para archivos de solo lectura y Git
    def _handle_remove_readonly(func, path, _):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    try:
        shutil.rmtree(target_dir, onerror=_handle_remove_readonly)
    except Exception:
        pass

    # Fallback por si Windows retiene algún descriptor de archivo brevemente
    if os.path.exists(target_dir):
        try:
            subprocess.run(f'cmd /c rmdir /s /q "{target_dir}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    if not os.path.exists(target_dir):
        return True, f"Proyecto '{project_name}' eliminado completamente."
    else:
        return False, f"No se pudo eliminar completamente la carpeta '{project_name}' (bloqueo en Windows)."

def create_project_laravel(project_name, progress_cb=None):
    status = get_status()
    if not status["all_running"]:
        return False, "No se puede crear el proyecto: los servicios del stack (Nginx, PHP o MariaDB) no están en ejecución."

    state = load_state()
    proj_root = state.get("projects_dir", "D:\\LabIA")
    php_ver = state.get("php_version", "8.4")
    php_exe = os.path.join(BIN_DIR, "php", f"php-{php_ver}", "php.exe")
    composer_phar = os.path.join(BIN_DIR, "composer", "composer.phar")
    target_dir = os.path.join(proj_root, project_name)

    if os.path.exists(target_dir):
        return False, f"La carpeta '{project_name}' ya existe en {proj_root}."

    if progress_cb: progress_cb("Descargando e instalando Laravel con Composer...")
    cmd = [php_exe, composer_phar, "create-project", "laravel/laravel", target_dir, "--prefer-dist", "--no-interaction"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        return False, f"Error en Composer: {res.stderr}"

    db_name = f"{project_name.lower().replace('-', '_')}_db"
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
    return True, f"Proyecto Laravel '{project_name}' listo en {target_dir}."

def create_project_wordpress(project_name, progress_cb=None):
    status = get_status()
    if not status["all_running"]:
        return False, "No se puede crear el proyecto: los servicios del stack (Nginx, PHP o MariaDB) no están en ejecución."

    state = load_state()
    proj_root = state.get("projects_dir", "D:\\LabIA")
    target_dir = os.path.join(proj_root, project_name)
    if os.path.exists(target_dir):
        return False, f"La carpeta '{project_name}' ya existe en {proj_root}."

    wp_zip = os.path.join(BASE_DIR, "downloads", "wordpress-latest.zip")
    if not os.path.exists(wp_zip):
        if progress_cb: progress_cb("Descargando WordPress oficial...")
        urllib.request.urlretrieve("https://wordpress.org/latest.zip", wp_zip)

    if progress_cb: progress_cb("Descomprimiendo archivos de WordPress...")
    temp_extract = os.path.join(BASE_DIR, "downloads", "temp_wp")
    with zipfile.ZipFile(wp_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_extract)
    
    shutil.move(os.path.join(temp_extract, "wordpress"), target_dir)
    shutil.rmtree(temp_extract, ignore_errors=True)

    db_name = f"{project_name.lower().replace('-', '_')}_db"
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
    return True, f"WordPress '{project_name}' listo con base de datos '{db_name}'."


