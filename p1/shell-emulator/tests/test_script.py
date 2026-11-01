import contextlib
import io
import os
import tempfile
import unittest

from emulator.script import run_script
from tests.commands.fixtures import make_ctx


class ScriptTest(unittest.TestCase):
    # ── setup ──────────────────────────────────────────────────────────

    def setUp(self):
        self.ctx = make_ctx()
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    # ── helpers ────────────────────────────────────────────────────────

    def write_script(self, text):
        path = os.path.join(self.tmp.name, "test.emu")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def run_and_capture(self, text):
        path = self.write_script(text)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = run_script(path, self.ctx)
        return code, out.getvalue()

    # ── output ─────────────────────────────────────────────────────────

    def test_echoes_prompt_and_output(self):
        code, out = self.run_and_capture("ls /etc\n")
        self.assertIsNone(code)
        self.assertEqual(
            out,
            "vfs:/$ ls /etc\n"
            "hosts\n",
        )

    # ── comments ───────────────────────────────────────────────────────

    def test_skips_blank_lines_and_comments(self):
        code, out = self.run_and_capture("# comment\n\n   \nls /etc\n")
        self.assertIsNone(code)
        self.assertEqual(out, "vfs:/$ ls /etc\nhosts\n")

    # ── errors ─────────────────────────────────────────────────────────

    def test_stops_at_first_error(self):
        code, out = self.run_and_capture("ls /etc\nfoo\nls /home\n")
        self.assertEqual(code, 1)
        self.assertIn(
            "Script error at line 2: foo: command not found",
            out,
        )
        self.assertNotIn("user", out)

    # ── encoding ───────────────────────────────────────────────────────

    def test_strips_utf8_bom(self):
        path = os.path.join(self.tmp.name, "bom.emu")
        with open(path, "wb") as f:
            f.write(b"\xef\xbb\xbfls /etc\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = run_script(path, self.ctx)
        self.assertIsNone(code)
        self.assertEqual(out.getvalue(), "vfs:/$ ls /etc\nhosts\n")

    # ── exit ───────────────────────────────────────────────────────────

    def test_exit_returns_code(self):
        code, out = self.run_and_capture("ls /etc\nexit 4\nls /home\n")
        self.assertEqual(code, 4)
        self.assertEqual(out.count("hosts"), 1)
        self.assertNotIn("user", out)


if __name__ == "__main__":
    unittest.main()
