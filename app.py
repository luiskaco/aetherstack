"""
AetherStack - Dribbble SaaS Dashboard Theme (Modo Oscuro Puro y Estable)
Diseño sólido, sin parpadeos ni conmutaciones involuntarias de tema.
"""
import os
import sys
import subprocess
import threading
import webbrowser
import customtkinter as ctk
from tkinter import filedialog
import core
import updater
import i18n
from i18n import t

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
ACCENT_TEXT = "#60A5FA"          # Azul claro para texto sobre fondos oscuros (contraste 7:1)
TEXT_STATUS_OFF = "#CBD5E1"     # Texto de badges apagados (contraste 12:1)

class AetherDribbbleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"AetherStack v{core.VERSION} - Local Dev Suite")
        self.geometry("1020x660")
        self.minsize(980, 620)
        self.configure(fg_color=BG_MAIN)

        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(self.icon_path):
            self.iconbitmap(self.icon_path)

        self.state_data = core.load_state()
        i18n.set_lang(self.state_data.get("language", "es"))
        self.php_var = ctk.StringVar(value=self.state_data.get("php_version", "8.4"))
        self.active_tab = "dashboard"

        self.build_dribbble_layout()
        self.refresh_status()
        self.auto_refresh_loop()
        self.start_update_check()

    def start_update_check(self):
        """Busca una versión nueva en segundo plano para no bloquear la interfaz."""
        def worker():
            info = core.check_for_update()
            if info:
                try:
                    self.after(0, lambda: self.show_update_banner(info))
                except Exception:
                    pass
        threading.Thread(target=worker, daemon=True).start()

    def show_update_banner(self, info):
        self.update_info = info
        banner = ctk.CTkFrame(self.center_content, fg_color="#1E3A8A", corner_radius=12,
                              border_width=1, border_color=ACCENT_BLUE)
        self.lbl_update = ctk.CTkLabel(banner, text=t("update_available", version=info["version"]),
                                       font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFFFFF")
        self.lbl_update.pack(side="left", padx=(14, 8), pady=8)
        self.one_click_update = bool(info.get("code_url") and info.get("sha_url"))
        self.btn_update = ctk.CTkButton(banner, text=self._update_btn_text(), width=130, height=28, corner_radius=8,
                                        font=ctk.CTkFont(size=11, weight="bold"),
                                        fg_color=ACCENT_BLUE, hover_color="#3B82F6", text_color="#FFFFFF",
                                        command=self.confirm_update if self.one_click_update
                                        else (lambda: webbrowser.open(info["url"])))
        self.btn_update.pack(side="right", padx=(8, 10), pady=8)
        if self.one_click_update:
            ctk.CTkButton(banner, text=t("update_download"), width=100, height=28, corner_radius=8,
                          font=ctk.CTkFont(size=11), fg_color="transparent", hover_color="#1E40AF",
                          text_color="#CBD5E1", command=lambda: webbrowser.open(info["url"])
                          ).pack(side="right", pady=8)
        banner.pack(fill="x", pady=(0, 12), before=self.view_container)

    def _update_btn_text(self):
        return t("update_now") if getattr(self, "one_click_update", False) else t("update_download")

    def confirm_update(self):
        info = self.update_info
        self.show_dark_confirm(t("update_confirm_title"),
                               t("update_confirm_msg", version=info["version"]),
                               confirm_text=t("update_now"), on_confirm=self.run_update, danger=False)

    def run_update(self):
        """Descarga y aplica la actualización en segundo plano; reinicia la app al terminar."""
        info = self.update_info
        self.btn_update.configure(state="disabled", text=t("update_downloading"))

        def worker():
            try:
                updater.download_and_apply(info["code_url"], info["sha_url"])
                self.after(0, self._update_done)
            except Exception as exc:
                msg = str(exc) if isinstance(exc, updater.UpdateError) else f"{exc}"
                self.after(0, lambda: self._update_failed(msg))
        threading.Thread(target=worker, daemon=True).start()

    def _update_done(self):
        def restart():
            updater.restart_app()
            self.destroy()
        self.show_dark_alert(t("update_done_title"), t("update_done_msg", version=self.update_info["version"]),
                             "success", callback=restart)

    def _update_failed(self, msg):
        self.btn_update.configure(state="normal", text=self._update_btn_text())
        self.show_dark_alert(t("update_error_title"), t("update_error_msg", detail=msg), "error")

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

        self.lbl_prefix = ctk.CTkLabel(path_box, text=t("projects_path_label"),
                                       font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_prefix.pack(side="left", padx=(0, 6))

        proj_path = core.get_projects_root()
        self.lbl_path_display = ctk.CTkLabel(path_box, text=proj_path,
                                             font=ctk.CTkFont(size=11, family="Consolas", weight="bold"),
                                             text_color=TEXT_DARK)
        self.lbl_path_display.pack(side="left", fill="x", expand=True, padx=4, anchor="w")

        self.btn_open_folder = ctk.CTkButton(path_box, text=t("open_folder"), font=ctk.CTkFont(size=11, weight="bold"),
                                             fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                             width=95, height=26, corner_radius=8,
                                             command=self.open_projects_dir)
        self.btn_open_folder.pack(side="right", padx=(4, 8), pady=7)

        # Botón Maestro Iniciar/Detener
        self.btn_master = ctk.CTkButton(top_bar, text=t("btn_start_stack"), font=ctk.CTkFont(size=12, weight="bold"),
                                        fg_color=GREEN_SUCCESS, hover_color="#059669", text_color="#FFFFFF",
                                        height=40, corner_radius=12, command=self.toggle_services)
        self.btn_master.pack(side="right", padx=(10, 0))

        # Botón Toggle Idioma EN/ES (Barra Superior)
        cur_lang = i18n.get_lang()
        btn_lang_txt = "🌐 EN" if cur_lang == "es" else "🌐 ES"
        self.btn_lang = ctk.CTkButton(top_bar, text=btn_lang_txt, font=ctk.CTkFont(size=11, weight="bold"),
                                      fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=TEXT_DARK,
                                      border_width=1, border_color=BORDER, width=64, height=40, corner_radius=12,
                                      command=self.toggle_language)
        self.btn_lang.pack(side="right", padx=(10, 0))

        self.view_container = ctk.CTkFrame(self.center_content, fg_color="transparent")
        self.view_container.pack(fill="both", expand=True)

        self.build_dashboard_cards()
        self.build_quick_actions()
        self.build_projects_table()

    def build_dashboard_cards(self):
        self.lbl_storage = ctk.CTkLabel(self.view_container, text=t("running_services_title"),
                                        font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_DARK)
        self.lbl_storage.pack(anchor="w", pady=(0, 8))

        self.cards_row = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.cards_row.pack(fill="x", pady=(0, 14))

        # Tarjeta Nginx
        self.card_nginx = ctk.CTkFrame(self.cards_row, fg_color="#1E293B", corner_radius=16, height=100)
        self.card_nginx.pack(side="left", fill="x", expand=True, padx=(0, 6))

        t1_top = ctk.CTkFrame(self.card_nginx, fg_color="transparent")
        t1_top.pack(fill="x", padx=14, pady=(12, 4))
        ctk.CTkLabel(t1_top, text="🌐", font=ctk.CTkFont(size=18), text_color="#FFFFFF").pack(side="left")
        self.badge_nginx = ctk.CTkLabel(t1_top, text="OFFLINE", font=ctk.CTkFont(size=9, weight="bold"),
                                       fg_color="#0F172A", text_color=TEXT_STATUS_OFF, corner_radius=6)
        self.badge_nginx.pack(side="right")

        ctk.CTkLabel(self.card_nginx, text="Nginx Web Server", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", padx=14)
        self.port_nginx_lbl = ctk.CTkLabel(self.card_nginx, text=t("nginx_card_sub"), font=ctk.CTkFont(size=10),
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

        self.port_php_lbl = ctk.CTkLabel(self.card_php, text=t("php_card_sub"), font=ctk.CTkFont(size=10),
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
                                     fg_color=BG_MAIN, text_color=TEXT_STATUS_OFF, corner_radius=6)
        self.badge_db.pack(side="right")

        ctk.CTkLabel(self.card_db, text="MariaDB Server", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=14)
        db_p = self.state_data.get("mariadb_port", 3307)
        self.port_db_lbl = ctk.CTkLabel(self.card_db, text=t("mariadb_card_sub", port=db_p), font=ctk.CTkFont(size=10),
                                       text_color=TEXT_MUTED)
        self.port_db_lbl.pack(anchor="w", padx=14, pady=(0, 10))

    def build_quick_actions(self):
        self.lbl_quick = ctk.CTkLabel(self.view_container, text=t("quick_actions_title"),
                                      font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_DARK)
        self.lbl_quick.pack(anchor="w", pady=(4, 8))

        q_row = ctk.CTkFrame(self.view_container, fg_color="transparent")
        q_row.pack(fill="x", pady=(0, 14))

        box_lar, self.lbl_act_lar = self.create_round_action_btn(q_row, "⚡", t("action_laravel"), "#271E22", "#EF4444",
                                                                 lambda: self.prompt_project("laravel"))
        box_lar.pack(side="left", padx=(0, 10))

        box_wp, self.lbl_act_wp = self.create_round_action_btn(q_row, "🚀", t("action_wordpress"), "#162838", "#38BDF8",
                                                              lambda: self.prompt_project("wordpress"))
        box_wp.pack(side="left", padx=10)

        box_local, self.lbl_act_local = self.create_round_action_btn(q_row, "🌐", t("action_localhost"), "#1E2238", "#818CF8",
                                                                    self.open_localhost)
        box_local.pack(side="left", padx=10)

        box_folder, self.lbl_act_folder = self.create_round_action_btn(q_row, "📁", t("action_folder"), "#2E2619", "#FBBF24",
                                                                      self.open_projects_dir)
        box_folder.pack(side="left", padx=10)

        box_cli, self.lbl_act_terminal = self.create_round_action_btn(q_row, "💻", t("action_terminal"), "#162B24", "#34D399",
                                                                    self.open_terminal)
        box_cli.pack(side="left", padx=10)

        box_db, self.lbl_act_db = self.create_round_action_btn(q_row, "🗄", t("action_database"), "#261C3B", "#C084FC",
                                                               lambda: self.open_db_manager())
        box_db.pack(side="left", padx=10)

    def create_round_action_btn(self, parent, icon, text, bg_color, fg_color, command):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        
        btn = ctk.CTkButton(box, text=icon, width=48, height=48, corner_radius=16,
                            fg_color=bg_color, hover_color="#334155",
                            text_color=fg_color, font=ctk.CTkFont(size=18), command=command,
                            border_width=1, border_color=BORDER)
        btn.pack()

        lbl = ctk.CTkLabel(box, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED)
        lbl.pack(pady=(4, 0))

        return box, lbl

    def build_projects_table(self):
        t_head = ctk.CTkFrame(self.view_container, fg_color="transparent")
        t_head.pack(fill="x", pady=(4, 6))

        self.lbl_files = ctk.CTkLabel(t_head, text=t("projects_table_title"),
                                      font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_DARK)
        self.lbl_files.pack(side="left")

        self.btn_reload = ctk.CTkButton(t_head, text=t("reload_list"), font=ctk.CTkFont(size=11, weight="bold"),
                                        fg_color="transparent", text_color=ACCENT_TEXT,
                                        hover_color="#1E293B", width=90, height=24, command=self.load_projects_list)
        self.btn_reload.pack(side="right")

        self.scroll_table = ctk.CTkScrollableFrame(self.view_container, fg_color=BG_CARD, corner_radius=16,
                                                  border_width=1, border_color=BORDER, height=220)
        self.scroll_table.pack(fill="both", expand=True)

        self.load_projects_list()

    def load_projects_list(self):
        core.write_default_index()
        for w in self.scroll_table.winfo_children():
            w.destroy()

        projects = core.list_projects()
        self._last_project_names = [p["name"] for p in projects]

        if not projects:
            empty = ctk.CTkLabel(self.scroll_table, text=t("no_projects_found"),
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
                                    command=lambda url=p["url"]: webbrowser.open(url))
            btn_web.pack(side="right", padx=(2, 8), pady=6)

            db_target = core.db_name_for(p["name"])
            btn_db = ctk.CTkButton(row, text="🗄", width=28, height=28, corner_radius=8,
                                   fg_color=BTN_SEC_BG, hover_color="#2E1065", text_color="#C084FC",
                                   border_width=1, border_color=BORDER,
                                   command=lambda d=db_target: self.open_db_manager(d))
            btn_db.pack(side="right", padx=2, pady=6)

            btn_dir = ctk.CTkButton(row, text="📁", width=28, height=28, corner_radius=8,
                                    fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                    border_width=1, border_color=BORDER,
                                    command=lambda path=p["path"]: self.open_folder(path))
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

        self.lbl_side_title = ctk.CTkLabel(head_box, text=t("sidebar_title"), font=ctk.CTkFont(size=14, weight="bold"),
                                          text_color=TEXT_DARK)
        self.lbl_side_title.pack(side="left")

        self.badge_stack_status = ctk.CTkLabel(head_box, text=t("status_standby"), font=ctk.CTkFont(size=9, weight="bold"),
                                              fg_color="#1E293B", text_color=TEXT_STATUS_OFF, corner_radius=6, padx=6, pady=2)
        self.badge_stack_status.pack(side="right")

        # 2. Tarjeta: Rendimiento del Sistema (RAM)
        card_ram = ctk.CTkFrame(pad_box, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER)
        card_ram.pack(fill="x", pady=(0, 10))

        c_ram_pad = ctk.CTkFrame(card_ram, fg_color="transparent")
        c_ram_pad.pack(fill="x", padx=12, pady=10)

        ram_head = ctk.CTkFrame(c_ram_pad, fg_color="transparent")
        ram_head.pack(fill="x")
        self.lbl_side_ram_title = ctk.CTkLabel(ram_head, text=t("system_memory"), font=ctk.CTkFont(size=11, weight="bold"),
                                              text_color=TEXT_DARK)
        self.lbl_side_ram_title.pack(side="left")
        self.lbl_ram_pct = ctk.CTkLabel(ram_head, text="35%", font=ctk.CTkFont(size=11, weight="bold"),
                                       text_color=ACCENT_TEXT)
        self.lbl_ram_pct.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(c_ram_pad, height=6, corner_radius=3, fg_color=PROGRESS_BG, progress_color=ACCENT_BLUE)
        self.progress_bar.pack(fill="x", pady=(6, 4))
        self.progress_bar.set(0.35)

        self.ram_lbl = ctk.CTkLabel(c_ram_pad, text=t("ram_stack_active"), font=ctk.CTkFont(size=10),
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
        db_p = self.state_data.get('mariadb_port', 3307)
        port_db_txt = f"Puerto {db_p}" if i18n.get_lang() == "es" else f"Port {db_p}"
        self.lbl_side_db_port = ctk.CTkLabel(db_head, text=port_db_txt,
                                             font=ctk.CTkFont(size=9, weight="bold"),
                                             fg_color="#064E3B", text_color="#34D399", corner_radius=6, padx=5, pady=1)
        self.lbl_side_db_port.pack(side="right")

        r1 = ctk.CTkFrame(c_db_pad, fg_color="transparent")
        r1.pack(fill="x", pady=1)
        ctk.CTkLabel(r1, text="Host:", font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(r1, text="127.0.0.1", font=ctk.CTkFont(size=10, family="Consolas", weight="bold"), text_color=TEXT_DARK).pack(side="right")

        r2 = ctk.CTkFrame(c_db_pad, fg_color="transparent")
        r2.pack(fill="x", pady=1)
        self.lbl_db_user_tag = ctk.CTkLabel(r2, text=t("db_user_label"), font=ctk.CTkFont(size=10), text_color=TEXT_MUTED)
        self.lbl_db_user_tag.pack(side="left")
        ctk.CTkLabel(r2, text="root", font=ctk.CTkFont(size=10, family="Consolas", weight="bold"), text_color=TEXT_DARK).pack(side="right")

        r3 = ctk.CTkFrame(c_db_pad, fg_color="transparent")
        r3.pack(fill="x", pady=1)
        self.lbl_db_pass_tag = ctk.CTkLabel(r3, text=t("db_pass_label"), font=ctk.CTkFont(size=10), text_color=TEXT_MUTED)
        self.lbl_db_pass_tag.pack(side="left")
        self.lbl_db_pass_val = ctk.CTkLabel(r3, text=t("db_no_pass"), font=ctk.CTkFont(size=10, family="Consolas", weight="bold"), text_color=TEXT_DARK)
        self.lbl_db_pass_val.pack(side="right")

        self.btn_copy_db = ctk.CTkButton(c_db_pad, text=t("btn_copy_conn"), font=ctk.CTkFont(size=10, weight="bold"),
                                         fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                         height=24, corner_radius=6, border_width=1, border_color=BORDER,
                                         command=self.copy_db_connection)
        self.btn_copy_db.pack(fill="x", pady=(6, 0))

        self.btn_open_db = ctk.CTkButton(c_db_pad, text=t("btn_open_db_web"), font=ctk.CTkFont(size=10, weight="bold"),
                                         fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color="#C084FC",
                                         height=24, corner_radius=6, border_width=1, border_color=BORDER,
                                         command=lambda: self.open_db_manager())
        self.btn_open_db.pack(fill="x", pady=(4, 0))

        # 4. Tarjeta: Carpeta Activa de Proyectos
        card_dir = ctk.CTkFrame(pad_box, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER)
        card_dir.pack(fill="x", pady=(0, 10))

        c_dir_pad = ctk.CTkFrame(card_dir, fg_color="transparent")
        c_dir_pad.pack(fill="x", padx=12, pady=10)

        self.lbl_side_dir_title = ctk.CTkLabel(c_dir_pad, text=t("projects_folder_card"), font=ctk.CTkFont(size=11, weight="bold"),
                                              text_color=TEXT_DARK)
        self.lbl_side_dir_title.pack(anchor="w", pady=(0, 4))

        p_chip = ctk.CTkFrame(c_dir_pad, fg_color=BG_ROW, corner_radius=8, border_width=1, border_color=BORDER)
        p_chip.pack(fill="x", pady=(0, 8))
        self.lbl_active_folder = ctk.CTkLabel(p_chip, text=core.get_projects_root(),
                                              font=ctk.CTkFont(size=10, family="Consolas", weight="bold"),
                                              text_color=ACCENT_TEXT, padx=8, pady=4, wraplength=210, justify="left")
        self.lbl_active_folder.pack(fill="x")

        dir_btns = ctk.CTkFrame(c_dir_pad, fg_color="transparent")
        dir_btns.pack(fill="x")

        self.btn_side_explore = ctk.CTkButton(dir_btns, text=t("explore"), font=ctk.CTkFont(size=10, weight="bold"),
                                              fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                              height=26, corner_radius=8, border_width=1, border_color=BORDER,
                                              command=self.open_projects_dir)
        self.btn_side_explore.pack(side="left", fill="x", expand=True, padx=(0, 3))

        self.btn_side_change = ctk.CTkButton(dir_btns, text=t("change"), font=ctk.CTkFont(size=10, weight="bold"),
                                             fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                             height=26, corner_radius=8, border_width=1, border_color=BORDER,
                                             command=self.open_settings_modal)
        self.btn_side_change.pack(side="right", fill="x", expand=True, padx=(3, 0))

        # 5. Botón inferior de Logs
        self.btn_side_logs = ctk.CTkButton(pad_box, text=t("btn_view_logs"), font=ctk.CTkFont(size=11, weight="bold"),
                                           fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                           border_width=1, border_color=BORDER, height=32, corner_radius=10,
                                           command=self.open_logs_dir)
        self.btn_side_logs.pack(fill="x", side="bottom", pady=4)

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
            self.badge_nginx.configure(text=t("status_online"), fg_color="#10B981", text_color="#FFFFFF")
        else:
            self.card_nginx.configure(fg_color="#1E293B")
            self.badge_nginx.configure(text=t("status_offline"), fg_color="#0F172A", text_color=TEXT_STATUS_OFF)

        php_v = status["php"]["version"]
        self.label_php_title.configure(text=f"PHP FastCGI ({php_v})")
        if self.php_var.get() != php_v:
            self.php_var.set(php_v)

        if status["mariadb"]["running"]:
            self.badge_db.configure(text=t("status_online"), fg_color="#064E3B", text_color="#34D399")
        else:
            self.badge_db.configure(text=t("status_offline"), fg_color=BG_MAIN, text_color=TEXT_STATUS_OFF)

        if status["all_running"]:
            self.btn_master.configure(text=t("btn_stop_stack"), fg_color=RED_ERROR, hover_color="#DC2626")
            if hasattr(self, "badge_stack_status"):
                self.badge_stack_status.configure(text=t("status_online"), fg_color="#064E3B", text_color="#34D399")
            if hasattr(self, "ram_lbl"):
                self.ram_lbl.configure(text=t("ram_stack_active"))
        else:
            self.btn_master.configure(text=t("btn_start_stack"), fg_color=GREEN_SUCCESS, hover_color="#059669")
            if hasattr(self, "badge_stack_status"):
                self.badge_stack_status.configure(text=t("status_standby"), fg_color="#1E293B", text_color=TEXT_STATUS_OFF)
            if hasattr(self, "ram_lbl"):
                self.ram_lbl.configure(text=t("ram_stack_stopped"))

        ram_load = self.get_system_ram_load()
        if hasattr(self, "progress_bar"):
            self.progress_bar.set(ram_load / 100.0)
        if hasattr(self, "lbl_ram_pct"):
            self.lbl_ram_pct.configure(text=f"{ram_load}%")

        cur_dir = core.get_projects_root()
        self.lbl_active_folder.configure(text=cur_dir)
        if hasattr(self, "lbl_path_display"):
            self.lbl_path_display.configure(text=cur_dir)

        db_port = status["config"].get("mariadb_port", 3307)
        if hasattr(self, "lbl_side_db_port"):
            port_lbl = f"Puerto {db_port}" if i18n.get_lang() == "es" else f"Port {db_port}"
            self.lbl_side_db_port.configure(text=port_lbl)
        if hasattr(self, "port_db_lbl"):
            self.port_db_lbl.configure(text=t("mariadb_card_sub", port=db_port))

    def toggle_language(self):
        new_lang = "en" if i18n.get_lang() == "es" else "es"
        i18n.set_lang(new_lang)
        core.set_language(new_lang)
        self.state_data["language"] = new_lang
        self.apply_language()

    def apply_language(self):
        cur_lang = i18n.get_lang()
        self.btn_lang.configure(text="🌐 EN" if cur_lang == "es" else "🌐 ES")
        
        # 1. Top bar
        if hasattr(self, "lbl_prefix"):
            self.lbl_prefix.configure(text=t("projects_path_label"))
        if hasattr(self, "btn_open_folder"):
            self.btn_open_folder.configure(text=t("open_folder"))

        # 2. Tarjetas de servicios
        if hasattr(self, "lbl_storage"):
            self.lbl_storage.configure(text=t("running_services_title"))
        if hasattr(self, "port_nginx_lbl"):
            self.port_nginx_lbl.configure(text=t("nginx_card_sub"))
        if hasattr(self, "port_php_lbl"):
            self.port_php_lbl.configure(text=t("php_card_sub"))

        # 3. Acceso rápido
        if hasattr(self, "lbl_quick"):
            self.lbl_quick.configure(text=t("quick_actions_title"))
        if hasattr(self, "lbl_act_lar"):
            self.lbl_act_lar.configure(text=t("action_laravel"))
        if hasattr(self, "lbl_act_wp"):
            self.lbl_act_wp.configure(text=t("action_wordpress"))
        if hasattr(self, "lbl_act_local"):
            self.lbl_act_local.configure(text=t("action_localhost"))
        if hasattr(self, "lbl_act_folder"):
            self.lbl_act_folder.configure(text=t("action_folder"))
        if hasattr(self, "lbl_act_terminal"):
            self.lbl_act_terminal.configure(text=t("action_terminal"))
        if hasattr(self, "lbl_act_db"):
            self.lbl_act_db.configure(text=t("action_database"))

        # 4. Tabla de proyectos
        if hasattr(self, "lbl_files"):
            self.lbl_files.configure(text=t("projects_table_title"))
        if hasattr(self, "btn_reload"):
            self.btn_reload.configure(text=t("reload_list"))

        # 5. Right Sidebar
        if hasattr(self, "lbl_side_title"):
            self.lbl_side_title.configure(text=t("sidebar_title"))
        if hasattr(self, "lbl_side_ram_title"):
            self.lbl_side_ram_title.configure(text=t("system_memory"))
        if hasattr(self, "lbl_db_user_tag"):
            self.lbl_db_user_tag.configure(text=t("db_user_label"))
        if hasattr(self, "lbl_db_pass_tag"):
            self.lbl_db_pass_tag.configure(text=t("db_pass_label"))
        if hasattr(self, "lbl_db_pass_val"):
            self.lbl_db_pass_val.configure(text=t("db_no_pass"))
        if hasattr(self, "btn_copy_db"):
            self.btn_copy_db.configure(text=t("btn_copy_conn"))
        if hasattr(self, "btn_open_db"):
            self.btn_open_db.configure(text=t("btn_open_db_web"))
        if hasattr(self, "lbl_side_dir_title"):
            self.lbl_side_dir_title.configure(text=t("projects_folder_card"))
        if hasattr(self, "btn_side_explore"):
            self.btn_side_explore.configure(text=t("explore"))
        if hasattr(self, "btn_side_change"):
            self.btn_side_change.configure(text=t("change"))
        if hasattr(self, "btn_side_logs"):
            self.btn_side_logs.configure(text=t("btn_view_logs"))

        # Aviso de actualización
        if hasattr(self, "lbl_update"):
            self.lbl_update.configure(text=t("update_available", version=self.update_info["version"]))
            if str(self.btn_update.cget("state")) != "disabled":
                self.btn_update.configure(text=self._update_btn_text())

        # 6. Refrescar estado y lista de proyectos
        self.refresh_status()
        self.load_projects_list()

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
        self.btn_master.configure(text=t("processing"), state="disabled")
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
        self._apply_window_icon(modal)

    def _apply_window_icon(self, win):
        if hasattr(self, "icon_path") and self.icon_path and os.path.exists(self.icon_path):
            try:
                win.after(80, lambda: win.iconbitmap(self.icon_path) if win.winfo_exists() else None)
            except Exception:
                pass

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

        btn = ctk.CTkButton(pad, text=t("understood"), height=32, corner_radius=10,
                            fg_color=ACCENT_BLUE, hover_color="#1D4ED8", text_color="#FFFFFF",
                            font=ctk.CTkFont(size=11, weight="bold"), command=close)
        btn.pack(fill="x")

        win.bind("<Return>", lambda e: close())
        win.bind("<Escape>", lambda e: close())
        win.grab_set()
        win.after(80, btn.focus)
        return win

    def show_dark_confirm(self, title, message, confirm_text="Eliminar", on_confirm=None, danger=True):
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

        badge = ctk.CTkLabel(head, text="🗑" if danger else "⬆", width=32, height=32, corner_radius=16,
                             fg_color="#451A1A" if danger else "#1E3A8A",
                             text_color="#EF4444" if danger else ACCENT_TEXT, font=ctk.CTkFont(size=16))
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

        btn_cancel = ctk.CTkButton(btn_row, text=t("cancel"), height=32, corner_radius=10,
                                   fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                   border_width=1, border_color=BORDER, command=close)
        btn_cancel.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_del = ctk.CTkButton(btn_row, text=confirm_text, height=32, corner_radius=10,
                                fg_color="#DC2626" if danger else ACCENT_BLUE,
                                hover_color="#B91C1C" if danger else "#1D4ED8", text_color="#FFFFFF",
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
                t("alert_services_stopped_title"),
                t("alert_services_stopped_msg"),
                alert_type="warning"
            )
            return

        win = ctk.CTkToplevel(self)
        is_lar = ptype.lower() == "laravel"
        title_txt = t("modal_create_laravel_title") if is_lar else t("modal_create_wp_title")
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

        ctk.CTkLabel(pad, text=t("modal_create_name_lbl"),
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        entry_name = ctk.CTkEntry(pad, placeholder_text=t("modal_create_placeholder"),
                                  fg_color=BG_ROW, border_color=BORDER, text_color=TEXT_DARK,
                                  height=34, corner_radius=10, font=ctk.CTkFont(size=12))
        entry_name.pack(fill="x", pady=(0, 16))
        win.after(80, entry_name.focus)

        def on_confirm():
            name = entry_name.get().strip()
            if not name:
                return
            if not core.is_valid_project_name(name):
                self.show_dark_alert(t("alert_create_error_title"), t("alert_invalid_name_msg"), alert_type="error")
                return

            status = core.get_status()
            if not status["all_running"]:
                win.destroy()
                self.show_dark_alert(
                    t("alert_services_stopped_title"),
                    t("alert_services_stopped_msg"),
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
                    db_p = self.state_data.get("mariadb_port", 3307)
                    self.after(50, lambda: self.show_dark_alert(
                        t("alert_project_created_title"),
                        t("alert_project_created_msg", type=ptype.capitalize(), name=name, port=db_p),
                        alert_type="success"
                    ))
                else:
                    self.after(50, lambda: self.show_dark_alert(t("alert_create_error_title"), msg, alert_type="error"))

            threading.Thread(target=run, daemon=True).start()

        def on_cancel():
            win.destroy()

        entry_name.bind("<Return>", lambda e: on_confirm())
        win.bind("<Escape>", lambda e: on_cancel())

        btn_row = ctk.CTkFrame(pad, fg_color="transparent")
        btn_row.pack(fill="x")

        btn_cancel = ctk.CTkButton(btn_row, text=t("cancel"), height=32, corner_radius=10,
                                   fg_color=BTN_SEC_BG, hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT,
                                   border_width=1, border_color=BORDER, command=on_cancel)
        btn_cancel.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_ok = ctk.CTkButton(btn_row, text=t("modal_create_btn"), height=32, corner_radius=10,
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
                self.after(50, lambda: self.show_dark_alert(t("alert_delete_error_title"), msg, alert_type="error"))

        db_name = core.db_name_for(name)
        self.show_dark_confirm(
            t("modal_delete_title"),
            t("modal_delete_msg", name=name, db_name=db_name),
            confirm_text=t("modal_delete_btn"),
            on_confirm=do_delete
        )

    def open_settings_modal(self):
        win = ctk.CTkToplevel(self)
        win.title(t("settings_title"))
        win.resizable(False, False)
        win.configure(fg_color=BG_CARD)
        win.attributes('-topmost', True)
        win.transient(self)
        self.center_modal(win, 450, 330)

        ctk.CTkLabel(win, text=t("settings_title"), font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=22, pady=(18, 4))
        ctk.CTkLabel(win, text="Personaliza la ubicación de tus proyectos y puertos locales." if i18n.get_lang() == "es" else "Customize your projects folder and local service ports.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w", padx=22, pady=(0, 14))

        f_box = ctk.CTkFrame(win, fg_color="transparent")
        f_box.pack(fill="x", padx=22, pady=4)
        ctk.CTkLabel(f_box, text=t("settings_folder_lbl"), font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w")

        dir_row = ctk.CTkFrame(f_box, fg_color="transparent")
        dir_row.pack(fill="x", pady=4)

        entry_dir = ctk.CTkEntry(dir_row, fg_color=BG_ROW, text_color=TEXT_DARK,
                                 border_color=BORDER, corner_radius=10)
        entry_dir.insert(0, core.get_projects_root())
        entry_dir.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def browse():
            f = filedialog.askdirectory(title=t("settings_folder_lbl"))
            if f:
                entry_dir.delete(0, "end")
                entry_dir.insert(0, f)

        ctk.CTkButton(dir_row, text=t("browse"), width=80, fg_color=BTN_SEC_BG,
                      hover_color=BTN_SEC_HOVER, text_color=BTN_SEC_TEXT, corner_radius=10,
                      border_width=1, border_color=BORDER, command=browse).pack(side="right")

        p_row = ctk.CTkFrame(win, fg_color="transparent")
        p_row.pack(fill="x", padx=22, pady=6)

        c1 = ctk.CTkFrame(p_row, fg_color="transparent")
        c1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(c1, text="Puerto Nginx" if i18n.get_lang() == "es" else "Nginx Port", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_DARK).pack(anchor="w")
        entry_nginx = ctk.CTkEntry(c1, fg_color=BG_ROW, text_color=TEXT_DARK, border_color=BORDER, corner_radius=10)
        entry_nginx.insert(0, str(self.state_data.get("nginx_port", 80)))
        entry_nginx.pack(fill="x", pady=4)

        c2 = ctk.CTkFrame(p_row, fg_color="transparent")
        c2.pack(side="right", fill="x", expand=True, padx=(6, 0))
        ctk.CTkLabel(c2, text=t("settings_port_lbl"), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_DARK).pack(anchor="w")
        entry_db = ctk.CTkEntry(c2, fg_color=BG_ROW, text_color=TEXT_DARK, border_color=BORDER, corner_radius=10)
        entry_db.insert(0, str(self.state_data.get("mariadb_port", 3307)))
        entry_db.pack(fill="x", pady=4)

        def save():
            projects_dir = entry_dir.get().strip()
            try:
                nginx_port = int(entry_nginx.get())
                db_port = int(entry_db.get())
            except ValueError:
                self.show_dark_alert(t("settings_title"), t("alert_invalid_settings_msg"), alert_type="error")
                return
            valid_ports = all(1 <= p_ <= 65535 for p_ in (nginx_port, db_port)) and nginx_port != db_port
            if not valid_ports or not os.path.isdir(projects_dir):
                self.show_dark_alert(t("settings_title"), t("alert_invalid_settings_msg"), alert_type="error")
                return
            new_conf = {
                "projects_dir": projects_dir,
                "nginx_port": nginx_port,
                "mariadb_port": db_port
            }
            core.update_global_config(new_conf)
            self.state_data = core.load_state()
            self.refresh_status()
            win.destroy()
            self.show_dark_alert(t("settings_title"), t("settings_saved"), alert_type="success")

        ctk.CTkButton(win, text=t("save_changes"), fg_color=ACCENT_BLUE, hover_color="#1D4ED8",
                      text_color="#FFFFFF", height=38, corner_radius=12,
                      command=save).pack(fill="x", padx=22, pady=(16, 0))

    def open_localhost(self):
        port = self.state_data.get("nginx_port", 80)
        url = f"http://localhost:{port}" if port != 80 else "http://localhost"
        webbrowser.open(url)

    def open_folder(self, path):
        """Abre una carpeta en el Explorador sin pasar por el shell."""
        if os.path.isdir(path):
            os.startfile(path)

    def open_projects_dir(self):
        self.open_folder(core.get_projects_root())

    def copy_db_connection(self):
        port = self.state_data.get("mariadb_port", 3307)
        conn_str = f"mysql -h 127.0.0.1 -P {port} -u root"
        self.clipboard_clear()
        self.clipboard_append(conn_str)
        self.update()
        self.show_dark_alert("MariaDB Server", f"{t('alert_conn_copied_msg')}\n\n{conn_str}", alert_type="info")

    def open_logs_dir(self):
        logs_dir = os.path.join(core.BASE_DIR, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        self.open_folder(logs_dir)

    def open_terminal(self):
        ver = self.php_var.get()
        if ver not in core.get_installed_php_versions():
            return
        p_dir = core.get_projects_root()
        php_dir = os.path.join(core.BIN_DIR, "php", f"php-{ver}")
        mariadb_bin = os.path.join(core.BIN_DIR, "mariadb")
        composer_dir = os.path.join(core.BIN_DIR, "composer")
        env = os.environ.copy()
        env["PATH"] = os.pathsep.join([php_dir, composer_dir, mariadb_bin, env.get("PATH", "")])
        subprocess.Popen(["cmd.exe", "/k", f"echo AetherStack Dev Shell (PHP {ver})"],
                         cwd=p_dir, env=env, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def open_db_manager(self, db_name=None):
        status = core.get_status()
        if not status["all_running"]:
            self.show_dark_alert(
                t("action_database"),
                t("alert_db_offline_msg"),
                alert_type="warning"
            )
            return
        core.open_db_manager(db_name)

if __name__ == "__main__":
    app = AetherDribbbleApp()
    app.mainloop()
