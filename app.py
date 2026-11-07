"""
AetherStack - Desktop Runner con PyWebView
Interfaz nativa ultra moderna con motor Edge Chromium.
"""
import os
import sys
import webview
import tkinter as tk
from tkinter import filedialog
import core

class AetherBridge:
    def __init__(self, window=None):
        self.window = window

    def get_status(self):
        return core.get_status()

    def start_services(self):
        return core.start_services()

    def stop_services(self):
        return core.stop_services()

    def switch_php(self, version):
        return core.switch_php(version)

    def update_config(self, new_config):
        return core.update_global_config(new_config)

    def choose_folder(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder = filedialog.askdirectory(title="Seleccionar carpeta de proyectos")
        root.destroy()
        return folder if folder else ""

    def create_project(self, project_type, name):
        if project_type == "laravel":
            success, msg = core.create_project_laravel(name)
        else:
            success, msg = core.create_project_wordpress(name)
        return {"success": success, "message": msg}

    def open_localhost(self):
        state = core.load_state()
        port = state.get("nginx_port", 80)
        url = f"http://localhost:{port}" if port != 80 else "http://localhost"
        os.system(f"start {url}")

    def open_projects_dir(self):
        state = core.load_state()
        p_dir = state.get("projects_dir", "D:\\LabIA")
        os.system(f'explorer "{p_dir}"')

    def open_terminal(self):
        state = core.load_state()
        ver = state.get("php_version", "8.4")
        p_dir = state.get("projects_dir", "D:\\LabIA")
        php_dir = os.path.join(core.BIN_DIR, "php", f"php-{ver}")
        mariadb_bin = os.path.join(core.BIN_DIR, "mariadb")
        composer_dir = os.path.join(core.BIN_DIR, "composer")
        
        env_cmd = f'set "PATH={php_dir};{composer_dir};{mariadb_bin};%PATH%" & cd /d "{p_dir}" & start cmd.exe /k "echo AetherStack Dev Shell (PHP {ver}) & echo."'
        os.system(env_cmd)

def main():
    bridge = AetherBridge()
    html_path = os.path.join(os.path.dirname(__file__), "ui", "web", "dashboard.html")

    window = webview.create_window(
        title="AetherStack",
        url=f"file:///{html_path.replace(os.sep, '/')}",
        js_api=bridge,
        width=480,
        height=620,
        resizable=False,
        easy_drag=True
    )
    bridge.window = window
    webview.start(debug=False)

if __name__ == "__main__":
    main()
