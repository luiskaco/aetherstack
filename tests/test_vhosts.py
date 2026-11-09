"""Pruebas de la generación de virtual hosts. Ejecutar: python -m unittest discover -s tests -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import vhosts


class VhostTests(unittest.TestCase):
    def test_tld_normalization(self):
        self.assertEqual(vhosts.normalize_tld("test"), "test")
        self.assertEqual(vhosts.normalize_tld(".TEST "), "test")
        for bad in ("", None, "a", "x" * 11, "te st", "te.st", "123", "../x", "test;rm"):
            self.assertEqual(vhosts.normalize_tld(bad), vhosts.DEFAULT_TLD, repr(bad))

    def test_domain_for(self):
        self.assertEqual(vhosts.domain_for("frutiflex", "test"), "frutiflex.test")
        self.assertEqual(vhosts.domain_for("orangeIA", None), "orangeIA.local")

    def test_render_uses_domain_port_and_root(self):
        text = vhosts.render_vhost("frutiflex", "C:/www/frutiflex", 80, "C:/bin/fastcgi_params", "test")
        self.assertIn("server_name frutiflex.test;", text)
        self.assertIn("listen 127.0.0.1:80;", text)
        self.assertIn('root "C:/www/frutiflex";', text)
        self.assertIn('include "C:/bin/fastcgi_params";', text)

    def test_render_listens_only_on_loopback_and_blocks_dotfiles(self):
        text = vhosts.render_vhost("x", "C:/www/x", 8080, "C:/f", "local")
        self.assertNotIn("listen 80;", text)
        self.assertIn("listen 127.0.0.1:8080;", text)
        self.assertIn("location ~ /\\. {", text)
        self.assertIn("deny all;", text)

    def test_render_has_balanced_braces(self):
        text = vhosts.render_vhost("x", "C:/www/x", 80, "C:/f", "test")
        self.assertEqual(text.count("{"), text.count("}"))


class NginxTemplateTests(unittest.TestCase):
    def test_master_config_allows_many_server_names(self):
        # Sin esto Nginx falla con "could not build server_names_hash" al tener muchos proyectos
        with open(os.path.join(os.path.dirname(__file__), "..", "core.py"), encoding="utf-8") as f:
            self.assertRegex(f.read(), r"server_names_hash_bucket_size\s+(64|128|256);")


if __name__ == "__main__":
    unittest.main()
