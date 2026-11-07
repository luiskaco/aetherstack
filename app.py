"""
AetherStack - App Runner Standalone
Lanza un servidor local HTTP ligero para la interfaz y abre una ventana de aplicación Edge limpia.
0% dependencias frágiles de WebView2 .NET, 100% estable y ultra rápida.
"""
import os
import sys
import json
import threading
import subprocess
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
import tkinter as tk
from tkinter import filedialog
import core

PORT = 5055
server_instance = None

class AetherHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silenciar logs en consola

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html_file = os.path.join(os.path.dirname(__file__), "ui", "web", "dashboard.html")
            with open(html_file, "rb") as f:
                self.wfile.write(f.read())
            return

        if parsed.path == "/api/status":
            self.send_json(core.get_status())
            return

        if parsed.path == "/api/projects":
            self.send_json(core.list_projects())
            return

        if parsed.path == "/api/choose-folder":
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            folder = filedialog.askdirectory(title="Seleccionar carpeta de proyectos")
            root.destroy()
            self.send_json({"folder": folder if folder else ""})
            return

        if parsed.path == "/api/open-localhost":
            state = core.load_state()
            port = state.get("nginx_port", 80)
            url = f"http://localhost:{port}" if port != 80 else "http://localhost"
            os.system(f"start {url}")
            self.send_json({"ok": True})
            return

        if parsed.path == "/api/open-projects-dir":
            state = core.load_state()
            p_dir = state.get("projects_dir", "D:\\LabIA")
            os.system(f'explorer "{p_dir}"')
            self.send_json({"ok": True})
            return

        if parsed.path == "/api/open-terminal":
            state = core.load_state()
            ver = state.get("php_version", "8.4")
            p_dir = state.get("projects_dir", "D:\\LabIA")
            php_dir = os.path.join(core.BIN_DIR, "php", f"php-{ver}")
            mariadb_bin = os.path.join(core.BIN_DIR, "mariadb")
            composer_dir = os.path.join(core.BIN_DIR, "composer")
            env_cmd = f'set "PATH={php_dir};{composer_dir};{mariadb_bin};%PATH%" & cd /d "{p_dir}" & start cmd.exe /k "echo AetherStack Dev Shell (PHP {ver}) & echo."'
            os.system(env_cmd)
            self.send_json({"ok": True})
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode('utf-8')
        data = json.loads(post_body) if post_body else {}

        if parsed.path == "/api/start":
            res = core.start_services()
            self.send_json(res)
            return

        if parsed.path == "/api/stop":
            res = core.stop_services()
            self.send_json(res)
            return

        if parsed.path == "/api/switch-php":
            ver = data.get("version", "8.4")
            res = core.switch_php(ver)
            self.send_json(res)
            return

        if parsed.path == "/api/config":
            res = core.update_global_config(data)
            self.send_json(res)
            return

        if parsed.path == "/api/create-project":
            ptype = data.get("type", "laravel")
            name = data.get("name", "")
            if ptype == "laravel":
                success, msg = core.create_project_laravel(name)
            else:
                success, msg = core.create_project_wordpress(name)
            self.send_json({"success": success, "message": msg})
            return

        if parsed.path == "/api/delete-project":
            name = data.get("name", "")
            success, msg = core.delete_project(name, delete_db=True)
            self.send_json({"success": success, "message": msg})
            return

        if parsed.path == "/api/open-url":
            url = data.get("url", "http://localhost")
            os.system(f'start {url}')
            self.send_json({"ok": True})
            return

        if parsed.path == "/api/open-folder":
            folder = data.get("folder", "D:\\LabIA")
            os.system(f'explorer "{folder}"')
            self.send_json({"ok": True})
            return

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def run_server():
    global server_instance
    try:
        server_instance = HTTPServer(('127.0.0.1', PORT), AetherHandler)
        server_instance.serve_forever()
    except Exception as e:
        print("Error en server:", e)

def main():
    # Iniciar servidor en hilo separado
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(0.5)

    app_url = f"http://127.0.0.1:{PORT}"
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    user_data = r"D:\LabIA\aetherstack\data\edge_profile"

    # Lanzar Edge en modo App de escritorio aislado
    cmd = [
        edge_exe,
        f"--app={app_url}",
        f"--user-data-dir={user_data}",
        "--window-size=520,720",
        "--disable-extensions",
        "--disable-plugins"
    ]
    p = subprocess.Popen(cmd)
    p.wait()

if __name__ == "__main__":
    main()
