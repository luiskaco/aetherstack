"""
Compatibilidad de la actualización con un clic con versiones YA PUBLICADAS.

El actualizador de cada versión solo instala una lista fija de archivos. Si el paquete nuevo trae
un archivo que la versión instalada no conoce, esa versión lo ignora y la app queda rota
(pasó con sigverify.py en v1.2.2 y con downloads.py en v1.2.3).

Esta prueba lee la lista de archivos permitidos del updater.py REAL de cada versión de
SUPPORTED_ONE_CLICK_FROM (desde git) y comprueba que el paquete actual cabe entera en ella.

Al publicar una versión nueva, añádela a SUPPORTED_ONE_CLICK_FROM. Las versiones que ya no
puedan actualizarse con un clic deben tener retirados los assets de código de su release.
Ejecutar: python -m unittest discover -s tests -v
"""
import ast
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
import updater

# Versiones cuyos clientes reconocen el prefijo actual de los assets y pueden actualizarse
# con un clic al paquete actual. v1.2.5 es la primera con el prefijo "AetherStack-update-".
SUPPORTED_ONE_CLICK_FROM = ["v1.2.5"]

CURRENT_PREFIX = "AetherStack-update-"
OLD_CLIENT_TAGS = ["v1.2.1", "v1.2.2", "v1.2.3", "v1.2.4"]


def old_allowlist(tag):
    """(archivos_raiz, carpetas) que aceptaba el updater.py de esa versión, o None si no hay git/tag."""
    try:
        src = subprocess.run(["git", "show", f"{tag}:updater.py"], cwd=ROOT, capture_output=True,
                             text=True, encoding="utf-8", check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    values = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("CODE_ROOT_FILES", "CODE_TREES"):
                values[node.targets[0].id] = ast.literal_eval(node.value)
    return values["CODE_ROOT_FILES"], values["CODE_TREES"]


def current_package_members():
    members = list(updater.CODE_ROOT_FILES)
    for tree in updater.CODE_TREES:
        for cur, dirs, files in os.walk(os.path.join(ROOT, tree)):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in files:
                members.append(os.path.relpath(os.path.join(cur, name), ROOT).replace("\\", "/"))
    return members


class CompatTests(unittest.TestCase):
    def test_package_fits_in_allowlist_of_supported_releases(self):
        for tag in SUPPORTED_ONE_CLICK_FROM:
            allow = old_allowlist(tag)
            if allow is None:
                self.skipTest(f"No hay git o falta la etiqueta {tag}")
            root_files, trees = allow
            not_installable = [m for m in current_package_members()
                               if m not in root_files and not any(m.startswith(t + "/") for t in trees)]
            self.assertEqual(not_installable, [],
                             f"{tag} ignoraría estos archivos y la app quedaría rota tras actualizar: "
                             f"{not_installable}. Publica primero una versión intermedia que los admita.")

    def test_every_top_level_module_is_in_the_package(self):
        # Un .py nuevo en la raíz que no esté en CODE_ROOT_FILES no viajaría en la actualización
        top_level = sorted(f for f in os.listdir(ROOT) if f.endswith(".py") and os.path.isfile(os.path.join(ROOT, f)))
        missing = [f for f in top_level if f not in updater.CODE_ROOT_FILES]
        self.assertEqual(missing, [], f"Añádelos a CODE_ROOT_FILES en updater.py: {missing}")

    def test_old_clients_do_not_recognize_current_update_assets(self):
        # Si un cliente antiguo reconociera el paquete actual, podría instalarlo a medias y romperse
        for tag in OLD_CLIENT_TAGS:
            try:
                src = subprocess.run(["git", "show", f"{tag}:core.py"], cwd=ROOT, capture_output=True,
                                     text=True, encoding="utf-8", check=True).stdout
            except (OSError, subprocess.CalledProcessError):
                self.skipTest(f"No hay git o falta la etiqueta {tag}")
            patterns = re.findall(r're\.match\(r"(\^AetherStack-[^"]+)", name\)', src)
            self.assertTrue(patterns, f"{tag}: no se encontró cómo reconoce los assets")
            for name in (f"{CURRENT_PREFIX}v9.9.9.zip", f"{CURRENT_PREFIX}v9.9.9.zip.sig", f"{CURRENT_PREFIX}v9.9.9.zip.sha256"):
                for pat in patterns:
                    self.assertIsNone(re.match(pat, name), f"{tag} reconocería {name} con {pat}")

    def test_core_uses_the_current_prefix(self):
        with open(os.path.join(ROOT, "core.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn(f'^{CURRENT_PREFIX}v[\\d.]+\\.zip$', src)

    def test_build_uses_the_current_prefix(self):
        with open(os.path.join(ROOT, "tools", "build_release_zip.py"), encoding="utf-8") as f:
            self.assertIn(f"{CURRENT_PREFIX}v{{version}}.zip", f.read())

    def test_detects_the_historical_failures(self):
        # Comprobación de la propia prueba: contra v1.2.1 y v1.2.2 el paquete actual NO cabe
        for tag, culprit in (("v1.2.1", "sigverify.py"), ("v1.2.2", "downloads.py")):
            allow = old_allowlist(tag)
            if allow is None:
                self.skipTest(f"No hay git o falta la etiqueta {tag}")
            root_files, _ = allow
            self.assertNotIn(culprit, root_files)
            self.assertIn(culprit, current_package_members())


if __name__ == "__main__":
    unittest.main()
