import contextlib
import io
import os
import tempfile
import textwrap
import unittest

from emulator.script import run_script
from tests.commands.fixtures import make_ctx


def normalize_triple(string):
    dedented = textwrap.dedent(string)
    no_leading_newline = dedented.removeprefix("\n")
    result = no_leading_newline

    return result


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
        code, out = self.run_and_capture(normalize_triple("""
                                         ls /etc
                                         """))
        self.assertIsNone(code)
        self.assertEqual(out,
                         normalize_triple("""
                         vfs:/$ ls /etc
                         hosts
                         """))

    # ── comments ───────────────────────────────────────────────────────

    def test_skips_blank_lines_and_comments(self):
        code, out = self.run_and_capture(normalize_triple("""
                                         # comment

                                         ls /etc
                                         """))
        self.assertIsNone(code)
        self.assertEqual(
            out,
            normalize_triple("""
            vfs:/$ ls /etc
            hosts
            """))

    # ── errors ─────────────────────────────────────────────────────────

    def test_stops_at_first_error(self):
        code, out = self.run_and_capture(normalize_triple("""
                                         ls /etc
                                         foo
                                         ls /home
                                         """))
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
        self.assertEqual(out.getvalue(),
                         normalize_triple("""
                         vfs:/$ ls /etc
                         hosts
                         """))

    # ── exit ───────────────────────────────────────────────────────────

    def test_exit_returns_code(self):
        code, out = self.run_and_capture(normalize_triple("""
                                         ls /etc
                                         exit 4
                                         ls /home
                                         """))
        self.assertEqual(code, 4)
        self.assertEqual(out.count("hosts"), 1)
        self.assertNotIn("user", out)


if __name__ == "__main__":
    unittest.main()
