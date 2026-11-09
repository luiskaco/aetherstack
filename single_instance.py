"""
AetherStack - Una sola copia de la aplicación (solo biblioteca estándar, Windows).

Con el icono de la bandeja la app puede quedar oculta. Si el usuario vuelve a abrirla desde el
acceso directo, la segunda copia no abre otra ventana: avisa a la primera mediante un archivo
y se cierra; la primera se muestra.
"""
import ctypes
import os
import time

ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Local\\AetherStack.SingleInstance"
SHOW_FLAG = "show-window.flag"


def acquire(wait_seconds=0.0):
    """
    Intenta ser la única copia. Devuelve (handle, es_la_primera).
    Con wait_seconds espera a que otra copia que se está cerrando libere el bloqueo
    (reinicio tras una actualización).
    """
    if os.name != "nt":
        return None, True
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    deadline = time.time() + wait_seconds
    while True:
        handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        already = ctypes.get_last_error() == ERROR_ALREADY_EXISTS or kernel32.GetLastError() == ERROR_ALREADY_EXISTS
        if not already:
            return handle, True
        kernel32.CloseHandle(ctypes.c_void_p(handle))
        if time.time() >= deadline:
            return None, False
        time.sleep(0.25)


def release(handle):
    if handle and os.name == "nt":
        ctypes.windll.kernel32.CloseHandle(ctypes.c_void_p(handle))


def request_show(conf_dir):
    """Lo llama la segunda copia: pide a la primera que muestre su ventana."""
    try:
        os.makedirs(conf_dir, exist_ok=True)
        with open(os.path.join(conf_dir, SHOW_FLAG), "w") as f:
            f.write("1")
    except OSError:
        pass


def consume_show_request(conf_dir):
    """Lo llama la primera copia periódicamente. True si hay que mostrar la ventana."""
    path = os.path.join(conf_dir, SHOW_FLAG)
    if not os.path.exists(path):
        return False
    try:
        os.remove(path)
    except OSError:
        pass
    return True
