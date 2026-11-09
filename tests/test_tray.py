"""Pruebas del icono de la bandeja y de la copia única. Ejecutar: python -m unittest discover -s tests -v"""
import os
import sys
import tempfile
import unittest
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import single_instance
import tray


def status(nginx, php, mariadb):
    return {"nginx": {"running": nginx}, "php": {"running": php}, "mariadb": {"running": mariadb}}


class StackStateTests(unittest.TestCase):
    def test_states(self):
        self.assertEqual(tray.stack_state(status(True, True, True)), tray.RUNNING)
        self.assertEqual(tray.stack_state(status(False, False, False)), tray.STOPPED)
        for partial in (status(True, False, False), status(True, True, False), status(False, False, True)):
            self.assertEqual(tray.stack_state(partial), tray.PARTIAL)

    def test_every_state_has_a_color(self):
        for state in (tray.RUNNING, tray.PARTIAL, tray.STOPPED):
            self.assertRegex(tray.COLORS[state], r"^#[0-9A-F]{6}$")
        self.assertEqual(len(set(tray.COLORS.values())), 3)


@unittest.skipUnless(tray.AVAILABLE, "pystray/Pillow no instalados")
class IconTests(unittest.TestCase):
    def test_icons_are_distinguishable_by_state(self):
        imgs = {s: tray.render_icon(s, 16) for s in (tray.RUNNING, tray.PARTIAL, tray.STOPPED)}
        for img in imgs.values():
            self.assertEqual(img.size, (16, 16))
            self.assertEqual(img.mode, "RGBA")
        # El píxel del fondo (esquina interior) tiene el color del estado
        centers = {s: img.getpixel((2, 8))[:3] for s, img in imgs.items()}
        self.assertEqual(len(set(centers.values())), 3, centers)

    def test_icon_has_transparent_corners_and_visible_bolt(self):
        img = tray.render_icon(tray.RUNNING, 64)
        self.assertEqual(img.getpixel((0, 0))[3], 0)  # esquina transparente
        px = img.load()
        white = sum(1 for x in range(64) for y in range(64) if px[x, y][:3] == (255, 255, 255) and px[x, y][3] == 255)
        self.assertGreater(white, 100)  # el rayo blanco se ve


class SingleInstanceTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "solo Windows")
    def test_second_acquire_fails_until_first_releases(self):
        # Nombre propio: la prueba no depende de si la app real está abierta
        name = "Local\\AetherStack.Test." + uuid.uuid4().hex
        first, ok1 = single_instance.acquire(name=name)
        try:
            self.assertTrue(ok1)
            second, ok2 = single_instance.acquire(name=name)
            self.assertFalse(ok2)
            self.assertIsNone(second)
        finally:
            single_instance.release(first)
        third, ok3 = single_instance.acquire(name=name)
        try:
            self.assertTrue(ok3)
        finally:
            single_instance.release(third)

    def test_show_request_roundtrip(self):
        with tempfile.TemporaryDirectory() as conf:
            self.assertFalse(single_instance.consume_show_request(conf))
            single_instance.request_show(conf)
            self.assertTrue(single_instance.consume_show_request(conf))
            self.assertFalse(single_instance.consume_show_request(conf))  # se consume una sola vez


if __name__ == "__main__":
    unittest.main()
