"""Pruebas de las validaciones de seguridad de core (carpeta de proyectos, state.json, nombres)."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402


class ProjectsDirTests(unittest.TestCase):
    def test_rejects_drive_root_profile_and_aetherstack_ancestors(self):
        self.assertFalse(core.is_safe_projects_dir(os.path.abspath(os.sep)))
        self.assertFalse(core.is_safe_projects_dir(os.environ["USERPROFILE"]))
        self.assertFalse(core.is_safe_projects_dir(core.BASE_DIR))
        self.assertFalse(core.is_safe_projects_dir(os.path.dirname(core.BASE_DIR)))

    def test_accepts_an_ordinary_folder(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(core.is_safe_projects_dir(d))

    def test_rejects_missing_folder(self):
        self.assertFalse(core.is_safe_projects_dir(os.path.join(core.BASE_DIR, "no-existe-xyz")))


class StateSanitizeTests(unittest.TestCase):
    def test_invalid_values_fall_back_to_defaults(self):
        conf = dict(core.DEFAULT_CONFIG, nginx_port="80; deny all", mariadb_port=0, php_workers=99,
                    vhost_tld="a;b")
        out = core._sanitize_state(conf)
        self.assertEqual(out["nginx_port"], core.DEFAULT_CONFIG["nginx_port"])
        self.assertEqual(out["mariadb_port"], core.DEFAULT_CONFIG["mariadb_port"])
        self.assertEqual(out["php_workers"], core.DEFAULT_CONFIG["php_workers"])
        self.assertRegex(out["vhost_tld"], r"^[a-z]{2,10}$")

    def test_valid_values_are_kept(self):
        conf = dict(core.DEFAULT_CONFIG, nginx_port=8080, vhost_tld="test")
        out = core._sanitize_state(conf)
        self.assertEqual(out["nginx_port"], 8080)
        self.assertEqual(out["vhost_tld"], "test")


class ProjectNameTests(unittest.TestCase):
    def test_trailing_newline_is_rejected(self):
        self.assertFalse(core.is_valid_project_name("sitio\n"))
        self.assertTrue(core.is_valid_project_name("mi-sitio"))


class DefaultIndexTests(unittest.TestCase):
    def _run_in_temp_root(self, setup_fn):
        orig = core.get_projects_root
        with tempfile.TemporaryDirectory() as d:
            core.get_projects_root = lambda: d
            try:
                setup_fn(d)
                core.write_default_index()
                out = {}
                for name in os.listdir(d):
                    path = os.path.join(d, name)
                    if os.path.isfile(path):
                        with open(path, encoding="utf-8") as f:
                            out[name] = f.read()
                return out
            finally:
                core.get_projects_root = orig

    def _write_file(self, path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def test_writes_default_index_php_in_empty_dir(self):
        files = self._run_in_temp_root(lambda d: None)
        self.assertIn("index.php", files)
        self.assertIn(core.DEFAULT_INDEX_MARKER, files["index.php"])

    def test_preserves_custom_index_php_and_html(self):
        files_php = self._run_in_temp_root(
            lambda d: self._write_file(os.path.join(d, "index.php"), "<?php echo 'custom';")
        )
        self.assertEqual(files_php["index.php"], "<?php echo 'custom';")

        files_html = self._run_in_temp_root(
            lambda d: self._write_file(os.path.join(d, "index.html"), "<h1>custom</h1>")
        )
        self.assertNotIn("index.php", files_html)
        self.assertEqual(files_html["index.html"], "<h1>custom</h1>")

    def test_migrates_old_marked_index_html_to_index_php(self):
        files = self._run_in_temp_root(
            lambda d: self._write_file(
                os.path.join(d, "index.html"),
                f"<!-- {core.DEFAULT_INDEX_MARKER} -->\n<html></html>",
            )
        )
        self.assertNotIn("index.html", files)
        self.assertIn("index.php", files)


if __name__ == "__main__":
    unittest.main()
