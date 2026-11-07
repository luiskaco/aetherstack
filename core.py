"""
AetherStack - Minimalist Local Dev Core Engine
Servicios: Nginx, PHP FastCGI (8.4/8.5), MariaDB
Diseño 100% portable y desacoplado de la terminal.
"""
import os
import sys
import subprocess
import time
import socket
import json
import shutil
import urllib.request
import zipfile

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
CONF_DIR = os.path.join(BASE_DIR, "conf")
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
PROJECTS_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
STATE_FILE = os.path.join(CONF_DIR, "state.json")

DEFAULT_CONFIG = {
    "php_version": "8.4",
    "nginx_port": 80,
    "mariadb_port": 3307,
    "php_port": 9000,
    "projects_dir": PROJECTS_ROOT
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

def is_port_in_use(port, host='127.0.0.1'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
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
    
    # Comprobar tanto puerto como proceso para máxima precisión
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
        "all_running": nginx_running and php_running and mariadb_running
    }

def start_services(php_version=None):
    state = load_state()
    if php_version:
        state["php_version"] = php_version
        save_state(state)

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
        subprocess.run(
            [nginx_exe, "-s", "stop", "-p", nginx_dir],
            cwd=nginx_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
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
    mariadb_dir = os.path.join(BIN_DIR, "mariadb")
    mariadb_cli = os.path.join(mariadb_dir, "mariadb.exe")
    cmd = f'CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
    try:
        res = subprocess.run(
            [mariadb_cli, "-h", "127.0.0.1", "-P", "3307", "-u", "root", "-e", cmd],
            cwd=mariadb_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return res.returncode == 0, f"Base de datos '{db_name}' creada en MariaDB."
    except Exception as e:
        return False, str(e)

def create_virtual_host(project_name, is_laravel=False):
    vhost_file = os.path.join(CONF_DIR, "vhosts", f"{project_name}.conf")
    doc_root = f"D:/LabIA/{project_name}/public" if is_laravel else f"D:/LabIA/{project_name}"
    
    raw_template = """# Virtual host para {name}
server {{
    listen 80;
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
    content = raw_template.format(name=project_name, root=doc_root)
    with open(vhost_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    if is_process_running("nginx.exe"):
        nginx_dir = os.path.join(BIN_DIR, "nginx")
        nginx_exe = os.path.join(nginx_dir, "nginx.exe")
        subprocess.run(
            [nginx_exe, "-s", "reload", "-p", nginx_dir],
            cwd=nginx_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

def create_project_laravel(project_name, progress_cb=None):
    state = load_state()
    php_ver = state.get("php_version", "8.4")
    php_exe = os.path.join(BIN_DIR, "php", f"php-{php_ver}", "php.exe")
    composer_phar = os.path.join(BIN_DIR, "composer", "composer.phar")
    target_dir = os.path.join(PROJECTS_ROOT, project_name)

    if os.path.exists(target_dir):
        return False, f"La carpeta '{project_name}' ya existe en D:\\LabIA."

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
        env_content = env_content.replace("DB_HOST=127.0.0.1", "DB_HOST=127.0.0.1\nDB_PORT=3307")
        env_content = env_content.replace("DB_PORT=3306", "DB_PORT=3307")
        env_content = env_content.replace("DB_DATABASE=laravel", f"DB_DATABASE={db_name}")
        env_content = env_content.replace("DB_USERNAME=root", "DB_USERNAME=root")
        env_content = env_content.replace("DB_PASSWORD=", "DB_PASSWORD=")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)

    create_virtual_host(project_name, is_laravel=True)
    return True, f"Proyecto Laravel '{project_name}' listo en D:\\LabIA\\{project_name}."

def create_project_wordpress(project_name, progress_cb=None):
    target_dir = os.path.join(PROJECTS_ROOT, project_name)
    if os.path.exists(target_dir):
        return False, f"La carpeta '{project_name}' ya existe en D:\\LabIA."

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
        cfg = cfg.replace("localhost", "127.0.0.1:3307")
        with open(wp_config, "w", encoding="utf-8") as f:
            f.write(cfg)

    create_virtual_host(project_name, is_laravel=False)
    return True, f"WordPress '{project_name}' listo con base de datos '{db_name}'."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "status":
            print(json.dumps(get_status(), indent=2))
        elif action == "start":
            ver = sys.argv[2] if len(sys.argv) > 2 else None
            print(json.dumps(start_services(ver), indent=2))
        elif action == "stop":
            print(json.dumps(stop_services(), indent=2))
        elif action == "switch-php":
            print(json.dumps(switch_php(sys.argv[2]), indent=2))
        elif action == "create-laravel":
            print(create_project_laravel(sys.argv[2]))
        elif action == "create-wp":
            print(create_project_wordpress(sys.argv[2]))
