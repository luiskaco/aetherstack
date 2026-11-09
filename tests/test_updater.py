"""Pruebas del actualizador y de la verificación de firmas. Ejecutar: python -m unittest discover -s tests -v"""
import base64
import hashlib
import os
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import sigverify
import sign_release
import updater

VERSION = "9.9.9"
GOOD = {"app.py": "V = 2\n", "core.py": "VERSION = '2'\n", "updater.py": "X = 1\n",
        "sigverify.py": "Y = 1\n", "downloads.py": "Z = 1\n", "docs/a.md": "nuevo"}


def make_zip(path, files, root="aetherstack"):
    with zipfile.ZipFile(path, "w") as z:
        for name, data in files.items():
            z.writestr(f"{root}/{name}" if root else name, data)


def sign_file(path, seed, version=VERSION):
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    sig = sign_release.sign(seed, updater.signing_message(version, digest))
    return base64.b64encode(sig).decode()


class SigVerifyTests(unittest.TestCase):
    # Vector 1 oficial del RFC 8032 (sección 7.1)
    SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    PUB = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
    SIG = bytes.fromhex("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b")

    def test_rfc8032_vector(self):
        self.assertEqual(sign_release.public_key_from_seed(self.SEED), self.PUB)
        self.assertEqual(sign_release.sign(self.SEED, b""), self.SIG)
        self.assertTrue(sigverify.verify(self.PUB, b"", self.SIG))

    def test_rejects_tampering(self):
        bad = bytearray(self.SIG)
        bad[10] ^= 1
        self.assertFalse(sigverify.verify(self.PUB, b"", bytes(bad)))
        self.assertFalse(sigverify.verify(self.PUB, b"otro mensaje", self.SIG))
        self.assertFalse(sigverify.verify(b"\x00" * 32, b"", self.SIG))
        self.assertFalse(sigverify.verify(self.PUB, b"", self.SIG[:-1]))
        self.assertFalse(sigverify.verify(self.PUB[:-1], b"", self.SIG))

    def test_project_public_key_is_valid_point(self):
        self.assertIsNotNone(sigverify.point_decompress(bytes.fromhex(updater.RELEASE_PUBLIC_KEY)))


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
        # Clave de pruebas: se sustituye la pública del proyecto mientras dura cada test
        self.seed = os.urandom(32)
        self._orig = (updater.BASE_DIR, updater.RELEASE_PUBLIC_KEY)
        updater.BASE_DIR = self.base
        updater.RELEASE_PUBLIC_KEY = sign_release.public_key_from_seed(self.seed).hex()

    def tearDown(self):
        updater.BASE_DIR, updater.RELEASE_PUBLIC_KEY = self._orig
        self.tmp.cleanup()

    def read(self, rel):
        with open(os.path.join(self.base, rel)) as f:
            return f.read()

    def assertUntouched(self):
        self.assertEqual(self.read("app.py"), "V = 1\n")
        self.assertEqual(self.read("core.py"), "VERSION = '1'\n")

    def test_applies_signed_update_and_keeps_user_data(self):
        make_zip(self.zip, GOOD)
        changed = updater.apply_update_from_files(self.zip, VERSION, sign_file(self.zip, self.seed))
        self.assertEqual(self.read("app.py"), "V = 2\n")
        self.assertEqual(self.read("docs/a.md"), "nuevo")
        self.assertEqual(self.read("data/keep.txt"), "datos del usuario")
        self.assertNotIn("data/keep.txt", changed)
        self.assertEqual(self.read(".update-backup/app.py"), "V = 1\n")

    def test_accepts_new_top_level_python_module(self):
        make_zip(self.zip, {**GOOD, "nuevo_modulo.py": "Q = 1\n"})
        updater.apply_update_from_files(self.zip, VERSION, sign_file(self.zip, self.seed))
        self.assertEqual(self.read("nuevo_modulo.py"), "Q = 1\n")

    def test_refuses_whole_package_if_it_has_files_this_version_cannot_install(self):
        # Instalar a medias dejaría código nuevo sin los archivos que necesita: se rechaza todo
        for extra in ("bin/x.exe", "data/keep.txt", "datos_nuevos.bin", "otra_carpeta/a.txt"):
            make_zip(self.zip, {**GOOD, extra: "x"})
            with self.assertRaises(updater.UpdateError, msg=extra):
                updater.apply_update_from_files(self.zip, VERSION, sign_file(self.zip, self.seed))
            self.assertUntouched()
            self.assertEqual(self.read("data/keep.txt"), "datos del usuario")

    def test_rejects_signature_from_another_key(self):
        make_zip(self.zip, GOOD)
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, VERSION, sign_file(self.zip, os.urandom(32)))
        self.assertUntouched()

    def test_rejects_zip_modified_after_signing(self):
        make_zip(self.zip, GOOD)
        sig = sign_file(self.zip, self.seed)
        make_zip(self.zip, {**GOOD, "app.py": "V = 'alterado'\n"})
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, VERSION, sig)
        self.assertUntouched()

    def test_rejects_old_signed_zip_replayed_as_new_version(self):
        make_zip(self.zip, GOOD)
        old_sig = sign_file(self.zip, self.seed, version="1.0.0")
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, "9.9.9", old_sig)
        self.assertUntouched()

    def test_rejects_missing_or_garbage_signature(self):
        make_zip(self.zip, GOOD)
        for bad in ("", "no-es-base64!!", base64.b64encode(b"corta").decode()):
            with self.assertRaises(updater.UpdateError):
                updater.apply_update_from_files(self.zip, VERSION, bad)
        self.assertUntouched()

    def test_rejects_path_traversal_even_if_signed(self):
        make_zip(self.zip, {**GOOD, "docs/../../evil.py": "x = 1"})
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, VERSION, sign_file(self.zip, self.seed))
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "evil.py")))
        self.assertUntouched()

    def test_rejects_syntax_error_even_if_signed(self):
        make_zip(self.zip, {**GOOD, "app.py": "def broken(:\n"})
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, VERSION, sign_file(self.zip, self.seed))
        self.assertUntouched()

    def test_rejects_incomplete_package(self):
        make_zip(self.zip, {"app.py": "V = 2\n"})
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, VERSION, sign_file(self.zip, self.seed))

    def test_rollback_when_write_fails(self):
        make_zip(self.zip, GOOD)
        # Un archivo donde debería haber una carpeta hace fallar la escritura de docs/a.md
        os.rmdir(os.path.join(self.base, "docs"))
        with open(os.path.join(self.base, "docs"), "w") as f:
            f.write("soy un archivo")
        with self.assertRaises(updater.UpdateError):
            updater.apply_update_from_files(self.zip, VERSION, sign_file(self.zip, self.seed))
        self.assertUntouched()
        self.assertFalse(os.path.exists(os.path.join(self.base, "updater.py")))

    def test_rejects_foreign_urls(self):
        with self.assertRaises(updater.UpdateError):
            updater.download_and_apply("https://evil.example/code.zip", "https://evil.example/code.zip.sig", VERSION)

    def test_allowed_paths(self):
        self.assertTrue(updater.is_allowed_path("ui/web/dashboard.html"))
        self.assertTrue(updater.is_allowed_path("sigverify.py"))
        self.assertTrue(updater.is_allowed_path("nuevo_modulo.py"))
        for bad in ("bin/php/php.exe", "data/mariadb/x", "conf/state.json", "projects/a", "logs/x.log", "tools/sign_release.py",
                    "datos.bin", "sub/modulo.py", "../evil.py"):
            self.assertFalse(updater.is_allowed_path(bad), bad)


if __name__ == "__main__":
    unittest.main()
