"""Pruebas de las descargas verificadas. Ejecutar: python -m unittest discover -s tests -v"""
import hashlib
import io
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import downloads

URL = "https://example.org/latest.zip"
HASH_URL = URL + ".sha1"


def make_zip_bytes(marker="v1"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("wordpress/index.php", marker)
    return buf.getvalue()


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class FakeNet:
    """Opener falso: responde según la URL y cuenta cuántas veces se descargó el zip."""

    def __init__(self, routes):
        self.routes = routes
        self.zip_downloads = 0

    def __call__(self, req, timeout=None):
        body = self.routes.get(req.full_url)
        if isinstance(body, Exception):
            raise body
        if body is None:
            raise OSError("sin red")
        if req.full_url == URL:
            self.zip_downloads += 1
        return FakeResponse(body)


def sha1_line(data):
    return (hashlib.sha1(data).hexdigest() + "  latest.zip\n").encode()


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dest = os.path.join(self.tmp.name, "downloads", "wp.zip")

    def tearDown(self):
        self.tmp.cleanup()

    def ensure(self, net, **kw):
        return downloads.ensure_verified_zip(URL, HASH_URL, self.dest, opener=net, **kw)

    def test_downloads_verifies_and_leaves_no_part_file(self):
        data = make_zip_bytes()
        net = FakeNet({URL: data, HASH_URL: sha1_line(data)})
        self.assertEqual(self.ensure(net), self.dest)
        self.assertTrue(downloads.zip_ok(self.dest))
        self.assertFalse(os.path.exists(self.dest + ".part"))

    def test_rejects_hash_mismatch_and_keeps_nothing(self):
        net = FakeNet({URL: make_zip_bytes("malo"), HASH_URL: sha1_line(make_zip_bytes("bueno"))})
        with self.assertRaises(downloads.DownloadError):
            self.ensure(net)
        self.assertFalse(os.path.exists(self.dest))
        self.assertFalse(os.path.exists(self.dest + ".part"))

    def test_reuses_cached_copy_when_hash_matches(self):
        data = make_zip_bytes()
        net = FakeNet({URL: data, HASH_URL: sha1_line(data)})
        self.ensure(net)
        self.ensure(net)
        self.assertEqual(net.zip_downloads, 1)

    def test_redownloads_when_official_hash_changed(self):
        old, new = make_zip_bytes("v1"), make_zip_bytes("v2")
        self.ensure(FakeNet({URL: old, HASH_URL: sha1_line(old)}))
        net = FakeNet({URL: new, HASH_URL: sha1_line(new)})
        self.ensure(net)
        self.assertEqual(net.zip_downloads, 1)
        with zipfile.ZipFile(self.dest) as z:
            self.assertEqual(z.read("wordpress/index.php"), b"v2")

    def test_replaces_corrupt_cached_file(self):
        os.makedirs(os.path.dirname(self.dest))
        with open(self.dest, "wb") as f:
            f.write(b"zip cortado a la mitad")
        data = make_zip_bytes()
        self.ensure(FakeNet({URL: data, HASH_URL: sha1_line(data)}))
        self.assertTrue(downloads.zip_ok(self.dest))

    def test_offline_uses_intact_cache(self):
        data = make_zip_bytes()
        self.ensure(FakeNet({URL: data, HASH_URL: sha1_line(data)}))
        self.assertEqual(self.ensure(FakeNet({})), self.dest)

    def test_offline_without_cache_fails_clearly(self):
        with self.assertRaises(downloads.DownloadError):
            self.ensure(FakeNet({}))

    def test_offline_with_corrupt_cache_fails(self):
        os.makedirs(os.path.dirname(self.dest))
        with open(self.dest, "wb") as f:
            f.write(b"corrupto")
        with self.assertRaises(downloads.DownloadError):
            self.ensure(FakeNet({}))

    def test_rejects_non_https(self):
        with self.assertRaises(downloads.DownloadError):
            downloads.ensure_verified_zip("http://example.org/x.zip", "http://example.org/x.zip.sha1",
                                          self.dest, opener=FakeNet({}))

    def test_enforces_size_limit(self):
        data = make_zip_bytes()
        net = FakeNet({URL: data, HASH_URL: sha1_line(data)})
        with self.assertRaises(downloads.DownloadError):
            self.ensure(net, limit=10)
        self.assertFalse(os.path.exists(self.dest))

    def test_parse_hash(self):
        self.assertEqual(downloads.parse_hash("A" * 40 + "  file", "sha1"), "a" * 40)
        self.assertIsNone(downloads.parse_hash("no es un hash", "sha1"))
        self.assertIsNone(downloads.parse_hash("a" * 39, "sha1"))


if __name__ == "__main__":
    unittest.main()
