"""Pruebas del actualizador. Ejecutar: python -m unittest discover -s tests -v"""
import hashlib
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import updater


def make_zip(path, files, root="aetherstack"):
    with zipfile.ZipFile(path, "w") as z:
        for name, data in files.items():
            z.writestr(f"{root}/{name}" if root else name, data)
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


GOOD = {"app.py": "V = 2\n", "core.py": "VERSION = '2'\n", "updater.py": "X = 1\n", "docs/a.md": "nuevo"}


class UpdaterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = os.path.join(self.tmp.name, "install")
        os.makedirs(os.path.join(self.base, "docs"))
        os.makedirs(os.path.join(self.base, "data"))
        for name, text in {"app.py": "V = 1\n", "core.py": "VERSION = '1'\n",
                           "data/keep.txt": "datos del usuario"}.items():
            with open(os.path.join(self.base, name), "w") as f:
                f.write(text)
        self.zip = os.path.join(self.tmp.name, "code.zip")
        self._orig = updater.BASE_DIR
        updater.BASE_DIR = self.base

    def tearDown(self):
        updater.BASE_DIR = self._orig
        self.tmp.cleanup()

    def read(self, rel):
        with open(os.path.join(self.base, rel)) as f:
            return f.read()

    def test_applies_update_and_keeps_user_data(self):
        h = make_zip(self.zip, {**GOOD, "data/keep.txt": "pisado", "bin/x.exe": "no"})
        changed = updater.apply_update_from_files(self.zip, h)
        self.assertEqual(self.read("app.py"), "V = 2\n")
        self.assertEqual(self.read("docs/a.md"), "nuevo")
        self.assertEqual(self.read("data/keep.txt"), "datos del usuario")
        self.assertFalse(os.path.exists(os.path.join(self.base, "bin")))
        self.assertNotIn("data/keep.txt", changed)
        self.assertEqual(open(os.path.join(self.base, ".update-backup", "app.py")).read(), "V = 1\n")

    def test_rejects_wrong_hash(self):
        make_zip(self.zip, GOOD)
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, "0" * 64)
        self.assertEqual(self.read("app.py"), "V = 1\n")

    def test_rejects_path_traversal(self):
        h = make_zip(self.zip, {**GOOD, "docs/../../evil.py": "x = 1"})
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, h)
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "evil.py")))
        self.assertEqual(self.read("app.py"), "V = 1\n")

    def test_rejects_syntax_error_without_touching_install(self):
        h = make_zip(self.zip, {**GOOD, "app.py": "def broken(:\n"})
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, h)
        self.assertEqual(self.read("app.py"), "V = 1\n")
        self.assertEqual(self.read("core.py"), "VERSION = '1'\n")

    def test_rejects_incomplete_package(self):
        h = make_zip(self.zip, {"app.py": "V = 2\n"})
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, h)

    def test_rollback_when_write_fails(self):
        h = make_zip(self.zip, GOOD)
        # Un archivo donde debería haber una carpeta hace fallar la escritura de docs/a.md
        os.rmdir(os.path.join(self.base, "docs"))
        with open(os.path.join(self.base, "docs"), "w") as f:
            f.write("soy un archivo")
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, h)
        self.assertEqual(self.read("app.py"), "V = 1\n")
        self.assertEqual(self.read("core.py"), "VERSION = '1'\n")
        self.assertFalse(os.path.exists(os.path.join(self.base, "updater.py")))

    def test_rejects_foreign_urls(self):
        with self.assertRaises(updater.UpdateError):
            updater.download_and_apply("https://evil.example/code.zip", "https://evil.example/code.zip.sha256")

    def test_allowed_paths(self):
        self.assertTrue(updater.is_allowed_path("ui/web/dashboard.html"))
        self.assertTrue(updater.is_allowed_path("core.py"))
        for bad in ("bin/php/php.exe", "data/mariadb/x", "conf/state.json", "projects/a", "logs/x.log"):
            self.assertFalse(updater.is_allowed_path(bad), bad)


if __name__ == "__main__":
    unittest.main()
