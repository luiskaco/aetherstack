"""Pruebas del bloque de hosts. No tocan el hosts real. Ejecutar: python -m unittest discover -s tests -v"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import hosts

ORIGINAL = (
    "# Copyright (c) 1993-2009 Microsoft Corp.\r\n"
    "#\r\n"
    "127.0.0.1       localhost\r\n"
    "127.0.0.1       frutiflex.test       #laragon magic!\r\n"
    "\r\n"
    "192.168.1.10    servidor-oficina\r\n"
)


class CleanDomainsTests(unittest.TestCase):
    def test_keeps_valid_lowercase_unique_sorted(self):
        self.assertEqual(hosts.clean_domains(["B.test", "a.test", "a.TEST", "a.test"]), ["a.test", "b.test"])

    def test_discards_anything_that_is_not_a_hostname(self):
        bad = ["", None, "sinpunto", "a b.test", "x.test; rm", "../etc.test", "a.test #x", "-a.test", "a..test",
               "127.0.0.1 evil.test", "a.test\nb.test", "a" * 70 + ".test"]
        self.assertEqual(hosts.clean_domains(bad), [])

    def test_accepts_hyphen_and_subdomains(self):
        self.assertEqual(hosts.clean_domains(["demo-ia-panasa.test", "www.a.test"]), ["demo-ia-panasa.test", "www.a.test"])


class ApplyBlockTests(unittest.TestCase):
    def test_adds_block_and_keeps_everything_else_byte_for_byte(self):
        out = hosts.apply_block(ORIGINAL, ["a.test", "b.test"])
        self.assertTrue(out.startswith(ORIGINAL.rstrip("\r\n")))
        self.assertIn("127.0.0.1 a.test", out)
        self.assertIn("127.0.0.1 b.test", out)
        self.assertEqual(out.count(hosts.BEGIN), 1)
        self.assertEqual(out.count(hosts.END), 1)

    def test_preserves_the_line_ending_style_of_the_file(self):
        crlf = hosts.apply_block(ORIGINAL, ["a.test"])
        self.assertNotIn("\r\r", crlf)
        self.assertEqual(crlf.count("\n"), crlf.count("\r\n"))
        lf = hosts.apply_block("127.0.0.1 localhost\n", ["a.test"])
        self.assertNotIn("\r", lf)

    def test_is_idempotent(self):
        once = hosts.apply_block(ORIGINAL, ["a.test", "b.test"])
        self.assertEqual(hosts.apply_block(once, ["b.test", "a.test"]), once)

    def test_updates_replacing_the_old_block_not_stacking(self):
        first = hosts.apply_block(ORIGINAL, ["a.test", "b.test"])
        second = hosts.apply_block(first, ["c.test"])
        self.assertNotIn("a.test", second)
        self.assertIn("c.test", second)
        self.assertEqual(second.count(hosts.BEGIN), 1)

    def test_empty_domains_removes_the_block_and_restores_the_original(self):
        with_block = hosts.apply_block(ORIGINAL, ["a.test"])
        removed = hosts.apply_block(with_block, [])
        self.assertNotIn(hosts.BEGIN, removed)
        self.assertEqual(removed.rstrip("\r\n"), ORIGINAL.rstrip("\r\n"))

    def test_never_touches_lines_outside_the_block(self):
        out = hosts.apply_block(ORIGINAL, ["a.test"])
        for line in ("127.0.0.1       localhost", "frutiflex.test       #laragon magic!", "192.168.1.10    servidor-oficina"):
            self.assertIn(line, out)

    def test_current_domains_reads_back_what_was_written(self):
        out = hosts.apply_block(ORIGINAL, ["b.test", "a.test"])
        self.assertEqual(hosts.current_domains(out), ["a.test", "b.test"])
        self.assertEqual(hosts.current_domains(ORIGINAL), [])


class SyncTests(unittest.TestCase):
    def test_sync_on_a_writable_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "hosts")
            with open(path, "w", newline="") as f:
                f.write(ORIGINAL)
            backups = os.path.join(d, "conf")
            self.assertEqual(hosts.sync(["a.test"], path, backups), "updated")
            self.assertEqual(hosts.sync(["a.test"], path, backups), "unchanged")
            self.assertIn("127.0.0.1 a.test", hosts.read_hosts(path))
            # La copia de seguridad es del archivo original y no se sobrescribe después
            self.assertEqual(hosts.read_hosts(os.path.join(backups, "hosts.backup")), ORIGINAL)
            hosts.sync(["b.test"], path, backups)
            self.assertEqual(hosts.read_hosts(os.path.join(backups, "hosts.backup")), ORIGINAL)

    def test_sync_with_no_domains_leaves_a_clean_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "hosts")
            with open(path, "w", newline="") as f:
                f.write(hosts.apply_block(ORIGINAL, ["a.test"]))
            self.assertEqual(hosts.sync([], path), "updated")
            self.assertNotIn(hosts.BEGIN, hosts.read_hosts(path))


class ElevatedScriptTests(unittest.TestCase):
    def test_script_copies_the_temp_file_over_hosts_and_logs_the_result(self):
        script = hosts.elevated_copy_script(r"C:\tmp\h.txt", r"C:\Windows\System32\drivers\etc\hosts", r"C:\tmp\h.log")
        self.assertIn("Copy-Item -LiteralPath 'C:\\tmp\\h.txt' -Destination 'C:\\Windows\\System32\\drivers\\etc\\hosts' -Force", script)
        self.assertIn("'OK'", script)
        self.assertIn("ERROR: ", script)
        self.assertIn("$ErrorActionPreference='Stop'", script)

    def test_script_verifies_the_hash_before_copying(self):
        script = hosts.elevated_copy_script(r"C:	mp\h.txt", r"C:\h", r"C:	mp\h.log", "ABC123")
        self.assertIn("Get-FileHash", script)
        self.assertIn("'ABC123'", script)
        self.assertLess(script.index("Get-FileHash"), script.index("Copy-Item"))

    def test_encoded_command_roundtrips(self):
        import base64
        script = "Write-Output 'a\"b' ; $x = 1"
        self.assertEqual(base64.b64decode(hosts.encode_script(script)).decode("utf-16-le"), script)
        self.assertRegex(hosts.encode_script(script), r"^[A-Za-z0-9+/=]+$")  # sin comillas ni espacios

class WritableProbeTests(unittest.TestCase):
    def test_probe_opens_the_file_instead_of_trusting_os_access(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "hosts")
            with open(path, "w") as f:
                f.write("x")
            self.assertTrue(hosts._is_admin_writable(path))
            self.assertFalse(hosts._is_admin_writable(os.path.join(d, "no-existe")))
            before = os.path.getmtime(path)
            hosts._is_admin_writable(path)
            self.assertEqual(os.path.getmtime(path), before)  # la prueba no modifica el archivo

if __name__ == "__main__":
    unittest.main()
