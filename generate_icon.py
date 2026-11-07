from PIL import Image, ImageDraw

def create_aether_icon(path):
    size = (256, 256)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Fondo redondeado oscuro (Slate 900)
    draw.rounded_rectangle([8, 8, 248, 248], radius=54, fill="#0F172A", outline="#38BDF8", width=6)

    # Gradiente / Rayo estilizado Aether en Cian Neón (#38BDF8) a Indigo (#6366F1)
    points = [
        (142, 38),   # Punta superior
        (72, 138),   # Quiebre izquierdo
        (130, 138),  # Centro adentro
        (114, 218),  # Punta inferior
        (184, 118),  # Quiebre derecho
        (126, 118)   # Centro arriba
    ]
    draw.polygon(points, fill="#38BDF8")

    # Guardar en múltiples resoluciones ICO estándar de Windows
    image.save(path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Icono generado con éxito:", path)

if __name__ == "__main__":
    create_aether_icon(r"D:\LabIA\aetherstack\icon.ico")
