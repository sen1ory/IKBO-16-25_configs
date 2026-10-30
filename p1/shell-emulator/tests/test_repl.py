import contextlib
import io
import json
import os
import tempfile
import unittest

from emulator.__main__ import main
from emulator.repl import Context


class ContextTest(unittest.TestCase):
    # ── default state ──────────────────────────────────────────────────

    def test_default_vfs_is_empty_root(self):
        ctx = Context()
        self.assertEqual(ctx.vfs.name, "vfs")
        self.assertEqual(ctx.vfs.root.children, {})

    def test_prompt_uses_vfs_name(self):
        ctx = Context()
        self.assertEqual(ctx.prompt(), "vfs:/$ ")


class MainVfsPathTest(unittest.TestCase):
    # ── setup ──────────────────────────────────────────────────────────

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    # ── helpers ────────────────────────────────────────────────────────

    def run_main(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(argv)
        return code, out.getvalue()

    # ── tests ──────────────────────────────────────────────────────────

    def test_missing_vfs_file_exits_with_error(self):
        path = os.path.join(self.tmp.name, "nope.json")
        code, out = self.run_main(["--vfs-path", path, "--startup-script",
                                   os.devnull])
        self.assertEqual(code, 1)
        self.assertIn("emulator: vfs file not found", out)


if __name__ == "__main__":
    unittest.main()
