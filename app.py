"""
AetherStack - Material Design 3 (M3 Dark Theme)
Implementación nativa de Material Design:
- Tokens de color M3 (Surface, Surface Container, Primary, Secondary Container, Error, Outline)
- Tipografía Roboto/Segoe UI con jerarquía M3 (Title, Body, Label)
- Elevación tonal sutil y esquinas redondeadas M3 (Large: 16px, Full: 24px)
"""
import os
import sys
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
import core

# Tokens de Color Material Design 3 (Dark Scheme)
M3_SURFACE = "#111318"             # Fondo base
M3_SURFACE_CONTAINER = "#1D2024"   # Tarjetas principales
M3_SURFACE_HIGH = "#282A2F"        # Tarjetas elevadas / modales
M3_PRIMARY = "#A8C7FA"             # Azul M3 primario
M3_ON_PRIMARY = "#062E6F"          # Texto sobre botón primario
M3_PRIMARY_CONTAINER = "#0842A0"   # Contenedores primarios suaves
M3_ON_PRIMARY_CONTAINER = "#D3E3FD"
M3_SECONDARY_CONTAINER = "#3B4858" # Botones secundarios tonales
M3_ON_SECONDARY = "#D7E3F8"
M3_TERTIARY = "#7FCFFF"            # Acento cian
M3_OUTLINE = "#43474E"             # Bordes sutiles M3
M3_SUCCESS = "#6DD58C"             # Estado activo (Green M3)
M3_ERROR = "#F2B8B5"               # Rojo M3 suave
M3_ON_ERROR = "#601410"
M3_ERROR_CONTAINER = "#8C1D18"
M3_TEXT_PRIMARY = "#E2E2E6"        # On Surface
M3_TEXT_SECONDARY = "#C4C7C5"      # On Surface Variant
M3_TEXT_MUTED = "#8E9192"          # Outline Variant

ctk.set_appearance_mode("Dark")

class AetherMaterialApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AetherStack")
        self.geometry("540x700")
        self.resizable(False, False)
        self.configure(fg_color=M3_SURFACE)

        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.state_data = core.load_state()
        self.php_var = ctk.StringVar(value=self.state_data.get("php_version", "8.4"))

        self.build_m3_ui()
        self.refresh_status()
        self.auto_refresh_loop()

    def build_m3_ui(self):
        # 1. Top App Bar (Material 3 Top Bar)
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=24, pady=(20, 10))

        title_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_box.pack(side="left")

        app_title = ctk.CTkLabel(title_box, text="AetherStack",
                                 font=ctk.CTkFont(size=22, weight="bold"),
                                 text_color=M3_TEXT_PRIMARY)
        app_title.pack(anchor="w")

        app_sub = ctk.CTkLabel(title_box, text="Material Web Stack • Nginx • PHP • MariaDB",
                               font=ctk.CTkFont(size=12),
                               text_color=M3_TEXT_SECONDARY)
        app_sub.pack(anchor="w")

        # Botón de configuración M3 (Filled Tonal Icon Button)
        btn_settings = ctk.CTkButton(top_bar, text="⚙", width=40, height=40, corner_radius=20,
                                     fg_color=M3_SECONDARY_CONTAINER, hover_color="#4F5B66",
                                     text_color=M3_ON_SECONDARY, font=ctk.CTkFont(size=17),
                                     command=self.open_settings_modal)
        btn_settings.pack(side="right")

        # 2. Material Navigation Bar (Píldoras M3)
        self.nav_tabs = ctk.CTkSegmentedButton(self, values=["Panel de Control", "Mis Proyectos"],
                                              command=self.on_tab_changed,
                                              fg_color=M3_SURFACE_CONTAINER,
                                              selected_color=M3_PRIMARY,
                                              selected_hover_color="#8AB4F8",
                                              text_color=M3_ON_PRIMARY,
                                              font=ctk.CTkFont(size=12, weight="bold"),
                                              corner_radius=20)
        self.nav_tabs.set("Panel de Control")
        self.nav_tabs.pack(fill="x", padx=24, pady=(6, 14))

        # 3. Contenedores de Vistas
        self.dash_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dash_frame.pack(fill="both", expand=True, padx=24)

        self.proj_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.build_dashboard_tab()
        self.build_projects_tab()

        # 4. Material Bottom Status Bar
        bottom_bar = ctk.CTkFrame(self, fg_color=M3_SURFACE_CONTAINER, height=36, corner_radius=0)
        bottom_bar.pack(fill="x", side="bottom")

        self.status_lbl = ctk.CTkLabel(bottom_bar, text="● Servicios en reposo",
                                       font=ctk.CTkFont(size=11), text_color=M3_TEXT_MUTED)
        self.status_lbl.pack(side="left", padx=18, pady=4)

        lic_lbl = ctk.CTkLabel(bottom_bar, text="Material Design 3 • Free",
                               font=ctk.CTkFont(size=10), text_color=M3_TEXT_MUTED)
        lic_lbl.pack(side="right", padx=18, pady=4)

    def build_dashboard_tab(self):
        # Card 1: Servicios (M3 Elevated Card)
        card_services = ctk.CTkFrame(self.dash_frame, fg_color=M3_SURFACE_CONTAINER,
                                     corner_radius=18, border_width=1, border_color=M3_OUTLINE)
        card_services.pack(fill="x", pady=6)

        c_head = ctk.CTkFrame(card_services, fg_color="transparent")
        c_head.pack(fill="x", padx=18, pady=(14, 8))

        c_title = ctk.CTkLabel(c_head, text="SERVICIOS DEL ENTORNO",
                               font=ctk.CTkFont(size=11, weight="bold"), text_color=M3_TEXT_SECONDARY)
        c_title.pack(side="left")

        # Selector PHP M3
        php_picker = ctk.CTkSegmentedButton(c_head, values=["8.4", "8.5"], variable=self.php_var,
                                            command=self.on_switch_php,
                                            width=110, height=28, corner_radius=14,
                                            fg_color=M3_SURFACE, selected_color=M3_PRIMARY,
                                            text_color=M3_ON_PRIMARY, font=ctk.CTkFont(size=11, weight="bold"))
        php_picker.pack(side="right")

        php_tag = ctk.CTkLabel(c_head, text="Versión PHP", font=ctk.CTkFont(size=11), text_color=M3_TEXT_MUTED)
        php_tag.pack(side="right", padx=(0, 8))

        # Lista de Servicios
        self.row_nginx = self.create_m3_service_row(card_services, "Nginx Web Server", "Puerto 80")
        self.row_php = self.create_m3_service_row(card_services, "PHP FastCGI", "Puerto 9000")
        self.row_mariadb = self.create_m3_service_row(card_services, "MariaDB Server", "Puerto 3307", is_last=True)

        # Botón Maestro M3 (Floating / Filled Primary Button)
        self.btn_master = ctk.CTkButton(self.dash_frame, text="INICIAR TODOS LOS SERVICIOS",
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        fg_color=M3_PRIMARY, hover_color="#C2E7FF",
                                        text_color=M3_ON_PRIMARY,
                                        height=48, corner_radius=24,
                                        command=self.toggle_services)
        self.btn_master.pack(fill="x", pady=12)

        # Card 2: Creación Rápida de Proyectos (M3 Tonal Card)
        card_quick = ctk.CTkFrame(self.dash_frame, fg_color=M3_SURFACE_CONTAINER,
                                  corner_radius=18, border_width=1, border_color=M3_OUTLINE)
        card_quick.pack(fill="x", pady=6)

        q_head = ctk.CTkFrame(card_quick, fg_color="transparent")
        q_head.pack(fill="x", padx=18, pady=(14, 8))

        q_title = ctk.CTkLabel(q_head, text="CREAR PROYECTO RÁPIDO",
                               font=ctk.CTkFont(size=11, weight="bold"), text_color=M3_TEXT_SECONDARY)
        q_title.pack(side="left")

        self.path_lbl = ctk.CTkLabel(q_head, text=self.state_data.get("projects_dir", "D:\\LabIA"),
                                     font=ctk.CTkFont(size=11, family="Consolas"), text_color=M3_TEXT_MUTED)
        self.path_lbl.pack(side="right")

        q_buttons = ctk.CTkFrame(card_quick, fg_color="transparent")
        q_buttons.pack(fill="x", padx=18, pady=(6, 16))

        # Botón Laravel (Material Red Accent)
        btn_lar = ctk.CTkButton(q_buttons, text="⚡ Nuevo Laravel", font=ctk.CTkFont(size=12, weight="bold"),
                                fg_color="#410002", hover_color="#8C1D18", text_color="#FFDAD6",
                                border_width=1, border_color="#93000A",
                                height=40, corner_radius=20,
                                command=lambda: self.prompt_project("laravel"))
        btn_lar.pack(side="left", fill="x", expand=True, padx=(0, 6))

        # Botón WordPress (Material Sky Accent)
        btn_wp = ctk.CTkButton(q_buttons, text="🚀 Nuevo WordPress", font=ctk.CTkFont(size=12, weight="bold"),
                               fg_color="#003355", hover_color="#004A77", text_color="#C2E7FF",
                               border_width=1, border_color="#00639B",
                               height=40, corner_radius=20,
                               command=lambda: self.prompt_project("wordpress"))
        btn_wp.pack(side="right", fill="x", expand=True, padx=(6, 0))

        # Card 3: Accesos Rápidos
        s_row = ctk.CTkFrame(self.dash_frame, fg_color="transparent")
        s_row.pack(fill="x", pady=8)

        btn_host = ctk.CTkButton(s_row, text="🌐 Localhost", fg_color=M3_SURFACE_CONTAINER,
                                 hover_color=M3_SURFACE_HIGH, text_color=M3_TEXT_PRIMARY,
                                 height=36, corner_radius=18, border_width=1, border_color=M3_OUTLINE,
                                 command=self.open_localhost)
        btn_host.pack(side="left", fill="x", expand=True, padx=(0, 4))

        btn_folder = ctk.CTkButton(s_row, text="📁 Carpeta", fg_color=M3_SURFACE_CONTAINER,
                                   hover_color=M3_SURFACE_HIGH, text_color=M3_TEXT_PRIMARY,
                                   height=36, corner_radius=18, border_width=1, border_color=M3_OUTLINE,
                                   command=self.open_projects_dir)
        btn_folder.pack(side="left", fill="x", expand=True, padx=4)

        btn_term = ctk.CTkButton(s_row, text="💻 Terminal", fg_color=M3_SURFACE_CONTAINER,
                                 hover_color=M3_SURFACE_HIGH, text_color=M3_TEXT_PRIMARY,
                                 height=36, corner_radius=18, border_width=1, border_color=M3_OUTLINE,
                                 command=self.open_terminal)
        btn_term.pack(side="right", fill="x", expand=True, padx=(4, 0))

    def create_m3_service_row(self, parent, name, port_text, is_last=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=5)

        dot = ctk.CTkLabel(row, text="●", font=ctk.CTkFont(size=14), text_color=M3_TEXT_MUTED)
        dot.pack(side="left")

        title = ctk.CTkLabel(row, text=f" {name}", font=ctk.CTkFont(size=12), text_color=M3_TEXT_PRIMARY)
        title.pack(side="left")

        port = ctk.CTkLabel(row, text=port_text, font=ctk.CTkFont(size=11, family="Consolas"), text_color=M3_TEXT_MUTED)
        port.pack(side="right")

        if not is_last:
            sep = ctk.CTkFrame(parent, fg_color=M3_SURFACE, height=1)
            sep.pack(fill="x", padx=18, pady=3)

        return {"dot": dot, "title": title, "port": port}

    def build_projects_tab(self):
        p_top = ctk.CTkFrame(self.proj_frame, fg_color="transparent")
        p_top.pack(fill="x", pady=(4, 8))

        lbl = ctk.CTkLabel(p_top, text="Proyectos Activos (Laravel & WordPress)",
                           font=ctk.CTkFont(size=12, weight="bold"), text_color=M3_TEXT_SECONDARY)
        lbl.pack(side="left")

        btn_reload = ctk.CTkButton(p_top, text="🔄 Recargar", width=90, height=28, corner_radius=14,
                                   fg_color=M3_SECONDARY_CONTAINER, hover_color="#4F5B66",
                                   text_color=M3_ON_SECONDARY, font=ctk.CTkFont(size=11),
                                   command=self.load_projects_list)
        btn_reload.pack(side="right")

        self.scroll_proj = ctk.CTkScrollableFrame(self.proj_frame, fg_color=M3_SURFACE_CONTAINER,
                                                 corner_radius=18, border_width=1, border_color=M3_OUTLINE,
                                                 height=430)
        self.scroll_proj.pack(fill="both", expand=True)

    def on_tab_changed(self, value):
        if value == "Panel de Control":
            self.proj_frame.pack_forget()
            self.dash_frame.pack(fill="both", expand=True, padx=24)
        else:
            self.dash_frame.pack_forget()
            self.proj_frame.pack(fill="both", expand=True, padx=24)
            self.load_projects_list()

    def load_projects_list(self):
        for widget in self.scroll_proj.winfo_children():
            widget.destroy()

        projects = core.list_projects()
        if not projects:
            empty_lbl = ctk.CTkLabel(self.scroll_proj, text="No hay proyectos WordPress ni Laravel creados.",
                                     font=ctk.CTkFont(size=12), text_color=M3_TEXT_MUTED)
            empty_lbl.pack(pady=50)
            return

        for p in projects:
            item = ctk.CTkFrame(self.scroll_proj, fg_color=M3_SURFACE, corner_radius=14, height=52)
            item.pack(fill="x", padx=8, pady=5)

            is_lar = p["type"] == "Laravel"
            t_bg = "#410002" if is_lar else "#003355"
            t_fg = "#FFDAD6" if is_lar else "#C2E7FF"
            t_badge = ctk.CTkLabel(item, text=f" {p['type']} ", font=ctk.CTkFont(size=9, weight="bold"),
                                   fg_color=t_bg, text_color=t_fg, corner_radius=8)
            t_badge.pack(side="left", padx=12, pady=10)

            info_frame = ctk.CTkFrame(item, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, pady=6)

            p_name = ctk.CTkLabel(info_frame, text=p["name"], font=ctk.CTkFont(size=12, weight="bold"),
                                  text_color=M3_TEXT_PRIMARY, anchor="w")
            p_name.pack(fill="x")

            p_host = ctk.CTkLabel(info_frame, text=p["vhost"], font=ctk.CTkFont(size=10, family="Consolas"),
                                  text_color=M3_TEXT_MUTED, anchor="w")
            p_host.pack(fill="x")

            # Botones con estilo Material Design (Tonal circular buttons)
            btn_web = ctk.CTkButton(item, text="🌐", width=32, height=32, corner_radius=16,
                                    fg_color=M3_SECONDARY_CONTAINER, hover_color="#4F5B66",
                                    command=lambda url=p["url"]: os.system(f"start {url}"))
            btn_web.pack(side="right", padx=(2, 10), pady=10)

            btn_dir = ctk.CTkButton(item, text="📁", width=32, height=32, corner_radius=16,
                                    fg_color=M3_SECONDARY_CONTAINER, hover_color="#4F5B66",
                                    command=lambda path=p["path"]: os.system(f'explorer "{path}"'))
            btn_dir.pack(side="right", padx=2, pady=10)

            btn_del = ctk.CTkButton(item, text="🗑", width=32, height=32, corner_radius=16,
                                    fg_color=M3_ERROR_CONTAINER, hover_color="#B3261E", text_color=M3_ERROR,
                                    command=lambda name=p["name"]: self.delete_project_modal(name))
            btn_del.pack(side="right", padx=2, pady=10)

    def delete_project_modal(self, name):
        if messagebox.askyesno("Eliminar Proyecto", f"¿Eliminar definitivamente '{name}'?\n\nEsta acción borrará los archivos en disco y la base de datos asociada."):
            self.status_lbl.configure(text=f"● Eliminando {name}...", text_color=M3_TERTIARY)
            self.update()
            success, msg = core.delete_project(name, delete_db=True)
            messagebox.showinfo("AetherStack", msg)
            self.load_projects_list()
            self.refresh_status()

    def refresh_status(self):
        status = core.get_status()

        # Nginx
        self.row_nginx["dot"].configure(text_color=M3_SUCCESS if status["nginx"]["running"] else M3_TEXT_MUTED)
        # PHP
        self.row_php["dot"].configure(text_color=M3_SUCCESS if status["php"]["running"] else M3_TEXT_MUTED)
        self.row_php["title"].configure(text=f" PHP FastCGI (v{status['php']['version']})")
        # MariaDB
        self.row_mariadb["dot"].configure(text_color=M3_SUCCESS if status["mariadb"]["running"] else M3_TEXT_MUTED)

        if status["all_running"]:
            self.btn_master.configure(text="DETENER TODOS LOS SERVICIOS",
                                      fg_color=M3_ERROR_CONTAINER, hover_color="#B3261E", text_color=M3_ERROR)
            self.status_lbl.configure(text="● Servicios activos y respondiendo", text_color=M3_SUCCESS)
        else:
            self.btn_master.configure(text="INICIAR TODOS LOS SERVICIOS",
                                      fg_color=M3_PRIMARY, hover_color="#C2E7FF", text_color=M3_ON_PRIMARY)
            self.status_lbl.configure(text="● Servicios en reposo", text_color=M3_TEXT_MUTED)

        self.path_lbl.configure(text=status["config"].get("projects_dir", "D:\\LabIA"))

    def auto_refresh_loop(self):
        self.refresh_status()
        self.after(3000, self.auto_refresh_loop)

    def toggle_services(self):
        status = core.get_status()
        self.btn_master.configure(text="Procesando...", state="disabled")
        self.update()

        def run():
            if status["all_running"]:
                core.stop_services()
            else:
                core.start_services(self.php_var.get())
            self.after(100, lambda: [self.btn_master.configure(state="normal"), self.refresh_status()])

        threading.Thread(target=run, daemon=True).start()

    def on_switch_php(self, ver):
        self.status_lbl.configure(text=f"● Cambiando a PHP {ver}...", text_color=M3_TERTIARY)
        self.update()

        def run():
            core.switch_php(ver)
            self.after(100, self.refresh_status)

        threading.Thread(target=run, daemon=True).start()

    def prompt_project(self, ptype):
        dialog = ctk.CTkInputDialog(text=f"Nombre del proyecto {ptype.capitalize()} (ej: mi-tienda):",
                                    title=f"Nuevo {ptype.capitalize()}")
        name = dialog.get_input()
        if not name or not name.strip():
            return
        name = name.strip()

        self.status_lbl.configure(text=f"● Creando {ptype} '{name}'... Por favor espera", text_color=M3_TERTIARY)
        self.update()

        def run():
            if ptype == "laravel":
                success, msg = core.create_project_laravel(name)
            else:
                success, msg = core.create_project_wordpress(name)
            
            if success:
                messagebox.showinfo("AetherStack", f"¡Proyecto {ptype.capitalize()} '{name}' creado con éxito!\nBase de datos asociada configurada.")
            else:
                messagebox.showerror("Error", msg)
            self.after(100, self.refresh_status)

        threading.Thread(target=run, daemon=True).start()

    def open_settings_modal(self):
        win = ctk.CTkToplevel(self)
        win.title("Configuración Global")
        win.geometry("450x330")
        win.resizable(False, False)
        win.configure(fg_color=M3_SURFACE)
        win.attributes('-topmost', True)

        ctk.CTkLabel(win, text="Configuración Global", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=M3_TEXT_PRIMARY).pack(anchor="w", padx=22, pady=(18, 4))
        ctk.CTkLabel(win, text="Personaliza la ubicación de tus proyectos y puertos locales.",
                     font=ctk.CTkFont(size=11), text_color=M3_TEXT_MUTED).pack(anchor="w", padx=22, pady=(0, 14))

        f_box = ctk.CTkFrame(win, fg_color="transparent")
        f_box.pack(fill="x", padx=22, pady=4)
        ctk.CTkLabel(f_box, text="Carpeta de Proyectos", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=M3_TEXT_PRIMARY).pack(anchor="w")

        dir_row = ctk.CTkFrame(f_box, fg_color="transparent")
        dir_row.pack(fill="x", pady=4)

        entry_dir = ctk.CTkEntry(dir_row, fg_color=M3_SURFACE_CONTAINER, text_color=M3_TEXT_PRIMARY,
                                 border_color=M3_OUTLINE, corner_radius=12)
        entry_dir.insert(0, self.state_data.get("projects_dir", "D:\\LabIA"))
        entry_dir.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def browse():
            f = filedialog.askdirectory(title="Seleccionar carpeta de proyectos")
            if f:
                entry_dir.delete(0, "end")
                entry_dir.insert(0, f)

        ctk.CTkButton(dir_row, text="Examinar", width=80, fg_color=M3_SECONDARY_CONTAINER,
                      hover_color="#4F5B66", text_color=M3_ON_SECONDARY, corner_radius=12,
                      command=browse).pack(side="right")

        # Puertos
        p_row = ctk.CTkFrame(win, fg_color="transparent")
        p_row.pack(fill="x", padx=22, pady=6)

        c1 = ctk.CTkFrame(p_row, fg_color="transparent")
        c1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(c1, text="Puerto Nginx (Web)", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=M3_TEXT_PRIMARY).pack(anchor="w")
        entry_nginx = ctk.CTkEntry(c1, fg_color=M3_SURFACE_CONTAINER, text_color=M3_TEXT_PRIMARY,
                                   border_color=M3_OUTLINE, corner_radius=12)
        entry_nginx.insert(0, str(self.state_data.get("nginx_port", 80)))
        entry_nginx.pack(fill="x", pady=4)

        c2 = ctk.CTkFrame(p_row, fg_color="transparent")
        c2.pack(side="right", fill="x", expand=True, padx=(6, 0))
        ctk.CTkLabel(c2, text="Puerto MariaDB", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=M3_TEXT_PRIMARY).pack(anchor="w")
        entry_db = ctk.CTkEntry(c2, fg_color=M3_SURFACE_CONTAINER, text_color=M3_TEXT_PRIMARY,
                                border_color=M3_OUTLINE, corner_radius=12)
        entry_db.insert(0, str(self.state_data.get("mariadb_port", 3307)))
        entry_db.pack(fill="x", pady=4)

        def save():
            new_conf = {
                "projects_dir": entry_dir.get().strip(),
                "nginx_port": int(entry_nginx.get()),
                "mariadb_port": int(entry_db.get())
            }
            core.update_global_config(new_conf)
            self.state_data = core.load_state()
            self.refresh_status()
            win.destroy()
            messagebox.showinfo("AetherStack", "Configuración guardada correctamente.")

        ctk.CTkButton(win, text="Guardar Cambios", fg_color=M3_PRIMARY, hover_color="#C2E7FF",
                      text_color=M3_ON_PRIMARY, height=40, corner_radius=20,
                      command=save).pack(fill="x", padx=22, pady=(16, 0))

    def open_localhost(self):
        port = self.state_data.get("nginx_port", 80)
        url = f"http://localhost:{port}" if port != 80 else "http://localhost"
        os.system(f"start {url}")

    def open_projects_dir(self):
        p_dir = self.state_data.get("projects_dir", "D:\\LabIA")
        os.system(f'explorer "{p_dir}"')

    def open_terminal(self):
        ver = self.php_var.get()
        p_dir = self.state_data.get("projects_dir", "D:\\LabIA")
        php_dir = os.path.join(core.BIN_DIR, "php", f"php-{ver}")
        mariadb_bin = os.path.join(core.BIN_DIR, "mariadb")
        composer_dir = os.path.join(core.BIN_DIR, "composer")
        env_cmd = f'set "PATH={php_dir};{composer_dir};{mariadb_bin};%PATH%" & cd /d "{p_dir}" & start cmd.exe /k "echo AetherStack Dev Shell (PHP {ver}) & echo."'
        os.system(env_cmd)

if __name__ == "__main__":
    app = AetherMaterialApp()
    app.mainloop()
