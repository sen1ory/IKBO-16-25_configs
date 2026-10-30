import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class VfsSamplesTest(unittest.TestCase):
    # ── helpers ────────────────────────────────────────────────────────

    def run_emulator(self, *args):
        """Run the emulator with `exit 0` on stdin. Returns (code, output)."""
        proc = subprocess.run(
            [sys.executable, "-m", "emulator", *args],
            input="exit 0\n",
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=10,
        )
        return proc.returncode, proc.stdout + proc.stderr

    def vfs(self, name):
        return os.path.join("vfs", name)

    # ── good files ─────────────────────────────────────────────────────

    def test_no_vfs_path_uses_default_prompt(self):
        code, out = self.run_emulator()
        self.assertEqual(code, 0)
        self.assertIn("vfs:/$ ", out)

    def test_minimal_loads(self):
        code, out = self.run_emulator("--vfs-path", self.vfs("minimal.json"))
        self.assertEqual(code, 0)
        self.assertIn("minimal:/$ ", out)

    def test_multi_file_loads(self):
        code, out = self.run_emulator(
            "--vfs-path", self.vfs("multi_file.json")
        )
        self.assertEqual(code, 0)
        self.assertIn("multi:/$ ", out)

    def test_deep_loads(self):
        code, out = self.run_emulator("--vfs-path", self.vfs("deep.json"))
        self.assertEqual(code, 0)
        self.assertIn("deep:/$ ", out)

    # ── error cases ────────────────────────────────────────────────────

    def test_missing_file(self):
        code, out = self.run_emulator(
            "--vfs-path", self.vfs("does_not_exist.json")
        )
        self.assertEqual(code, 1)
        self.assertIn("vfs file not found", out)

    def test_broken_syntax(self):
        code, out = self.run_emulator(
            "--vfs-path", self.vfs("broken_syntax.json")
        )
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", out)

    def test_broken_schema(self):
        code, out = self.run_emulator(
            "--vfs-path", self.vfs("broken_schema.json")
        )
        self.assertEqual(code, 1)
        self.assertIn("unknown type 'link'", out)

    def test_broken_base64(self):
        code, out = self.run_emulator(
            "--vfs-path", self.vfs("broken_base64.json")
        )
        self.assertEqual(code, 1)
        self.assertIn("invalid base64", out)


if __name__ == "__main__":
    unittest.main()
