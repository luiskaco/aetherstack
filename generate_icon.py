import os
import sys
import subprocess
import ctypes
from PIL import Image, ImageDraw

def create_aether_icon(path):
    size = (256, 256)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Fondo redondeado oscuro (Slate 900) con borde cian neón (#38BDF8)
    draw.rounded_rectangle([10, 10, 246, 246], radius=52, fill="#0F172A", outline="#38BDF8", width=8)

    # Rayo estilizado Aether en Cian Neón (#38BDF8)
    points = [
        (142, 36),   # Punta superior
        (72, 140),   # Quiebre izquierdo
        (130, 140),  # Centro adentro
        (114, 220),  # Punta inferior
        (184, 116),  # Quiebre derecho
        (126, 116)   # Centro arriba
    ]
    draw.polygon(points, fill="#38BDF8")

    # Guardar en resoluciones ICO estándar con bitmap_format="bmp" (DIB nativo de Windows para compatibilidad total)
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    image.save(path, format="ICO", sizes=sizes, bitmap_format="bmp")
    print("Icono .ico compatible con Windows generado con éxito en:", path)

def create_shortcuts(base_dir):
    icon_path = os.path.join(base_dir, "icon.ico")
    app_py = os.path.join(base_dir, "app.py")
    
    # Resolver pythonw.exe dinámicamente
    python_dir = os.path.dirname(sys.executable)
    pythonw = os.path.join(python_dir, "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = "pythonw.exe"

    # Script PowerShell para crear el acceso directo en Desktop y en base_dir
    ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")

# 1. Escritorio
$s1 = $WshShell.CreateShortcut("$desktop\\AetherStack.lnk")
$s1.TargetPath = "{pythonw}"
$s1.Arguments = '"{app_py}"'
$s1.WorkingDirectory = "{base_dir}"
$s1.IconLocation = "{icon_path},0"
$s1.Description = "AetherStack - Local Dev Environment"
$s1.Save()

# 2. Carpeta local
$s2 = $WshShell.CreateShortcut("{base_dir}\\AetherStack.lnk")
$s2.TargetPath = "{pythonw}"
$s2.Arguments = '"{app_py}"'
$s2.WorkingDirectory = "{base_dir}"
$s2.IconLocation = "{icon_path},0"
$s2.Description = "AetherStack - Local Dev Environment"
$s2.Save()
'''
    res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script], capture_output=True, text=True)
    if res.returncode == 0:
        print("Accesos directos actualizados correctamente.")
    else:
        print("Aviso al crear accesos directos:", res.stderr)

    # Notificar al Shell de Windows (Explorer) para refrescar la caché de iconos al instante
    try:
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, 0, 0)
        print("Caché de iconos de Windows actualizada vía SHChangeNotify.")
    except Exception as e:
        print("Aviso al notificar shell:", e)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_file = os.path.join(base_dir, "icon.ico")
    create_aether_icon(icon_file)
    create_shortcuts(base_dir)
