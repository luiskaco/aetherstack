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


if __name__ == "__main__":
    unittest.main()
