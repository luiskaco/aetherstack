"""
AetherStack - Dribbble SaaS Dashboard Theme con Soporte Modo Oscuro / Claro
Conmutador dinámico (🌙 / ☀️) en el Rail lateral y paleta profunda de alto contraste.
"""
import os
import sys
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
import core

# Paletas de Color para Modo Claro y Modo Oscuro
THEMES = {
    "dark": {
        "bg_main": "#0B0F19",             # Fondo principal oscuro profundo
        "bg_sidebar": "#111827",          # Panel derecho
        "bg_rail": "#1E293B",             # Rail lateral izquierdo
        "rail_btn_active": "#2563EB",     # Azul vibrante en el rail
        "rail_icon_color": "#94A3B8",
        "bg_card": "#161F30",             # Tarjetas blancas pasan a slate oscuro
        "bg_card_highlight": "#1D4ED8",   # Tarjeta Nginx destacada
        "bg_row": "#111827",              # Fila de proyectos
        "border": "#1E293B",              # Bordes sutiles
        "text_dark": "#F8FAFC",           # Títulos en blanco suave
        "text_muted": "#94A3B8",          # Texto secundario
        "search_bg": "#161F30",
        "btn_sec_bg": "#1E293B",
        "btn_sec_hover": "#334155",
        "btn_sec_text": "#F8FAFC",
        "progress_bg": "#1E293B"
    },
    "light": {
        "bg_main": "#F0F4F9",
        "bg_sidebar": "#FFFFFF",
        "bg_rail": "#1E88E5",
        "rail_btn_active": "#1565C0",
        "rail_icon_color": "#BBDEFB",
        "bg_card": "#FFFFFF",
        "bg_card_highlight": "#1E88E5",
        "bg_row": "#F8FAFC",
        "border": "#E2E8F0",
        "text_dark": "#1E293B",
        "text_muted": "#64748B",
        "search_bg": "#FFFFFF",
        "btn_sec_bg": "#FFFFFF",
        "btn_sec_hover": "#F1F5F9",
        "btn_sec_text": "#1E293B",
        "progress_bg": "#E2E8F0"
    }
}

GREEN_SUCCESS = "#10B981"
RED_ERROR = "#EF4444"
ACCENT_BLUE = "#2563EB"

class AetherDribbbleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AetherStack - Local Dev Suite")
        self.geometry("980x640")
        self.minsize(940, 600)

        # Cargar estado y tema inicial (Modo Oscuro por defecto)
        self.state_data = core.load_state()
        self.current_theme = self.state_data.get("theme", "dark")
        ctk.set_appearance_mode(self.current_theme)

        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.php_var = ctk.StringVar(value=self.state_data.get("php_version", "8.4"))
        self.active_tab = "dashboard"

        self.t = THEMES[self.current_theme]
        self.configure(fg_color=self.t["bg_main"])

        self.build_dribbble_layout()
        self.refresh_status()
        self.auto_refresh_loop()

    def build_dribbble_layout(self):
        t = self.t

        self.root_frame = ctk.CTkFrame(self, fg_color=t["bg_main"], corner_radius=0)
        self.root_frame.pack(fill="both", expand=True)

        # ----------------- 1. LEFT RAIL (Iconos de la app) -----------------
        self.left_rail = ctk.CTkFrame(self.root_frame, width=64, fg_color=t["bg_rail"], corner_radius=0)
        self.left_rail.pack(side="left", fill="y")
        self.left_rail.pack_propagate(False)

        # Logo superior en el rail
        logo_btn = ctk.CTkButton(self.left_rail, text="⚡", width=44, height=44, corner_radius=14,
                                 fg_color="#FFFFFF" if self.current_theme == "light" else "#2563EB",
                                 text_color="#1E88E5" if self.current_theme == "light" else "#FFFFFF",
                                 font=ctk.CTkFont(size=20, weight="bold"),
                                 hover_color="#3B82F6", command=lambda: self.switch_view("dashboard"))
        logo_btn.pack(pady=(16, 20))

        # Iconos de navegación
        self.btn_rail_dash = ctk.CTkButton(self.left_rail, text="📊", width=44, height=44, corner_radius=12,
                                          fg_color=t["rail_btn_active"], text_color="#FFFFFF", font=ctk.CTkFont(size=18),
                                          hover_color=t["rail_btn_active"], command=lambda: self.switch_view("dashboard"))
        self.btn_rail_dash.pack(pady=4)

        self.btn_rail_proj = ctk.CTkButton(self.left_rail, text="📁", width=44, height=44, corner_radius=12,
                                          fg_color="transparent", text_color=t["rail_icon_color"], font=ctk.CTkFont(size=18),
                                          hover_color="#334155" if self.current_theme == "dark" else "#1976D2",
                                          command=lambda: self.switch_view("projects"))
        self.btn_rail_proj.pack(pady=4)

        # Botón Toggle Modo Oscuro / Claro en la parte inferior del rail
        theme_icon = "☀️" if self.current_theme == "dark" else "🌙"
        self.btn_theme = ctk.CTkButton(self.left_rail, text=theme_icon, width=44, height=44, corner_radius=12,
                                       fg_color="transparent", text_color="#F8FAFC", font=ctk.CTkFont(size=18),
                                       hover_color="#334155" if self.current_theme == "dark" else "#1976D2",
                                       command=self.toggle_theme)
        self.btn_theme.pack(side="bottom", pady=(4, 16))

        # Configuración
        btn_rail_cfg = ctk.CTkButton(self.left_rail, text="⚙", width=44, height=44, corner_radius=12,
                                     fg_color="transparent", text_color=t["rail_icon_color"], font=ctk.CTkFont(size=18),
                                     hover_color="#334155" if self.current_theme == "dark" else "#1976D2",
                                     command=self.open_settings_modal)
        btn_rail_cfg.pack(side="bottom", pady=4)

        # ----------------- 2. MAIN CENTER CONTENT -----------------
        self.center_content = ctk.CTkFrame(self.root_frame, fg_color=t["bg_main"], corner_radius=0)
        self.center_content.pack(side="left", fill="both", expand=True, padx=20, pady=16)

        # Top Bar
        top_bar = ctk.CTkFrame(self.center_content, fg_color="transparent", height=44)
        top_bar.pack(fill="x", pady=(0, 16))

        search_box = ctk.CTkFrame(top_bar, fg_color=t["search_bg"], corner_radius=12, height=40,
                                 border_width=1, border_color=t["border"])
        search_box.pack(side="left", fill="x", expand=True)

        s_icon = ctk.CTkLabel(search_box, text="🔍", font=ctk.CTkFont(size=13), text_color=t["text_muted"])
        s_icon.pack(side="left", padx=(12, 6))

        self.search_entry = ctk.CTkEntry(search_box, placeholder_text="Buscar proyectos en la carpeta...",
                                         fg_color="transparent", border_width=0, text_color=t["text_dark"],
                                         font=ctk.CTkFont(size=12))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Botón Maestro Iniciar/Detener
        self.btn_master = ctk.CTkButton(top_bar, text="INICIAR STACK", font=ctk.CTkFont(size=12, weight="bold"),
                                        fg_color=GREEN_SUCCESS, hover_color="#059669", text_color="#FFFFFF",
                                        height=40, corner_radius=12, command=self.toggle_services)
        self.btn_master.pack(side="right", padx=(12, 0))

        self.view_container = ctk.CTkFrame(self.center_content, fg_color="transparent")
        self.view_container.pack(fill="both", expand=True)

        self.build_dashboard_cards()
        self.build_quick_actions()
        self.build_projects_table()

        # ----------------- 3. RIGHT PANEL -----------------
        self.right_panel = ctk.CTkFrame(self.root_frame, width=240, fg_color=t["bg_sidebar"], corner_radius=18,
                                        border_width=1, border_color=t["border"])
        self.right_panel.pack(side="right", fill="y", padx=(0, 16), pady=16)
        self.right_panel.pack_propagate(False)

        self.build_right_sidebar()

    def build_dashboard_cards(self):
        t = self.t
        lbl_storage = ctk.CTkLabel(self.view_container, text="Servicios en Ejecución",
                                   font=ctk.CTkFont(size=14, weight="bold"), text_color=t["text_dark"])
        lbl_storage.pack(anchor="w", pady=(0, 8))

        self.cards_row = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.cards_row.pack(fill="x", pady=(0, 14))

        # Tarjeta Nginx
        self.card_nginx = ctk.CTkFrame(self.cards_row, fg_color=t["bg_card_highlight"], corner_radius=16, height=100)
        self.card_nginx.pack(side="left", fill="x", expand=True, padx=(0, 6))

        t1_top = ctk.CTkFrame(self.card_nginx, fg_color="transparent")
        t1_top.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(t1_top, text="🌐", font=ctk.CTkFont(size=18), text_color="#FFFFFF").pack(side="left")
        self.badge_nginx = ctk.CTkLabel(t1_top, text="OFFLINE", font=ctk.CTkFont(size=9, weight="bold"),
                                       fg_color="#0F172A", text_color="#94A3B8", corner_radius=6)
        self.badge_nginx.pack(side="right")

        ctk.CTkLabel(self.card_nginx, text="Nginx Web Server", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", padx=14)
        self.port_nginx_lbl = ctk.CTkLabel(self.card_nginx, text="Puerto 80 • HTTP", font=ctk.CTkFont(size=10),
                                          text_color="#CBD5E1")
        self.port_nginx_lbl.pack(anchor="w", padx=14, pady=(0, 10))

        # Tarjeta PHP FastCGI
        self.card_php = ctk.CTkFrame(self.cards_row, fg_color=t["bg_card"], corner_radius=16, height=100,
                                     border_width=1, border_color=t["border"])
        self.card_php.pack(side="left", fill="x", expand=True, padx=6)

        t2_top = ctk.CTkFrame(self.card_php, fg_color="transparent")
        t2_top.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(t2_top, text="🐘", font=ctk.CTkFont(size=18)).pack(side="left")

        self.php_segmented = ctk.CTkSegmentedButton(t2_top, values=["8.4", "8.5"], variable=self.php_var,
                                                   command=self.on_switch_php,
                                                   width=75, height=22, corner_radius=6,
                                                   fg_color=t["bg_main"], selected_color=ACCENT_BLUE,
                                                   text_color=t["text_dark"], selected_hover_color=ACCENT_BLUE)
        self.php_segmented.pack(side="right")

        self.label_php_title = ctk.CTkLabel(self.card_php, text="PHP FastCGI (8.4)",
                                            font=ctk.CTkFont(size=12, weight="bold"), text_color=t["text_dark"])
        self.label_php_title.pack(anchor="w", padx=14)

        self.port_php_lbl = ctk.CTkLabel(self.card_php, text="Puerto 9000 • FastCGI", font=ctk.CTkFont(size=10),
                                        text_color=t["text_muted"])
        self.port_php_lbl.pack(anchor="w", padx=14, pady=(0, 10))

        # Tarjeta MariaDB
        self.card_db = ctk.CTkFrame(self.cards_row, fg_color=t["bg_card"], corner_radius=16, height=100,
                                   border_width=1, border_color=t["border"])
        self.card_db.pack(side="right", fill="x", expand=True, padx=(6, 0))

        t3_top = ctk.CTkFrame(self.card_db, fg_color="transparent")
        t3_top.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(t3_top, text="🐬", font=ctk.CTkFont(size=18)).pack(side="left")
        self.badge_db = ctk.CTkLabel(t3_top, text="OFFLINE", font=ctk.CTkFont(size=9, weight="bold"),
                                     fg_color=t["bg_main"], text_color=t["text_muted"], corner_radius=6)
        self.badge_db.pack(side="right")

        ctk.CTkLabel(self.card_db, text="MariaDB Server", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=t["text_dark"]).pack(anchor="w", padx=14)
        self.port_db_lbl = ctk.CTkLabel(self.card_db, text="Puerto 3307 • MySQL", font=ctk.CTkFont(size=10),
                                       text_color=t["text_muted"])
        self.port_db_lbl.pack(anchor="w", padx=14, pady=(0, 10))

    def build_quick_actions(self):
        t = self.t
        lbl_quick = ctk.CTkLabel(self.view_container, text="Acceso Rápido & Creación",
                                 font=ctk.CTkFont(size=14, weight="bold"), text_color=t["text_dark"])
        lbl_quick.pack(anchor="w", pady=(4, 8))

        q_row = ctk.CTkFrame(self.view_container, fg_color="transparent")
        q_row.pack(fill="x", pady=(0, 14))

        bg_round = "#271E22" if self.current_theme == "dark" else "#FEE2E2"
        btn_lar = self.create_round_action_btn(q_row, "⚡", "Laravel", bg_round, "#EF4444",
                                              lambda: self.prompt_project("laravel"))
        btn_lar.pack(side="left", padx=(0, 10))

        bg_round_wp = "#162838" if self.current_theme == "dark" else "#E0F2FE"
        btn_wp = self.create_round_action_btn(q_row, "🚀", "WordPress", bg_round_wp, "#38BDF8",
                                             lambda: self.prompt_project("wordpress"))
        btn_wp.pack(side="left", padx=10)

        bg_round_loc = "#1E2238" if self.current_theme == "dark" else "#E0E7FF"
        btn_local = self.create_round_action_btn(q_row, "🌐", "Localhost", bg_round_loc, "#818CF8",
                                                self.open_localhost)
        btn_local.pack(side="left", padx=10)

        bg_round_fol = "#2E2619" if self.current_theme == "dark" else "#FEF3C7"
        btn_folder = self.create_round_action_btn(q_row, "📁", "Carpeta", bg_round_fol, "#FBBF24",
                                                 self.open_projects_dir)
        btn_folder.pack(side="left", padx=10)

        bg_round_cli = "#162B24" if self.current_theme == "dark" else "#DCFCE7"
        btn_cli = self.create_round_action_btn(q_row, "💻", "Terminal", bg_round_cli, "#34D399",
                                              self.open_terminal)
        btn_cli.pack(side="left", padx=10)

    def create_round_action_btn(self, parent, icon, text, bg_color, fg_color, command):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        
        btn = ctk.CTkButton(box, text=icon, width=48, height=48, corner_radius=16,
                            fg_color=bg_color, hover_color="#334155" if self.current_theme == "dark" else "#FFFFFF",
                            text_color=fg_color, font=ctk.CTkFont(size=18), command=command,
                            border_width=1, border_color=self.t["border"])
        btn.pack()

        lbl = ctk.CTkLabel(box, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color=self.t["text_muted"])
        lbl.pack(pady=(4, 0))

        return box

    def build_projects_table(self):
        t = self.t
        t_head = ctk.CTkFrame(self.view_container, fg_color="transparent")
        t_head.pack(fill="x", pady=(4, 6))

        lbl_files = ctk.CTkLabel(t_head, text="Mis Proyectos (WordPress & Laravel)",
                                 font=ctk.CTkFont(size=14, weight="bold"), text_color=t["text_dark"])
        lbl_files.pack(side="left")

        btn_reload = ctk.CTkButton(t_head, text="Recargar lista", font=ctk.CTkFont(size=11, weight="bold"),
                                   fg_color="transparent", text_color=ACCENT_BLUE,
                                   hover_color="#1E293B" if self.current_theme == "dark" else "#E3F2FD",
                                   width=90, height=24, command=self.load_projects_list)
        btn_reload.pack(side="right")

        self.scroll_table = ctk.CTkScrollableFrame(self.view_container, fg_color=t["bg_card"], corner_radius=16,
                                                  border_width=1, border_color=t["border"], height=220)
        self.scroll_table.pack(fill="both", expand=True)

        self.load_projects_list()

    def load_projects_list(self):
        t = self.t
        for w in self.scroll_table.winfo_children():
            w.destroy()

        projects = core.list_projects()
        if not projects:
            empty = ctk.CTkLabel(self.scroll_table, text="No hay proyectos WordPress ni Laravel en la carpeta.",
                                 font=ctk.CTkFont(size=12), text_color=t["text_muted"])
            empty.pack(pady=40)
            return

        for p in projects:
            row = ctk.CTkFrame(self.scroll_table, fg_color=t["bg_row"], corner_radius=12, height=44)
            row.pack(fill="x", padx=6, pady=3)

            is_lar = p["type"] == "Laravel"
            icon_char = "⚡" if is_lar else "🚀"
            b_color = "#EF4444" if is_lar else "#38BDF8"

            f_icon = ctk.CTkLabel(row, text=icon_char, font=ctk.CTkFont(size=14), width=32)
            f_icon.pack(side="left", padx=(10, 4))

            p_name = ctk.CTkLabel(row, text=p["name"], font=ctk.CTkFont(size=12, weight="bold"),
                                  text_color=t["text_dark"], width=140, anchor="w")
            p_name.pack(side="left", padx=4)

            badge = ctk.CTkLabel(row, text=f" {p['type']} ", font=ctk.CTkFont(size=9, weight="bold"),
                                 fg_color=t["bg_card"], text_color=b_color, corner_radius=6,
                                 border_width=1, border_color=t["border"])
            badge.pack(side="left", padx=8)

            v_host = ctk.CTkLabel(row, text=p["vhost"], font=ctk.CTkFont(size=10, family="Consolas"),
                                  text_color=t["text_muted"], anchor="w")
            v_host.pack(side="left", fill="x", expand=True, padx=8)

            btn_web = ctk.CTkButton(row, text="🌐", width=28, height=28, corner_radius=8,
                                    fg_color=t["btn_sec_bg"], hover_color=t["btn_sec_hover"], text_color=t["btn_sec_text"],
                                    border_width=1, border_color=t["border"],
                                    command=lambda url=p["url"]: os.system(f"start {url}"))
            btn_web.pack(side="right", padx=(2, 8), pady=6)

            btn_dir = ctk.CTkButton(row, text="📁", width=28, height=28, corner_radius=8,
                                    fg_color=t["btn_sec_bg"], hover_color=t["btn_sec_hover"], text_color=t["btn_sec_text"],
                                    border_width=1, border_color=t["border"],
                                    command=lambda path=p["path"]: os.system(f'explorer "{path}"'))
            btn_dir.pack(side="right", padx=2, pady=6)

            btn_del = ctk.CTkButton(row, text="🗑", width=28, height=28, corner_radius=8,
                                    fg_color=t["btn_sec_bg"], hover_color="#DC2626", text_color="#EF4444",
                                    border_width=1, border_color=t["border"],
                                    command=lambda name=p["name"]: self.delete_project_modal(name))
            btn_del.pack(side="right", padx=2, pady=6)

    def build_right_sidebar(self):
        t = self.t
        pad_box = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        pad_box.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(pad_box, text="Detalles del Stack", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=t["text_dark"]).pack(anchor="w", pady=(0, 12))

        status_box = ctk.CTkFrame(pad_box, fg_color=t["bg_row"], corner_radius=14, border_width=1, border_color=t["border"])
        status_box.pack(fill="x", pady=(0, 14))

        sb_pad = ctk.CTkFrame(status_box, fg_color="transparent")
        sb_pad.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(sb_pad, text="Rendimiento del Sistema", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=t["text_dark"]).pack(anchor="w")

        self.ram_lbl = ctk.CTkLabel(sb_pad, text="Consumo: < 95 MB RAM", font=ctk.CTkFont(size=10),
                                    text_color=t["text_muted"])
        self.ram_lbl.pack(anchor="w")

        self.progress_bar = ctk.CTkProgressBar(sb_pad, height=6, corner_radius=3, fg_color=t["progress_bg"], progress_color=ACCENT_BLUE)
        self.progress_bar.pack(fill="x", pady=(6, 2))
        self.progress_bar.set(0.15)

        ctk.CTkLabel(pad_box, text="CARPETA ACTIVA", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))

        self.lbl_active_folder = ctk.CTkLabel(pad_box, text=self.state_data.get("projects_dir", "D:\\LabIA"),
                                              font=ctk.CTkFont(size=10, family="Consolas"), text_color=t["text_dark"],
                                              wraplength=200, justify="left")
        self.lbl_active_folder.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(pad_box, text="BASE DE DATOS", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=t["text_muted"]).pack(anchor="w", pady=(8, 2))

        db_txt = "Host: 127.0.0.1\nPuerto: 3307\nUser: root\nPass: (ninguna)"
        ctk.CTkLabel(pad_box, text=db_txt, font=ctk.CTkFont(size=10, family="Consolas"), text_color=t["text_dark"],
                     justify="left").pack(anchor="w")

        btn_change_dir = ctk.CTkButton(pad_box, text="Cambiar Carpeta", font=ctk.CTkFont(size=11, weight="bold"),
                                       fg_color=t["btn_sec_bg"], hover_color=t["btn_sec_hover"], text_color=t["btn_sec_text"],
                                       border_width=1, border_color=t["border"], height=32, corner_radius=10,
                                       command=self.open_settings_modal)
        btn_change_dir.pack(fill="x", side="bottom", pady=4)

    def toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.current_theme = new_theme
        self.state_data["theme"] = new_theme
        core.update_global_config({"theme": new_theme})
        
        # Reconstruir la UI con la nueva paleta
        ctk.set_appearance_mode(new_theme)
        self.t = THEMES[new_theme]
        self.configure(fg_color=self.t["bg_main"])
        
        for w in self.winfo_children():
            w.destroy()
            
        self.build_dribbble_layout()
        self.refresh_status()

    def switch_view(self, view_name):
        self.active_tab = view_name
        t = self.t
        if view_name == "dashboard":
            self.btn_rail_dash.configure(fg_color=t["rail_btn_active"], text_color="#FFFFFF")
            self.btn_rail_proj.configure(fg_color="transparent", text_color=t["rail_icon_color"])
        else:
            self.btn_rail_dash.configure(fg_color="transparent", text_color=t["rail_icon_color"])
            self.btn_rail_proj.configure(fg_color=t["rail_btn_active"], text_color="#FFFFFF")
            self.load_projects_list()

    def refresh_status(self):
        status = core.get_status()

        if status["nginx"]["running"]:
            self.card_nginx.configure(fg_color=self.t["bg_card_highlight"])
            self.badge_nginx.configure(text="ONLINE", fg_color="#10B981", text_color="#FFFFFF")
        else:
            self.card_nginx.configure(fg_color="#334155" if self.current_theme == "dark" else "#64748B")
            self.badge_nginx.configure(text="OFFLINE", fg_color="#1E293B", text_color="#94A3B8")

        self.label_php_title.configure(text=f"PHP FastCGI ({status['php']['version']})")

        if status["mariadb"]["running"]:
            self.badge_db.configure(text="ONLINE", fg_color="#064E3B" if self.current_theme == "dark" else "#DCFCE7",
                                   text_color="#34D399" if self.current_theme == "dark" else "#16A34A")
        else:
            self.badge_db.configure(text="OFFLINE", fg_color=self.t["bg_main"], text_color=self.t["text_muted"])

        if status["all_running"]:
            self.btn_master.configure(text="DETENER STACK", fg_color=RED_ERROR, hover_color="#DC2626")
            self.progress_bar.set(0.65)
        else:
            self.btn_master.configure(text="INICIAR STACK", fg_color=GREEN_SUCCESS, hover_color="#059669")
            self.progress_bar.set(0.10)

        self.lbl_active_folder.configure(text=status["config"].get("projects_dir", "D:\\LabIA"))

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
        def run():
            core.switch_php(ver)
            self.after(100, self.refresh_status)

        threading.Thread(target=run, daemon=True).start()

    def prompt_project(self, ptype):
        dialog = ctk.CTkInputDialog(text=f"Nombre para el proyecto {ptype.capitalize()} (ej: mi-web):",
                                    title=f"Crear {ptype.capitalize()}")
        name = dialog.get_input()
        if not name or not name.strip():
            return
        name = name.strip()

        def run():
            if ptype == "laravel":
                success, msg = core.create_project_laravel(name)
            else:
                success, msg = core.create_project_wordpress(name)
            
            if success:
                messagebox.showinfo("AetherStack", f"¡Proyecto {ptype.capitalize()} '{name}' creado con éxito!\nBase de datos en puerto 3307.")
            else:
                messagebox.showerror("Error", msg)
            self.after(100, lambda: [self.refresh_status(), self.load_projects_list()])

        threading.Thread(target=run, daemon=True).start()

    def delete_project_modal(self, name):
        if messagebox.askyesno("Eliminar Proyecto", f"¿Eliminar '{name}'?\n\nEsta acción borrará la carpeta en disco y la base de datos asociada."):
            success, msg = core.delete_project(name, delete_db=True)
            messagebox.showinfo("AetherStack", msg)
            self.load_projects_list()
            self.refresh_status()

    def open_settings_modal(self):
        t = self.t
        win = ctk.CTkToplevel(self)
        win.title("Configuración")
        win.geometry("450x330")
        win.resizable(False, False)
        win.configure(fg_color=t["bg_card"])
        win.attributes('-topmost', True)

        ctk.CTkLabel(win, text="Configuración Global", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=t["text_dark"]).pack(anchor="w", padx=22, pady=(18, 4))
        ctk.CTkLabel(win, text="Personaliza la ubicación de tus proyectos y puertos locales.",
                     font=ctk.CTkFont(size=11), text_color=t["text_muted"]).pack(anchor="w", padx=22, pady=(0, 14))

        f_box = ctk.CTkFrame(win, fg_color="transparent")
        f_box.pack(fill="x", padx=22, pady=4)
        ctk.CTkLabel(f_box, text="Carpeta de Proyectos", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=t["text_dark"]).pack(anchor="w")

        dir_row = ctk.CTkFrame(f_box, fg_color="transparent")
        dir_row.pack(fill="x", pady=4)

        entry_dir = ctk.CTkEntry(dir_row, fg_color=t["bg_row"], text_color=t["text_dark"],
                                 border_color=t["border"], corner_radius=10)
        entry_dir.insert(0, self.state_data.get("projects_dir", "D:\\LabIA"))
        entry_dir.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def browse():
            f = filedialog.askdirectory(title="Seleccionar carpeta de proyectos")
            if f:
                entry_dir.delete(0, "end")
                entry_dir.insert(0, f)

        ctk.CTkButton(dir_row, text="Examinar", width=80, fg_color=t["btn_sec_bg"],
                      hover_color=t["btn_sec_hover"], text_color=t["btn_sec_text"], corner_radius=10,
                      border_width=1, border_color=t["border"], command=browse).pack(side="right")

        p_row = ctk.CTkFrame(win, fg_color="transparent")
        p_row.pack(fill="x", padx=22, pady=6)

        c1 = ctk.CTkFrame(p_row, fg_color="transparent")
        c1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(c1, text="Puerto Nginx", font=ctk.CTkFont(size=11, weight="bold"), text_color=t["text_dark"]).pack(anchor="w")
        entry_nginx = ctk.CTkEntry(c1, fg_color=t["bg_row"], text_color=t["text_dark"], border_color=t["border"], corner_radius=10)
        entry_nginx.insert(0, str(self.state_data.get("nginx_port", 80)))
        entry_nginx.pack(fill="x", pady=4)

        c2 = ctk.CTkFrame(p_row, fg_color="transparent")
        c2.pack(side="right", fill="x", expand=True, padx=(6, 0))
        ctk.CTkLabel(c2, text="Puerto MariaDB", font=ctk.CTkFont(size=11, weight="bold"), text_color=t["text_dark"]).pack(anchor="w")
        entry_db = ctk.CTkEntry(c2, fg_color=t["bg_row"], text_color=t["text_dark"], border_color=t["border"], corner_radius=10)
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

        ctk.CTkButton(win, text="Guardar Cambios", fg_color=ACCENT_BLUE, hover_color="#1D4ED8",
                      text_color="#FFFFFF", height=38, corner_radius=12,
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
    app = AetherDribbbleApp()
    app.mainloop()
