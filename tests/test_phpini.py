"""Pruebas del ajuste de php.ini. Ejecutar: python -m unittest discover -s tests -v"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import phpini

SAMPLE = """[PHP]
memory_limit = 512M

[opcache]
zend_extension=opcache
opcache.enable=1
opcache.memory_consumption=128
opcache.interned_strings_buffer=8
opcache.max_accelerated_files=10000
opcache.revalidate_freq=0
opcache.validate_timestamps=1
"""


def value(text, key):
    m = re.search(r"(?m)^\s*%s\s*=\s*(.*)$" % re.escape(key), text)
    return m.group(1).strip() if m else None


class TuneTests(unittest.TestCase):
    def test_replaces_existing_values(self):
        out = phpini.tune_php_ini(SAMPLE)
        self.assertEqual(value(out, "opcache.memory_consumption"), "256")
        self.assertEqual(value(out, "opcache.max_accelerated_files"), "50000")
        self.assertEqual(value(out, "opcache.revalidate_freq"), "2")
        self.assertEqual(out.count("opcache.max_accelerated_files"), 1)  # no se duplica

    def test_leaves_unrelated_settings_alone(self):
        out = phpini.tune_php_ini(SAMPLE)
        self.assertEqual(value(out, "memory_limit"), "512M")
        self.assertEqual(value(out, "opcache.enable"), "1")
        self.assertIn("zend_extension=opcache", out)

    def test_adds_missing_keys_in_one_marked_block(self):
        out = phpini.tune_php_ini(SAMPLE)
        self.assertEqual(value(out, "realpath_cache_size"), "4096K")
        self.assertEqual(value(out, "realpath_cache_ttl"), "600")
        self.assertEqual(out.count(phpini.MARKER), 1)

    def test_is_idempotent(self):
        once = phpini.tune_php_ini(SAMPLE)
        self.assertEqual(phpini.tune_php_ini(once), once)
        self.assertEqual(phpini.tune_php_ini(phpini.tune_php_ini(once)), once)

    def test_ignores_commented_lines_and_activates_the_value(self):
        out = phpini.tune_php_ini(";opcache.memory_consumption=128\n")
        self.assertEqual(value(out, "opcache.memory_consumption"), "256")
        self.assertIn(";opcache.memory_consumption=128", out)  # el comentario original se respeta

    def test_every_value_is_sane_for_many_sites(self):
        self.assertGreaterEqual(int(phpini.TUNING["opcache.max_accelerated_files"]), 30000)
        self.assertGreaterEqual(int(phpini.TUNING["opcache.memory_consumption"]), 192)


if __name__ == "__main__":
    unittest.main()
