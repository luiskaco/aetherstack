"""
AetherStack - Minimalist Local Dev Environment
UI Nativa en Modo Oscuro Minimalista
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
import core

BG_COLOR = "#0F172A"
CARD_BG = "#1E293B"
BORDER_COLOR = "#334155"
TEXT_MAIN = "#F8FAFC"
TEXT_MUTED = "#94A3B8"
ACCENT_CYAN = "#38BDF8"
SUCCESS_GREEN = "#10B981"
DANGER_RED = "#EF4444"

class AetherStackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AetherStack")
        self.root.geometry("520x640")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self.state = core.load_state()
        self.selected_php = tk.StringVar(value=self.state.get("php_version", "8.4"))

        self.build_ui()
        self.update_status_display()
        self.start_status_loop()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=BG_COLOR)
        header.pack(fill="x", padx=28, pady=(24, 16))

        top_row = tk.Frame(header, bg=BG_COLOR)
        top_row.pack(fill="x")

        logo_title = tk.Label(top_row, text="AetherStack", font=("Segoe UI", 20, "bold"), fg=TEXT_MAIN, bg=BG_COLOR)
        logo_title.pack(side="left")

        badge = tk.Label(top_row, text="v1.0 - Portable", font=("Segoe UI", 8, "bold"), fg=ACCENT_CYAN, bg="#082F49", padx=8, pady=2)
        badge.pack(side="left", padx=(12, 0), pady=(4, 0))

        subtitle = tk.Label(
            header,
            text="Entorno local ultraligero - Nginx - PHP 8.4/8.5 - MariaDB",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_COLOR
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        # Tarjeta de Servicios
        card = tk.Frame(self.root, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
        card.pack(fill="x", padx=28, pady=8)

        card_title = tk.Label(card, text="ESTADO DE SERVICIOS", font=("Segoe UI", 8, "bold"), fg=TEXT_MUTED, bg=CARD_BG)
        card_title.pack(anchor="w", padx=20, pady=(16, 12))

        self.row_nginx = self.create_service_row(card, "Nginx Web Server", "Puerto 80")
        self.row_php = self.create_service_row(card, "PHP FastCGI", "Puerto 9000")
        self.row_mariadb = self.create_service_row(card, "MariaDB (MySQL)", "Puerto 3307")

        php_switch_frame = tk.Frame(card, bg=CARD_BG)
        php_switch_frame.pack(fill="x", padx=20, pady=(12, 16))

        lbl_switch = tk.Label(php_switch_frame, text="Version activa de PHP:", font=("Segoe UI", 9), fg=TEXT_MAIN, bg=CARD_BG)
        lbl_switch.pack(side="left")

        r84 = tk.Radiobutton(
            php_switch_frame, text="PHP 8.4", variable=self.selected_php, value="8.4",
            command=self.on_php_switch, bg=CARD_BG, fg=TEXT_MAIN, selectcolor=BG_COLOR,
            activebackground=CARD_BG, activeforeground=ACCENT_CYAN, font=("Segoe UI", 9, "bold")
        )
        r84.pack(side="left", padx=(16, 8))

        r85 = tk.Radiobutton(
            php_switch_frame, text="PHP 8.5", variable=self.selected_php, value="8.5",
            command=self.on_php_switch, bg=CARD_BG, fg=TEXT_MAIN, selectcolor=BG_COLOR,
            activebackground=CARD_BG, activeforeground=ACCENT_CYAN, font=("Segoe UI", 9, "bold")
        )
        r85.pack(side="left", padx=8)

        # Boton Maestro
        action_frame = tk.Frame(self.root, bg=BG_COLOR)
        action_frame.pack(fill="x", padx=28, pady=12)

        self.btn_master = tk.Button(
            action_frame,
            text="INICIAR TODOS LOS SERVICIOS",
            font=("Segoe UI", 10, "bold"),
            bg=SUCCESS_GREEN,
            fg="#FFFFFF",
            activebackground="#059669",
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            pady=12,
            cursor="hand2",
            command=self.toggle_services
        )
        self.btn_master.pack(fill="x")

        # Seccion de Creador Rapido
        proj_card = tk.Frame(self.root, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
        proj_card.pack(fill="x", padx=28, pady=8)

        proj_title = tk.Label(proj_card, text="CREAR PROYECTO RAPIDO", font=("Segoe UI", 8, "bold"), fg=TEXT_MUTED, bg=CARD_BG)
        proj_title.pack(anchor="w", padx=20, pady=(16, 12))

        btn_row = tk.Frame(proj_card, bg=CARD_BG)
        btn_row.pack(fill="x", padx=20, pady=(0, 16))

        btn_laravel = tk.Button(
            btn_row,
            text="Nuevo Laravel",
            font=("Segoe UI", 9, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.create_laravel_modal
        )
        btn_laravel.pack(side="left", expand=True, fill="x", padx=(0, 6))

        btn_wp = tk.Button(
            btn_row,
            text="Nuevo WordPress",
            font=("Segoe UI", 9, "bold"),
            bg="#0284C7",
            fg="#FFFFFF",
            activebackground="#0369A1",
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.create_wp_modal
        )
        btn_wp.pack(side="right", expand=True, fill="x", padx=(6, 0))

        # Accesos Directos
        shortcuts_frame = tk.Frame(self.root, bg=BG_COLOR)
        shortcuts_frame.pack(fill="x", padx=28, pady=12)

        btn_open_web = tk.Button(
            shortcuts_frame, text="Abrir Localhost", font=("Segoe UI", 9),
            bg=CARD_BG, fg=TEXT_MAIN, bd=0, relief="flat", pady=8, cursor="hand2",
            command=lambda: os.system("start http://localhost")
        )
        btn_open_web.pack(side="left", expand=True, fill="x", padx=(0, 4))

        btn_open_dir = tk.Button(
            shortcuts_frame, text="Carpeta D:\\LabIA", font=("Segoe UI", 9),
            bg=CARD_BG, fg=TEXT_MAIN, bd=0, relief="flat", pady=8, cursor="hand2",
            command=lambda: os.system('explorer "D:\\LabIA"')
        )
        btn_open_dir.pack(side="left", expand=True, fill="x", padx=(4, 4))

        btn_open_cli = tk.Button(
            shortcuts_frame, text="Terminal Dev", font=("Segoe UI", 9),
            bg=CARD_BG, fg=TEXT_MAIN, bd=0, relief="flat", pady=8, cursor="hand2",
            command=self.open_dev_terminal
        )
        btn_open_cli.pack(side="right", expand=True, fill="x", padx=(4, 0))

        self.status_bar = tk.Label(self.root, text="Listo", font=("Segoe UI", 8), fg=TEXT_MUTED, bg=BG_COLOR)
        self.status_bar.pack(side="bottom", pady=8)

    def create_service_row(self, parent, name, port_info):
        frame = tk.Frame(parent, bg=CARD_BG)
        frame.pack(fill="x", padx=20, pady=4)

        dot = tk.Label(frame, text="*", font=("Segoe UI", 12), fg="#64748B", bg=CARD_BG)
        dot.pack(side="left")

        title = tk.Label(frame, text=f" {name}", font=("Segoe UI", 10), fg=TEXT_MAIN, bg=CARD_BG)
        title.pack(side="left")

        port = tk.Label(frame, text=port_info, font=("Segoe UI", 9), fg=TEXT_MUTED, bg=CARD_BG)
        port.pack(side="right")

        return {"dot": dot, "title": title}

    def update_status_display(self):
        status = core.get_status()
        
        self.row_nginx["dot"].config(fg=SUCCESS_GREEN if status["nginx"]["running"] else "#64748B")
        self.row_php["dot"].config(fg=SUCCESS_GREEN if status["php"]["running"] else "#64748B")
        self.row_php["title"].config(text=f" PHP FastCGI (v{status['php']['version']})")
        self.row_mariadb["dot"].config(fg=SUCCESS_GREEN if status["mariadb"]["running"] else "#64748B")

        if status["all_running"]:
            self.btn_master.config(text="DETENER TODOS LOS SERVICIOS", bg=DANGER_RED, activebackground="#DC2626")
            self.status_bar.config(text="Todos los servicios activos y listos para trabajar")
        else:
            self.btn_master.config(text="INICIAR TODOS LOS SERVICIOS", bg=SUCCESS_GREEN, activebackground="#059669")
            self.status_bar.config(text="Servicios en reposo")

    def start_status_loop(self):
        def loop():
            self.update_status_display()
            self.root.after(3000, self.start_status_loop)
        self.root.after(3000, loop)

    def toggle_services(self):
        status = core.get_status()
        self.btn_master.config(text="Procesando...", state="disabled")
        self.root.update()

        def run():
            if status["all_running"]:
                core.stop_services()
            else:
                core.start_services(self.selected_php.get())
            self.root.after(100, lambda: [self.btn_master.config(state="normal"), self.update_status_display()])

        threading.Thread(target=run, daemon=True).start()

    def on_php_switch(self):
        ver = self.selected_php.get()
        self.status_bar.config(text=f"Cambiando a PHP {ver}...")
        self.root.update()

        def run():
            core.switch_php(ver)
            self.root.after(100, self.update_status_display)

        threading.Thread(target=run, daemon=True).start()

    def open_dev_terminal(self):
        ver = self.selected_php.get()
        php_dir = os.path.join(core.BIN_DIR, "php", f"php-{ver}")
        mariadb_bin = os.path.join(core.BIN_DIR, "mariadb")
        composer_dir = os.path.join(core.BIN_DIR, "composer")
        
        env_cmd = f'set "PATH={php_dir};{composer_dir};{mariadb_bin};%PATH%" & cd /d "D:\\LabIA" & start cmd.exe /k "echo AetherStack Dev Terminal (PHP {ver}) & echo."'
        os.system(env_cmd)

    def create_laravel_modal(self):
        name = simpledialog.askstring("Nuevo Proyecto Laravel", "Nombre de la carpeta para el proyecto (ej: tienda):", parent=self.root)
        if not name:
            return
        name = name.strip()

        self.status_bar.config(text=f"Creando Laravel '{name}'... Esto puede tardar 1 minuto.")
        self.root.update()

        def run():
            success, msg = core.create_project_laravel(name)
            if success:
                messagebox.showinfo("AetherStack", f"Proyecto Laravel '{name}' creado con exito!\nBase de datos: {name}_db en puerto 3307")
            else:
                messagebox.showerror("Error", msg)
            self.update_status_display()

        threading.Thread(target=run, daemon=True).start()

    def create_wp_modal(self):
        name = simpledialog.askstring("Nuevo Proyecto WordPress", "Nombre de la carpeta para WordPress (ej: blog):", parent=self.root)
        if not name:
            return
        name = name.strip()

        self.status_bar.config(text=f"Creando WordPress '{name}'...")
        self.root.update()

        def run():
            success, msg = core.create_project_wordpress(name)
            if success:
                messagebox.showinfo("AetherStack", f"Sitio WordPress '{name}' creado con exito!\nBase de datos: {name}_db configurada.")
            else:
                messagebox.showerror("Error", msg)
            self.update_status_display()

        threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AetherStackApp(root)
    root.mainloop()
