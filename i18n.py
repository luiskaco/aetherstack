# -*- coding: utf-8 -*-
"""
AetherStack - Internationalization (i18n) Module
Provides translations for Spanish (es) and English (en).
"""

_CURRENT_LANG = "es"

TRANSLATIONS = {
    "es": {
        # Common / Buttons
        "ok": "OK",
        "cancel": "Cancelar",
        "understood": "Entendido",
        "delete": "Eliminar",
        "save_changes": "Guardar Cambios",
        "processing": "Procesando...",
        "browse": "Examinar...",
        "change": "Cambiar",
        "explore": "Explorar",
        
        # Top Bar
        "projects_path_label": "Ruta de Proyectos:",
        "open_folder": "Abrir carpeta",
        "btn_start_stack": "INICIAR STACK",
        "btn_stop_stack": "DETENER STACK",
        "lang_switch_btn": "🌐 EN",
        "update_available": "Nueva versión disponible: v{version}",
        "update_download": "Ver novedades",
        "settings_tld_lbl": "Dominio de desarrollo (ej. test):",
        "btn_import_sync": "Importar proyectos y hosts",
        "settings_hosts_hint": "Importa los proyectos que ya están en la carpeta y escribe sus dominios en el archivo hosts de Windows. Windows pedirá permiso de administrador.",
        "sync_running": "Trabajando...",
        "sync_updated": "Listo: {count} proyectos importados y dominios escritos en el archivo hosts.",
        "sync_unchanged": "Todo estaba al día: {count} proyectos importados y los dominios ya estaban en el archivo hosts.",
        "sync_cancelled": "Se importaron {count} proyectos, pero no se aceptó el permiso de Windows: los dominios no se escribieron en el archivo hosts.",
        "sync_error": "No se pudo actualizar el archivo hosts. Prueba de nuevo y acepta el aviso de Windows.",
        "tray_open": "Abrir AetherStack",
        "tray_quit": "Salir",
        "tray_start": "Iniciar stack",
        "tray_stop": "Detener stack",
        "tray_status_running": "Stack en ejecución",
        "tray_status_partial": "Stack parcialmente activo",
        "tray_status_stopped": "Stack detenido",
        "tray_bg_title": "AetherStack sigue en segundo plano",
        "tray_bg_msg": "Los servicios siguen activos. Usa el icono de la bandeja para abrirlo o salir.",
        "exit_confirm_title": "Salir de AetherStack",
        "exit_confirm_msg": "El stack sigue en ejecución. Si sales, se detendrán Nginx, PHP y MariaDB.",
        "exit_confirm_btn": "Detener y salir",
        "update_now": "Actualizar ahora",
        "update_confirm_title": "Actualizar a v{version}",
        "update_confirm_msg": "Se descargará la nueva versión, se verificará su integridad y la app se reiniciará.\n\nTus proyectos, bases de datos y ajustes no se tocan.",
        "update_downloading": "Actualizando...",
        "update_done_title": "Actualización lista",
        "update_done_msg": "AetherStack v{version} se instaló correctamente. La app se reiniciará ahora.",
        "update_error_title": "No se pudo actualizar",
        "update_error_msg": "Se mantiene la versión actual.\n\n{detail}",
        
        # Dashboard Cards
        "running_services_title": "Servicios en Ejecución",
        "nginx_card_title": "Nginx Web Server",
        "nginx_card_sub": "Puerto 80 • HTTP",
        "php_card_sub": "Puerto 9000 • FastCGI",
        "mariadb_card_title": "MariaDB Server",
        "mariadb_card_sub": "Puerto {port} • MySQL",
        "status_online": "ONLINE",
        "status_offline": "OFFLINE",
        "status_standby": "STANDBY",
        
        # Quick Actions
        "quick_actions_title": "Acceso Rápido & Creación",
        "action_laravel": "Laravel",
        "action_wordpress": "WordPress",
        "action_localhost": "Localhost",
        "action_folder": "Carpeta",
        "action_terminal": "Terminal",
        "action_database": "Gestor DB",
        
        # Projects Table
        "projects_table_title": "Mis Proyectos",
        "reload_list": "Recargar lista",
        "no_projects_found": "No hay proyectos WordPress ni Laravel en la carpeta.",
        
        # Right Sidebar
        "sidebar_title": "Detalles del Stack",
        "system_memory": "⚡ Memoria del Sistema",
        "ram_stack_active": "Stack ligero: < 95 MB activos",
        "ram_stack_stopped": "Servicios detenidos",
        "db_host_label": "Host:",
        "db_user_label": "Usuario:",
        "db_pass_label": "Clave:",
        "db_no_pass": "(sin contraseña)",
        "btn_copy_conn": "📋 Copiar Conexión",
        "btn_open_db_web": "🗄 Abrir HeidiSQL",
        "projects_folder_card": "📁 Carpeta de Proyectos",
        "btn_view_logs": "📜 Ver Logs del Stack",
        
        # Modals: Create Project
        "modal_create_laravel_title": "Crear Proyecto Laravel",
        "modal_create_wp_title": "Crear Sitio WordPress",
        "modal_create_name_lbl": "Ingresa el nombre del proyecto (ej: mi-web):",
        "modal_create_placeholder": "ej: mi-web, blog, api-rest",
        "modal_create_btn": "Crear Proyecto",
        
        # Modals: Delete Project
        "modal_delete_title": "Eliminar Proyecto",
        "modal_delete_msg": "¿Estás seguro de que deseas eliminar permanentemente '{name}'?\n\nEsta acción borrará la carpeta física y la base de datos asociada '{db_name}'.",
        "modal_delete_btn": "Eliminar Permanentemente",
        "modal_delete_type": "Para confirmar, escribe el nombre del proyecto: {name}",
        
        # Modals: Settings
        "settings_title": "Configuración General",
        "settings_folder_lbl": "Carpeta raíz de proyectos (WordPress & Laravel):",
        "settings_port_lbl": "Puerto de MariaDB (por defecto 3307):",
        "settings_lang_lbl": "Idioma de la interfaz:",
        "settings_saved": "Configuración guardada correctamente.",
        
        # Alerts & Notifications
        "alert_services_stopped_title": "Servicios Detenidos",
        "alert_services_stopped_msg": "No puedes crear proyectos mientras los servicios estén apagados.\n\nInicia el stack pulsando 'INICIAR STACK' para activar Nginx, PHP y MariaDB.",
        "alert_project_created_title": "¡Proyecto Creado!",
        "alert_project_created_msg": "¡Proyecto {type} '{name}' creado con éxito!\nBase de datos en puerto {port}.",
        "alert_create_error_title": "Error al Crear",
        "alert_invalid_name_msg": "Nombre inválido. Usa solo letras, números, guion (-) y guion bajo (_), máximo 64 caracteres, y empieza con letra o número.",
        "alert_invalid_settings_msg": "Revisa los datos: la carpeta debe existir y los puertos deben ser números distintos entre 1 y 65535.",
        "alert_delete_error_title": "Error al Eliminar",
        "alert_conn_copied_title": "Conexión Copiada",
        "alert_conn_copied_msg": "Datos de conexión MySQL copiados al portapapeles.",
        "alert_db_offline_msg": "Debes iniciar el stack de servicios para abrir HeidiSQL.\n\nPulsa 'INICIAR STACK' para levantar MariaDB en el puerto 3307.",
    },
    "en": {
        # Common / Buttons
        "ok": "OK",
        "cancel": "Cancel",
        "understood": "Understood",
        "delete": "Delete",
        "save_changes": "Save Changes",
        "processing": "Processing...",
        "browse": "Browse...",
        "change": "Change",
        "explore": "Explore",
        
        # Top Bar
        "projects_path_label": "Projects Path:",
        "open_folder": "Open folder",
        "btn_start_stack": "START STACK",
        "btn_stop_stack": "STOP STACK",
        "lang_switch_btn": "🌐 ES",
        "update_available": "New version available: v{version}",
        "update_download": "See what's new",
        "settings_tld_lbl": "Development domain (e.g. test):",
        "btn_import_sync": "Import projects and hosts",
        "settings_hosts_hint": "Imports the projects already in the folder and writes their domains to the Windows hosts file. Windows will ask for administrator permission.",
        "sync_running": "Working...",
        "sync_updated": "Done: {count} projects imported and domains written to the hosts file.",
        "sync_unchanged": "Everything was up to date: {count} projects imported and the domains were already in the hosts file.",
        "sync_cancelled": "{count} projects were imported, but the Windows permission was not accepted: the domains were not written to the hosts file.",
        "sync_error": "The hosts file could not be updated. Try again and accept the Windows prompt.",
        "tray_open": "Open AetherStack",
        "tray_quit": "Quit",
        "tray_start": "Start stack",
        "tray_stop": "Stop stack",
        "tray_status_running": "Stack running",
        "tray_status_partial": "Stack partially active",
        "tray_status_stopped": "Stack stopped",
        "tray_bg_title": "AetherStack is still running in the background",
        "tray_bg_msg": "The services are still active. Use the tray icon to open it or quit.",
        "exit_confirm_title": "Quit AetherStack",
        "exit_confirm_msg": "The stack is still running. If you quit, Nginx, PHP and MariaDB will be stopped.",
        "exit_confirm_btn": "Stop and quit",
        "update_now": "Update now",
        "update_confirm_title": "Update to v{version}",
        "update_confirm_msg": "The new version will be downloaded, its integrity verified, and the app will restart.\n\nYour projects, databases and settings are not touched.",
        "update_downloading": "Updating...",
        "update_done_title": "Update complete",
        "update_done_msg": "AetherStack v{version} was installed successfully. The app will restart now.",
        "update_error_title": "Update failed",
        "update_error_msg": "The current version is kept.\n\n{detail}",
        
        # Dashboard Cards
        "running_services_title": "Running Services",
        "nginx_card_title": "Nginx Web Server",
        "nginx_card_sub": "Port 80 • HTTP",
        "php_card_sub": "Port 9000 • FastCGI",
        "mariadb_card_title": "MariaDB Server",
        "mariadb_card_sub": "Port {port} • MySQL",
        "status_online": "ONLINE",
        "status_offline": "OFFLINE",
        "status_standby": "STANDBY",
        
        # Quick Actions
        "quick_actions_title": "Quick Access & Creation",
        "action_laravel": "Laravel",
        "action_wordpress": "WordPress",
        "action_localhost": "Localhost",
        "action_folder": "Folder",
        "action_terminal": "Terminal",
        "action_database": "DB Manager",
        
        # Projects Table
        "projects_table_title": "My Projects",
        "reload_list": "Reload list",
        "no_projects_found": "No WordPress or Laravel projects found in folder.",
        
        # Right Sidebar
        "sidebar_title": "Stack Details",
        "system_memory": "⚡ System Memory",
        "ram_stack_active": "Lightweight stack: < 95 MB active",
        "ram_stack_stopped": "Services stopped",
        "db_host_label": "Host:",
        "db_user_label": "User:",
        "db_pass_label": "Password:",
        "db_no_pass": "(no password)",
        "btn_copy_conn": "📋 Copy Connection",
        "btn_open_db_web": "🗄 Open HeidiSQL",
        "projects_folder_card": "📁 Projects Folder",
        "btn_view_logs": "📜 View Stack Logs",
        
        # Modals: Create Project
        "modal_create_laravel_title": "Create Laravel Project",
        "modal_create_wp_title": "Create WordPress Site",
        "modal_create_name_lbl": "Enter project name (e.g. my-web):",
        "modal_create_placeholder": "e.g. my-web, blog, api-rest",
        "modal_create_btn": "Create Project",
        
        # Modals: Delete Project
        "modal_delete_title": "Delete Project",
        "modal_delete_msg": "Are you sure you want to permanently delete '{name}'?\n\nThis will remove the physical folder and the database '{db_name}'.",
        "modal_delete_btn": "Delete Permanently",
        "modal_delete_type": "To confirm, type the project name: {name}",
        
        # Modals: Settings
        "settings_title": "General Settings",
        "settings_folder_lbl": "Root projects directory (WordPress & Laravel):",
        "settings_port_lbl": "MariaDB Port (default 3307):",
        "settings_lang_lbl": "Interface Language:",
        "settings_saved": "Settings saved successfully.",
        
        # Alerts & Notifications
        "alert_services_stopped_title": "Services Stopped",
        "alert_services_stopped_msg": "You cannot create projects while services are stopped.\n\nStart the stack by clicking 'START STACK' to activate Nginx, PHP and MariaDB.",
        "alert_project_created_title": "Project Created!",
        "alert_project_created_msg": "{type} project '{name}' created successfully!\nDatabase on port {port}.",
        "alert_create_error_title": "Error Creating Project",
        "alert_invalid_name_msg": "Invalid name. Use only letters, numbers, hyphen (-) and underscore (_), up to 64 characters, starting with a letter or number.",
        "alert_invalid_settings_msg": "Check the values: the folder must exist and ports must be different numbers between 1 and 65535.",
        "alert_delete_error_title": "Error Deleting Project",
        "alert_conn_copied_title": "Connection Copied",
        "alert_conn_copied_msg": "MySQL connection details copied to clipboard.",
        "alert_db_offline_msg": "You must start the service stack to open HeidiSQL.\n\nClick 'START STACK' to run MariaDB on port 3307.",
    }
}

def set_lang(lang_code):
    global _CURRENT_LANG
    if lang_code in TRANSLATIONS:
        _CURRENT_LANG = lang_code
    return _CURRENT_LANG

def get_lang():
    return _CURRENT_LANG

def t(key, **kwargs):
    lang_dict = TRANSLATIONS.get(_CURRENT_LANG, TRANSLATIONS["es"])
    text = lang_dict.get(key)
    if text is None:
        text = TRANSLATIONS["es"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
