"""
AetherStack - Icono de la bandeja del sistema (opcional).

Muestra que el stack está en segundo plano y de qué color es su estado:
verde = todo activo, ámbar = parcial, gris = detenido.

Necesita `pystray` y `Pillow`. Si faltan, AVAILABLE es False y la app funciona igual, sin icono.
No usa Tk: recibe funciones desde la app, que decide en qué hilo se ejecutan.
"""
try:
    import pystray
    from PIL import Image, ImageDraw
    AVAILABLE = True
except Exception:  # librería no instalada o sin entorno gráfico
    pystray = Image = ImageDraw = None
    AVAILABLE = False

RUNNING, PARTIAL, STOPPED = "running", "partial", "stopped"
COLORS = {RUNNING: "#10B981", PARTIAL: "#F59E0B", STOPPED: "#64748B"}
_BOLT = [(142, 36), (72, 140), (130, 140), (114, 220), (184, 116), (126, 116)]  # mismo rayo que icon.ico


def stack_state(status):
    """Resume core.get_status() en RUNNING, PARTIAL o STOPPED."""
    flags = [bool(status[k]["running"]) for k in ("nginx", "php", "mariadb")]
    if all(flags):
        return RUNNING
    return PARTIAL if any(flags) else STOPPED


def render_icon(state, size=64):
    """Cuadrado redondeado del color del estado con el rayo de AetherStack en blanco."""
    if not AVAILABLE:
        return None
    scale = 256
    img = Image.new("RGBA", (scale, scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([10, 10, 246, 246], radius=52, fill=COLORS[state])
    d.polygon(_BOLT, fill="#FFFFFF")
    return img.resize((size, size), Image.LANCZOS)


class TrayIcon:
    """
    on_open / on_toggle / on_quit: funciones sin argumentos (se llaman desde el hilo del icono;
    la app las reenvía al hilo de Tk). labels: textos ya traducidos, ver set_state().
    """

    def __init__(self, name, on_open, on_toggle, on_quit):
        self._name = name
        self._on_open, self._on_toggle, self._on_quit = on_open, on_toggle, on_quit
        self._state = None
        self._labels = {"open": "Open", "toggle": "Start", "quit": "Quit", "status": "", "tooltip": name}
        menu = pystray.Menu(
            pystray.MenuItem(lambda item: self._labels["open"], lambda icon, item: self._on_open(), default=True),
            pystray.MenuItem(lambda item: self._labels["status"], None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda item: self._labels["toggle"], lambda icon, item: self._on_toggle()),
            pystray.MenuItem(lambda item: self._labels["quit"], lambda icon, item: self._on_quit()),
        )
        self._icon = pystray.Icon("aetherstack", render_icon(STOPPED), name, menu)

    def start(self):
        self._icon.run_detached()

    def set_state(self, state, labels):
        """Actualiza color, texto emergente y menú solo si algo cambió (se llama cada pocos segundos)."""
        if state == self._state and labels == self._labels:
            return
        if state != self._state:
            self._icon.icon = render_icon(state)
        self._state, self._labels = state, dict(labels)
        self._icon.title = labels.get("tooltip", self._name)
        self._icon.update_menu()

    def notify(self, title, message):
        try:
            self._icon.notify(message, title)
        except Exception:
            pass  # las notificaciones son un extra: nunca deben romper la app

    def stop(self):
        try:
            self._icon.stop()
        except Exception:
            pass
