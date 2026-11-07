"""
AetherStack - Dribbble SaaS Dashboard Theme (Modo Oscuro Puro y Estable)
Diseño sólido, sin parpadeos ni conmutaciones involuntarias de tema.
"""
import os
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog
import core

# Fijar Modo Oscuro estricto a nivel de toolkit para evitar que Windows o callbacks re-rendericen en blanco
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Tokens exactos de la imagen adaptados a Modo Oscuro de alto contraste
BG_MAIN = "#0B0F19"             # Fondo principal oscuro profundo
BG_SIDEBAR = "#111827"          # Panel derecho (Sidebar de detalles)
BG_RAIL = "#1E293B"             # Rail lateral izquierdo
RAIL_ACTIVE = "#2563EB"         # Azul vibrante activo en rail
RAIL_ICON_MUTED = "#94A3B8"     # Iconos inactivos del rail
BG_CARD = "#161F30"             # Tarjetas principales (Surface elevada)
BG_CARD_HIGHLIGHT = "#1D4ED8"   # Tarjeta Nginx destacada
BG_ROW = "#111827"              # Filas de proyectos
BORDER = "#1E293B"              # Bordes sutiles
TEXT_DARK = "#F8FAFC"           # Títulos en blanco suave
TEXT_MUTED = "#94A3B8"          # Texto secundario
SEARCH_BG = "#161F30"           # Fondo de buscador
BTN_SEC_BG = "#1E293B"          # Botones secundarios
BTN_SEC_HOVER = "#334155"
BTN_SEC_TEXT = "#F8FAFC"
PROGRESS_BG = "#1E293B"

GREEN_SUCCESS = "#10B981"
RED_ERROR = "#EF4444"
ACCENT_BLUE = "#2563EB"

class AetherDribbbleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AetherStack - Local Dev Suite")
        self.geometry("1020x660")
        self.minsize(980, 620)
        self.configure(fg_color=BG_MAIN)

        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.state_data = core.load_state()
        self.php_var = ctk.StringVar(value=self.state_data.get("php_version", "8.4"))
        self.active_tab = "dashboard"

        self.build_dribbble_layout()
        self.refresh_status()
        self.auto_refresh_loop()

    def build_dribbble_layout(self):
        self.root_frame = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.root_frame.pack(fill="both", expand=True)

        # ----------------- 1. LEFT RAIL (Iconos de la app) -----------------
        self.left_rail = ctk.CTkFrame(self.root_frame, width=64, fg_color=BG_RAIL, corner_radius=0)
        self.left_rail.pack(side="left", fill="y")
        self.left_rail.pack_propagate(False)

        # Logo superior en el rail
        logo_btn = ctk.CTkButton(self.left_rail, text="⚡", width=44, height=44, corner_radius=14,
                                 fg_color=ACCENT_BLUE, text_color="#FFFFFF",
                                 font=ctk.CTkFont(size=20, weight="bold"),
                                 hover_color="#3B82F6", command=lambda: self.switch_view("dashboard"))
        logo_btn.pack(pady=(16, 20))

        # Iconos de navegación
        self.btn_rail_dash = ctk.CTkButton(self.left_rail, text="📊", width=44, height=44, corner_radius=12,
                                          fg_color=RAIL_ACTIVE, text_color="#FFFFFF", font=ctk.CTkFont(size=18),
                                          hover_color=RAIL_ACTIVE, command=lambda: self.switch_view("dashboard"))
        self.btn_rail_dash.pack(pady=4)

        self.btn_rail_proj = ctk.CTkButton(self.left_rail, text="📁", width=44, height=44, corner_radius=12,
                                          fg_color="transparent", text_color=RAIL_ICON_MUTED, font=ctk.CTkFont(size=18),
                                          hover_color="#334155", command=self.open_projects_dir)
        self.btn_rail_proj.pack(pady=4)

        # Configuración abajo en el rail
        btn_rail_cfg = ctk.CTkButton(self.left_rail, text="⚙", width=44, height=44, corner_radius=12,
                                     fg_color="transparent", text_color=RAIL_ICON_MUTED, font=ctk.CTkFont(size=18),
                                     hover_color="#334155", command=self.open_settings_modal)
        btn_rail_cfg.pack(side="bottom", pady=16)

        # ----------------- 2. RIGHT PANEL (Packeado primero a la derecha para no ser recortado) -----------------
        self.right_panel = ctk.CTkFrame(self.root_frame, width=265, fg_color=BG_SIDEBAR, corner_radius=18,
                                        border_width=1, border_color=BORDER)
        self.right_panel.pack(side="right", fill="y", padx=(0, 16), pady=16)
        self.right_panel.pack_propagate(False)

        self.build_right_sidebar()

        # ----------------- 3. MAIN CENTER CONTENT -----------------
        self.center_content = ctk.CTkFrame(self.root_frame, fg_color=BG_MAIN, corner_radius=0)
        self.center_content.pack(side="left", fill="both", expand=True, padx=(16, 16), pady=16)

        # Top Bar
        top_bar = ctk.CTkFrame(self.center_content, fg_color="transparent", height=44)
        top_bar.pack(fill="x", pady=(0, 16))

        path_box = ctk.CTkFrame(top_bar, fg_color=SEARCH_BG, corner_radius=12, height=40,
                                border_width=1, border_color=BORDER)
        path_box.pack(side="left", fill="x", expand=True)

        f_icon = ctk.CTkLabel(path_box, text="📁", font=ctk.CTkFont(size=14))
        f_icon.pack(side="left", padx=(14, 8))

        lbl_prefix = ctk.CTkLabel(path_box, text="Ruta de Proyectos:",
                                  font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED)
        lbl_prefix.pack(side="left", padx=(0, 6))

        proj_path = self.state_data.get("projects_dir", "D:\\LabIA")
        self.lbl_path_display = ctk.CTkLabel(path_box, text=proj_path,
                                             font=ctk.CTkFont(size=11, family="Consolas", weight="bold"),
                                             text_color=TEXT_DARK)
        self.lbl_path_display.pack(side="left", fill="x", expand=True, padx=4, anchor="w")

        btn_open_folder = ctk.CTkButton(path_box, text="Abrir carpeta", font=ctk.CTkFont(size=11, weight="bold"),
                                        fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                        width=95, height=26, corner_radius=8,
                                        command=self.open_projects_dir)
        btn_open_folder.pack(side="right", padx=(4, 8), pady=7)

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

    def build_dashboard_cards(self):
        lbl_storage = ctk.CTkLabel(self.view_container, text="Servicios en Ejecución",
                                   font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_DARK)
        lbl_storage.pack(anchor="w", pady=(0, 8))

        self.cards_row = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.cards_row.pack(fill="x", pady=(0, 14))

        # Tarjeta Nginx
        self.card_nginx = ctk.CTkFrame(self.cards_row, fg_color="#1E293B", corner_radius=16, height=100)
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
        self.card_php = ctk.CTkFrame(self.cards_row, fg_color=BG_CARD, corner_radius=16, height=100,
                                     border_width=1, border_color=BORDER)
        self.card_php.pack(side="left", fill="x", expand=True, padx=6)

        t2_top = ctk.CTkFrame(self.card_php, fg_color="transparent")
        t2_top.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(t2_top, text="🐘", font=ctk.CTkFont(size=18)).pack(side="left")

        php_versions = core.get_installed_php_versions() or ["8.1", "8.2", "8.3", "8.4", "8.5"]
        self.php_menu = ctk.CTkOptionMenu(t2_top, values=php_versions, variable=self.php_var,
                                          command=self.on_switch_php,
                                          width=80, height=24, corner_radius=8,
                                          fg_color=BG_MAIN, button_color=ACCENT_BLUE,
                                          button_hover_color="#1D4ED8", text_color=TEXT_DARK,
                                          dropdown_fg_color=BG_CARD, dropdown_text_color=TEXT_DARK,
                                          dropdown_hover_color=BTN_SEC_HOVER, font=ctk.CTkFont(size=11, weight="bold"))
        self.php_menu.pack(side="right")

        self.label_php_title = ctk.CTkLabel(self.card_php, text="PHP FastCGI (8.4)",
                                            font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_DARK)
        self.label_php_title.pack(anchor="w", padx=14)

        self.port_php_lbl = ctk.CTkLabel(self.card_php, text="Puerto 9000 • FastCGI", font=ctk.CTkFont(size=10),
                                        text_color=TEXT_MUTED)
        self.port_php_lbl.pack(anchor="w", padx=14, pady=(0, 10))

        # Tarjeta MariaDB
        self.card_db = ctk.CTkFrame(self.cards_row, fg_color=BG_CARD, corner_radius=16, height=100,
                                   border_width=1, border_color=BORDER)
        self.card_db.pack(side="right", fill="x", expand=True, padx=(6, 0))

        t3_top = ctk.CTkFrame(self.card_db, fg_color="transparent")
        t3_top.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(t3_top, text="🐬", font=ctk.CTkFont(size=18)).pack(side="left")
        self.badge_db = ctk.CTkLabel(t3_top, text="OFFLINE", font=ctk.CTkFont(size=9, weight="bold"),
                                     fg_color=BG_MAIN, text_color=TEXT_MUTED, corner_radius=6)
        self.badge_db.pack(side="right")

        ctk.CTkLabel(self.card_db, text="MariaDB Server", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=14)
        self.port_db_lbl = ctk.CTkLabel(self.card_db, text="Puerto 3307 • MySQL", font=ctk.CTkFont(size=10),
                                       text_color=TEXT_MUTED)
        self.port_db_lbl.pack(anchor="w", padx=14, pady=(0, 10))

    def build_quick_actions(self):
        lbl_quick = ctk.CTkLabel(self.view_container, text="Acceso Rápido & Creación",
                                 font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_DARK)
        lbl_quick.pack(anchor="w", pady=(4, 8))

        q_row = ctk.CTkFrame(self.view_container, fg_color="transparent")
        q_row.pack(fill="x", pady=(0, 14))

        btn_lar = self.create_round_action_btn(q_row, "⚡", "Laravel", "#271E22", "#EF4444",
                                              lambda: self.prompt_project("laravel"))
        btn_lar.pack(side="left", padx=(0, 10))

        btn_wp = self.create_round_action_btn(q_row, "🚀", "WordPress", "#162838", "#38BDF8",
                                             lambda: self.prompt_project("wordpress"))
        btn_wp.pack(side="left", padx=10)

        btn_local = self.create_round_action_btn(q_row, "🌐", "Localhost", "#1E2238", "#818CF8",
                                                self.open_localhost)
        btn_local.pack(side="left", padx=10)

        btn_folder = self.create_round_action_btn(q_row, "📁", "Carpeta", "#2E2619", "#FBBF24",
                                                 self.open_projects_dir)
        btn_folder.pack(side="left", padx=10)

        btn_cli = self.create_round_action_btn(q_row, "💻", "Terminal", "#162B24", "#34D399",
                                              self.open_terminal)
        btn_cli.pack(side="left", padx=10)

    def create_round_action_btn(self, parent, icon, text, bg_color, fg_color, command):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        
        btn = ctk.CTkButton(box, text=icon, width=48, height=48, corner_radius=16,
                            fg_color=bg_color, hover_color="#334155",
                            text_color=fg_color, font=ctk.CTkFont(size=18), command=command,
                            border_width=1, border_color=BORDER)
        btn.pack()

        lbl = ctk.CTkLabel(box, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED)
        lbl.pack(pady=(4, 0))

        return box

    def build_projects_table(self):
        t_head = ctk.CTkFrame(self.view_container, fg_color="transparent")
        t_head.pack(fill="x", pady=(4, 6))

        lbl_files = ctk.CTkLabel(t_head, text="Mis Proyectos (WordPress & Laravel)",
                                 font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_DARK)
        lbl_files.pack(side="left")

        btn_reload = ctk.CTkButton(t_head, text="Recargar lista", font=ctk.CTkFont(size=11, weight="bold"),
                                   fg_color="transparent", text_color=ACCENT_BLUE,
                                   hover_color="#1E293B", width=90, height=24, command=self.load_projects_list)
        btn_reload.pack(side="right")

        self.scroll_table = ctk.CTkScrollableFrame(self.view_container, fg_color=BG_CARD, corner_radius=16,
                                                  border_width=1, border_color=BORDER, height=220)
        self.scroll_table.pack(fill="both", expand=True)

        self.load_projects_list()

    def load_projects_list(self):
        for w in self.scroll_table.winfo_children():
            w.destroy()

        projects = core.list_projects()
        self._last_project_names = [p["name"] for p in projects]

        if not projects:
            empty = ctk.CTkLabel(self.scroll_table, text="No hay proyectos WordPress ni Laravel en la carpeta.",
                                 font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
            empty.pack(pady=40)
            return

        for p in projects:
            row = ctk.CTkFrame(self.scroll_table, fg_color=BG_ROW, corner_radius=12, height=44)
            row.pack(fill="x", padx=6, pady=3)

            is_lar = p["type"] == "Laravel"
            icon_char = "⚡" if is_lar else "🚀"
            b_color = "#EF4444" if is_lar else "#38BDF8"

            f_icon = ctk.CTkLabel(row, text=icon_char, font=ctk.CTkFont(size=14), width=32)
            f_icon.pack(side="left", padx=(10, 4))

            p_name = ctk.CTkLabel(row, text=p["name"], font=ctk.CTkFont(size=12, weight="bold"),
                                  text_color=TEXT_DARK, width=140, anchor="w")
            p_name.pack(side="left", padx=4)

            badge = ctk.CTkLabel(row, text=f" {p['type']} ", font=ctk.CTkFont(size=9, weight="bold"),
                                 fg_color=BG_CARD, text_color=b_color, corner_radius=6,
                                 border_width=1, border_color=BORDER)
            badge.pack(side="left", padx=8)

            v_host = ctk.CTkLabel(row, text=p["vhost"], font=ctk.CTkFont(size=10, family="Consolas"),
                                  text_color=TEXT_MUTED, anchor="w")
            v_host.pack(side="left", fill="x", expand=True, padx=8)

            btn_web = ctk.CTkButton(row, text="🌐", width=28, height=28, corner_radius=8,
                                    fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                    border_width=1, border_color=BORDER,
                                    command=lambda url=p["url"]: os.system(f"start {url}"))
            btn_web.pack(side="right", padx=(2, 8), pady=6)

            btn_dir = ctk.CTkButton(row, text="📁", width=28, height=28, corner_radius=8,
                                    fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                    border_width=1, border_color=BORDER,
                                    command=lambda path=p["path"]: os.system(f'explorer "{path}"'))
            btn_dir.pack(side="right", padx=2, pady=6)

            btn_del = ctk.CTkButton(row, text="🗑", width=28, height=28, corner_radius=8,
                                    fg_color=BTN_SEC_BG, hover_color="#DC2626", text_color="#EF4444",
                                    border_width=1, border_color=BORDER,
                                    command=lambda name=p["name"]: self.delete_project_modal(name))
            btn_del.pack(side="right", padx=2, pady=6)

    def get_system_ram_load(self):
        try:
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ('dwLength', ctypes.c_ulong),
                    ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong),
                    ('ullAvailPhys', ctypes.c_ulonglong),
                    ('ullTotalPageFile', ctypes.c_ulonglong),
                    ('ullAvailPageFile', ctypes.c_ulonglong),
                    ('ullTotalVirtual', ctypes.c_ulonglong),
                    ('ullAvailVirtual', ctypes.c_ulonglong),
                    ('sullAvailExtendedVirtual', ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return stat.dwMemoryLoad
        except Exception:
            return 30

    def build_right_sidebar(self):
        pad_box = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        pad_box.pack(fill="both", expand=True, padx=14, pady=16)

        # 1. Cabecera con título e indicador
        head_box = ctk.CTkFrame(pad_box, fg_color="transparent")
        head_box.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(head_box, text="Detalles del Stack", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left")

        self.badge_stack_status = ctk.CTkLabel(head_box, text="STANDBY", font=ctk.CTkFont(size=9, weight="bold"),
                                              fg_color="#1E293B", text_color="#94A3B8", corner_radius=6, padx=6, pady=2)
        self.badge_stack_status.pack(side="right")

        # 2. Tarjeta: Rendimiento del Sistema (RAM)
        card_ram = ctk.CTkFrame(pad_box, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER)
        card_ram.pack(fill="x", pady=(0, 10))

        c_ram_pad = ctk.CTkFrame(card_ram, fg_color="transparent")
        c_ram_pad.pack(fill="x", padx=12, pady=10)

        ram_head = ctk.CTkFrame(c_ram_pad, fg_color="transparent")
        ram_head.pack(fill="x")
        ctk.CTkLabel(ram_head, text="⚡ Memoria del Sistema", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left")
        self.lbl_ram_pct = ctk.CTkLabel(ram_head, text="35%", font=ctk.CTkFont(size=11, weight="bold"),
                                       text_color=ACCENT_BLUE)
        self.lbl_ram_pct.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(c_ram_pad, height=6, corner_radius=3, fg_color=PROGRESS_BG, progress_color=ACCENT_BLUE)
        self.progress_bar.pack(fill="x", pady=(6, 4))
        self.progress_bar.set(0.35)

        self.ram_lbl = ctk.CTkLabel(c_ram_pad, text="Stack ligero: < 95 MB activos", font=ctk.CTkFont(size=10),
                                    text_color=TEXT_MUTED)
        self.ram_lbl.pack(anchor="w")

        # 3. Tarjeta: Base de Datos MariaDB
        card_db = ctk.CTkFrame(pad_box, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER)
        card_db.pack(fill="x", pady=(0, 10))

        c_db_pad = ctk.CTkFrame(card_db, fg_color="transparent")
        c_db_pad.pack(fill="x", padx=12, pady=10)

        db_head = ctk.CTkFrame(c_db_pad, fg_color="transparent")
        db_head.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(db_head, text="🐬 MariaDB Server", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left")
        self.lbl_side_db_port = ctk.CTkLabel(db_head, text=f"Puerto {self.state_data.get('mariadb_port', 3307)}",
                                             font=ctk.CTkFont(size=9, weight="bold"),
                                             fg_color="#064E3B", text_color="#34D399", corner_radius=6, padx=5, pady=1)
        self.lbl_side_db_port.pack(side="right")

        def make_param_row(parent, label, val):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=10, family="Consolas", weight="bold"), text_color=TEXT_DARK).pack(side="right")

        make_param_row(c_db_pad, "Host:", "127.0.0.1")
        make_param_row(c_db_pad, "Usuario:", "root")
        make_param_row(c_db_pad, "Clave:", "(sin contraseña)")

        btn_copy_db = ctk.CTkButton(c_db_pad, text="📋 Copiar Conexión", font=ctk.CTkFont(size=10, weight="bold"),
                                    fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                    height=24, corner_radius=6, border_width=1, border_color=BORDER,
                                    command=self.copy_db_connection)
        btn_copy_db.pack(fill="x", pady=(6, 0))

        # 4. Tarjeta: Carpeta Activa de Proyectos
        card_dir = ctk.CTkFrame(pad_box, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER)
        card_dir.pack(fill="x", pady=(0, 10))

        c_dir_pad = ctk.CTkFrame(card_dir, fg_color="transparent")
        c_dir_pad.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(c_dir_pad, text="📁 Carpeta de Proyectos", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(0, 4))

        p_chip = ctk.CTkFrame(c_dir_pad, fg_color=BG_ROW, corner_radius=8, border_width=1, border_color=BORDER)
        p_chip.pack(fill="x", pady=(0, 8))
        self.lbl_active_folder = ctk.CTkLabel(p_chip, text=self.state_data.get("projects_dir", "D:\\LabIA"),
                                              font=ctk.CTkFont(size=10, family="Consolas", weight="bold"),
                                              text_color=ACCENT_BLUE, padx=8, pady=4, wraplength=210, justify="left")
        self.lbl_active_folder.pack(fill="x")

        dir_btns = ctk.CTkFrame(c_dir_pad, fg_color="transparent")
        dir_btns.pack(fill="x")

        btn_open_exp = ctk.CTkButton(dir_btns, text="Explorar", font=ctk.CTkFont(size=10, weight="bold"),
                                     fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                     height=26, corner_radius=8, border_width=1, border_color=BORDER,
                                     command=self.open_projects_dir)
        btn_open_exp.pack(side="left", fill="x", expand=True, padx=(0, 3))

        btn_change = ctk.CTkButton(dir_btns, text="Cambiar", font=ctk.CTkFont(size=10, weight="bold"),
                                   fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                   height=26, corner_radius=8, border_width=1, border_color=BORDER,
                                   command=self.open_settings_modal)
        btn_change.pack(side="right", fill="x", expand=True, padx=(3, 0))

        # 5. Botón inferior de Logs
        btn_logs = ctk.CTkButton(pad_box, text="📜 Ver Logs del Stack", font=ctk.CTkFont(size=11, weight="bold"),
                                 fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                 border_width=1, border_color=BORDER, height=32, corner_radius=10,
                                 command=self.open_logs_dir)
        btn_logs.pack(fill="x", side="bottom", pady=4)

    def switch_view(self, view_name):
        self.active_tab = view_name
        if view_name == "dashboard":
            self.btn_rail_dash.configure(fg_color=RAIL_ACTIVE, text_color="#FFFFFF")
            self.btn_rail_proj.configure(fg_color="transparent", text_color=RAIL_ICON_MUTED)
        else:
            self.btn_rail_dash.configure(fg_color="transparent", text_color=RAIL_ICON_MUTED)
            self.btn_rail_proj.configure(fg_color=RAIL_ACTIVE, text_color="#FFFFFF")
            self.load_projects_list()

    def refresh_status(self):
        status = core.get_status()

        if status["nginx"]["running"]:
            self.card_nginx.configure(fg_color=BG_CARD_HIGHLIGHT)
            self.badge_nginx.configure(text="ONLINE", fg_color="#10B981", text_color="#FFFFFF")
        else:
            self.card_nginx.configure(fg_color="#1E293B")
            self.badge_nginx.configure(text="OFFLINE", fg_color="#0F172A", text_color="#94A3B8")

        php_v = status["php"]["version"]
        self.label_php_title.configure(text=f"PHP FastCGI ({php_v})")
        if self.php_var.get() != php_v:
            self.php_var.set(php_v)

        if status["mariadb"]["running"]:
            self.badge_db.configure(text="ONLINE", fg_color="#064E3B", text_color="#34D399")
        else:
            self.badge_db.configure(text="OFFLINE", fg_color=BG_MAIN, text_color=TEXT_MUTED)

        if status["all_running"]:
            self.btn_master.configure(text="DETENER STACK", fg_color=RED_ERROR, hover_color="#DC2626")
            if hasattr(self, "badge_stack_status"):
                self.badge_stack_status.configure(text="ONLINE", fg_color="#064E3B", text_color="#34D399")
            if hasattr(self, "ram_lbl"):
                self.ram_lbl.configure(text="Stack ligero: < 95 MB activos")
        else:
            self.btn_master.configure(text="INICIAR STACK", fg_color=GREEN_SUCCESS, hover_color="#059669")
            if hasattr(self, "badge_stack_status"):
                self.badge_stack_status.configure(text="STANDBY", fg_color="#1E293B", text_color="#94A3B8")
            if hasattr(self, "ram_lbl"):
                self.ram_lbl.configure(text="Servicios detenidos")

        ram_load = self.get_system_ram_load()
        if hasattr(self, "progress_bar"):
            self.progress_bar.set(ram_load / 100.0)
        if hasattr(self, "lbl_ram_pct"):
            self.lbl_ram_pct.configure(text=f"{ram_load}%")

        cur_dir = status["config"].get("projects_dir", "D:\\LabIA")
        self.lbl_active_folder.configure(text=cur_dir)
        if hasattr(self, "lbl_path_display"):
            self.lbl_path_display.configure(text=cur_dir)

        db_port = status["config"].get("mariadb_port", 3307)
        if hasattr(self, "lbl_side_db_port"):
            self.lbl_side_db_port.configure(text=f"Puerto {db_port}")

    def auto_refresh_loop(self):
        self.refresh_status()
        # Detección y recarga automática si los proyectos en disco cambiaron
        try:
            current_projects = [p["name"] for p in core.list_projects()]
            if getattr(self, "_last_project_names", None) is not None:
                if self._last_project_names != current_projects:
                    self._last_project_names = current_projects
                    self.load_projects_list()
            else:
                self._last_project_names = current_projects
        except Exception:
            pass
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

    def center_modal(self, modal, width, height):
        modal.update_idletasks()
        self.update_idletasks()
        p_x = self.winfo_rootx()
        p_y = self.winfo_rooty()
        p_w = self.winfo_width()
        p_h = self.winfo_height()
        x = max(0, p_x + (p_w - width) // 2)
        y = max(0, p_y + (p_h - height) // 2)
        modal.geometry(f"{width}x{height}+{x}+{y}")

    def show_dark_alert(self, title, message, alert_type="info", callback=None):
        win = ctk.CTkToplevel(self)
        win.title("AetherStack")
        win.resizable(False, False)
        win.configure(fg_color=BG_CARD)
        win.attributes("-topmost", True)
        win.transient(self)

        self.center_modal(win, 440, 210)

        pad = ctk.CTkFrame(win, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=22, pady=18)

        head = ctk.CTkFrame(pad, fg_color="transparent")
        head.pack(fill="x", pady=(0, 8))

        icon_char = "✓" if alert_type == "success" else ("✕" if alert_type == "error" else ("⚠" if alert_type == "warning" else "ℹ"))
        icon_bg = "#064E3B" if alert_type == "success" else ("#451A1A" if alert_type == "error" else ("#453210" if alert_type == "warning" else "#1E293B"))
        icon_fg = "#10B981" if alert_type == "success" else ("#EF4444" if alert_type == "error" else ("#F59E0B" if alert_type == "warning" else "#38BDF8"))

        badge = ctk.CTkLabel(head, text=icon_char, width=32, height=32, corner_radius=16,
                             fg_color=icon_bg, text_color=icon_fg, font=ctk.CTkFont(size=16, weight="bold"))
        badge.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(head, text=title, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left", anchor="w")

        ctk.CTkLabel(pad, text=message, font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                     wraplength=380, justify="left").pack(anchor="w", pady=(0, 16))

        def close():
            win.destroy()
            if callback:
                callback()

        btn = ctk.CTkButton(pad, text="Entendido", height=32, corner_radius=10,
                            fg_color=ACCENT_BLUE, hover_color="#1D4ED8", text_color="#FFFFFF",
                            font=ctk.CTkFont(size=11, weight="bold"), command=close)
        btn.pack(fill="x")

        win.bind("<Return>", lambda e: close())
        win.bind("<Escape>", lambda e: close())
        win.grab_set()
        win.after(80, btn.focus)
        return win

    def show_dark_confirm(self, title, message, confirm_text="Eliminar", on_confirm=None):
        win = ctk.CTkToplevel(self)
        win.title("AetherStack")
        win.resizable(False, False)
        win.configure(fg_color=BG_CARD)
        win.attributes("-topmost", True)
        win.transient(self)

        self.center_modal(win, 440, 210)

        pad = ctk.CTkFrame(win, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=22, pady=18)

        head = ctk.CTkFrame(pad, fg_color="transparent")
        head.pack(fill="x", pady=(0, 8))

        badge = ctk.CTkLabel(head, text="🗑", width=32, height=32, corner_radius=16,
                             fg_color="#451A1A", text_color="#EF4444", font=ctk.CTkFont(size=16))
        badge.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(head, text=title, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left", anchor="w")

        ctk.CTkLabel(pad, text=message, font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                     wraplength=380, justify="left").pack(anchor="w", pady=(0, 16))

        btn_row = ctk.CTkFrame(pad, fg_color="transparent")
        btn_row.pack(fill="x")

        def close():
            win.destroy()

        def confirm():
            win.destroy()
            if on_confirm:
                on_confirm()

        btn_cancel = ctk.CTkButton(btn_row, text="Cancelar", height=32, corner_radius=10,
                                   fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                   border_width=1, border_color=BORDER, command=close)
        btn_cancel.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_del = ctk.CTkButton(btn_row, text=confirm_text, height=32, corner_radius=10,
                                fg_color="#DC2626", hover_color="#B91C1C", text_color="#FFFFFF",
                                font=ctk.CTkFont(size=11, weight="bold"), command=confirm)
        btn_del.pack(side="right", fill="x", expand=True, padx=(6, 0))

        win.bind("<Escape>", lambda e: close())
        win.grab_set()
        win.after(80, btn_cancel.focus)
        return win

    def prompt_project(self, ptype):
        status = core.get_status()
        if not status["all_running"]:
            self.show_dark_alert(
                "Servicios Detenidos",
                "No puedes crear proyectos mientras los servicios estén apagados.\n\nInicia el stack pulsando 'INICIAR STACK' para activar Nginx, PHP y MariaDB.",
                alert_type="warning"
            )
            return

        win = ctk.CTkToplevel(self)
        is_lar = ptype.lower() == "laravel"
        title_txt = "Crear Proyecto Laravel" if is_lar else "Crear Sitio WordPress"
        icon_char = "⚡" if is_lar else "🚀"

        win.title(title_txt)
        win.resizable(False, False)
        win.configure(fg_color=BG_CARD)
        win.attributes('-topmost', True)
        win.transient(self)
        self.center_modal(win, 420, 220)

        pad = ctk.CTkFrame(win, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=22, pady=18)

        # Cabecera con icono y título
        head = ctk.CTkFrame(pad, fg_color="transparent")
        head.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(head, text=icon_char, font=ctk.CTkFont(size=18)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(head, text=title_txt, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkLabel(pad, text="Ingresa el nombre del proyecto (ej: mi-web):",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        entry_name = ctk.CTkEntry(pad, placeholder_text="ej: mi-web, blog, api-rest",
                                  fg_color=BG_ROW, border_color=BORDER, text_color=TEXT_DARK,
                                  height=34, corner_radius=10, font=ctk.CTkFont(size=12))
        entry_name.pack(fill="x", pady=(0, 16))
        win.after(80, entry_name.focus)

        def on_confirm():
            name = entry_name.get().strip()
            if not name:
                return

            status = core.get_status()
            if not status["all_running"]:
                win.destroy()
                self.show_dark_alert(
                    "Servicios Detenidos",
                    "No se pudo crear el proyecto: los servicios del stack no están activos.",
                    alert_type="warning"
                )
                return

            win.destroy()

            def run():
                if ptype == "laravel":
                    success, msg = core.create_project_laravel(name)
                else:
                    success, msg = core.create_project_wordpress(name)

                self.after(0, self.load_projects_list)
                self.after(0, self.refresh_status)
                if success:
                    self.after(50, lambda: self.show_dark_alert(
                        "¡Proyecto Creado!",
                        f"¡Proyecto {ptype.capitalize()} '{name}' creado con éxito!\nBase de datos en puerto 3307.",
                        alert_type="success"
                    ))
                else:
                    self.after(50, lambda: self.show_dark_alert("Error al Crear", msg, alert_type="error"))

            threading.Thread(target=run, daemon=True).start()

        def on_cancel():
            win.destroy()

        entry_name.bind("<Return>", lambda e: on_confirm())
        win.bind("<Escape>", lambda e: on_cancel())

        btn_row = ctk.CTkFrame(pad, fg_color="transparent")
        btn_row.pack(fill="x")

        btn_cancel = ctk.CTkButton(btn_row, text="Cancelar", height=32, corner_radius=10,
                                   fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                   border_width=1, border_color=BORDER, command=on_cancel)
        btn_cancel.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_ok = ctk.CTkButton(btn_row, text="Crear Proyecto", height=32, corner_radius=10,
                               fg_color=ACCENT_BLUE, hover_color="#1D4ED8", text_color="#FFFFFF",
                               font=ctk.CTkFont(size=11, weight="bold"), command=on_confirm)
        btn_ok.pack(side="right", fill="x", expand=True, padx=(6, 0))

        win.grab_set()

    def delete_project_modal(self, name):
        def do_delete():
            success, msg = core.delete_project(name, delete_db=True)
            self.after(0, self.load_projects_list)
            self.after(0, self.refresh_status)
            if not success:
                self.after(50, lambda: self.show_dark_alert("Error al Eliminar", msg, alert_type="error"))

        self.show_dark_confirm(
            "Eliminar Proyecto",
            f"¿Estás seguro de eliminar '{name}'?\n\nEsta acción borrará la carpeta en disco y la base de datos asociada de forma irreversible.",
            confirm_text="Eliminar Proyecto",
            on_confirm=do_delete
        )

    def open_settings_modal(self):
        win = ctk.CTkToplevel(self)
        win.title("Configuración")
        win.resizable(False, False)
        win.configure(fg_color=BG_CARD)
        win.attributes('-topmost', True)
        win.transient(self)
        self.center_modal(win, 450, 330)

        ctk.CTkLabel(win, text="Configuración Global", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=22, pady=(18, 4))
        ctk.CTkLabel(win, text="Personaliza la ubicación de tus proyectos y puertos locales.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w", padx=22, pady=(0, 14))

        f_box = ctk.CTkFrame(win, fg_color="transparent")
        f_box.pack(fill="x", padx=22, pady=4)
        ctk.CTkLabel(f_box, text="Carpeta de Proyectos", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w")

        dir_row = ctk.CTkFrame(f_box, fg_color="transparent")
        dir_row.pack(fill="x", pady=4)

        entry_dir = ctk.CTkEntry(dir_row, fg_color=BG_ROW, text_color=TEXT_DARK,
                                 border_color=BORDER, corner_radius=10)
        entry_dir.insert(0, self.state_data.get("projects_dir", "D:\\LabIA"))
        entry_dir.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def browse():
            f = filedialog.askdirectory(title="Seleccionar carpeta de proyectos")
            if f:
                entry_dir.delete(0, "end")
                entry_dir.insert(0, f)

        ctk.CTkButton(dir_row, text="Examinar", width=80, fg_color=BTN_SEC_BG,
                      hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT, corner_radius=10,
                      border_width=1, border_color=BORDER, command=browse).pack(side="right")

        p_row = ctk.CTkFrame(win, fg_color="transparent")
        p_row.pack(fill="x", padx=22, pady=6)

        c1 = ctk.CTkFrame(p_row, fg_color="transparent")
        c1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(c1, text="Puerto Nginx", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_DARK).pack(anchor="w")
        entry_nginx = ctk.CTkEntry(c1, fg_color=BG_ROW, text_color=TEXT_DARK, border_color=BORDER, corner_radius=10)
        entry_nginx.insert(0, str(self.state_data.get("nginx_port", 80)))
        entry_nginx.pack(fill="x", pady=4)

        c2 = ctk.CTkFrame(p_row, fg_color="transparent")
        c2.pack(side="right", fill="x", expand=True, padx=(6, 0))
        ctk.CTkLabel(c2, text="Puerto MariaDB", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_DARK).pack(anchor="w")
        entry_db = ctk.CTkEntry(c2, fg_color=BG_ROW, text_color=TEXT_DARK, border_color=BORDER, corner_radius=10)
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
            self.show_dark_alert("Configuración", "Configuración guardada correctamente.", alert_type="success")

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

    def copy_db_connection(self):
        port = self.state_data.get("mariadb_port", 3307)
        conn_str = f"mysql -h 127.0.0.1 -P {port} -u root"
        self.clipboard_clear()
        self.clipboard_append(conn_str)
        self.update()
        self.show_dark_alert("MariaDB Server", f"Comando de conexión copiado al portapapeles:\n\n{conn_str}", alert_type="info")

    def open_logs_dir(self):
        logs_dir = os.path.join(core.BASE_DIR, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        os.system(f'explorer "{logs_dir}"')

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
