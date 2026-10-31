import unittest

from emulator.commands.cd import run
from emulator.errors import CommandError

from .fixtures import make_ctx


class CdTest(unittest.TestCase):
    # ── setup ──────────────────────────────────────────────────────────

    def setUp(self):
        self.ctx = make_ctx()

    # ── valid paths ────────────────────────────────────────────────────

    def test_absolute(self):
        self.assertIsNone(run(["/etc"], self.ctx))
        self.assertEqual(self.ctx.cwd, "/etc")

    def test_relative(self):
        run(["/home"], self.ctx)
        run(["user"], self.ctx)
        self.assertEqual(self.ctx.cwd, "/home/user")

    def test_dotdot(self):
        run(["/home/user"], self.ctx)
        run([".."], self.ctx)
        self.assertEqual(self.ctx.cwd, "/home")

    def test_no_args_goes_to_root(self):
        run(["/etc"], self.ctx)
        run([], self.ctx)
        self.assertEqual(self.ctx.cwd, "/")

    def test_updates_prompt(self):
        run(["/etc"], self.ctx)
        self.assertEqual(self.ctx.prompt(), "vfs:/etc$ ")

    # ── errors ─────────────────────────────────────────────────────────

    def test_missing_directory(self):
        with self.assertRaises(CommandError) as cm:
            run(["nope"], self.ctx)
        self.assertEqual(str(cm.exception),
                         "cd: nope: No such file or directory")
        self.assertEqual(self.ctx.cwd, "/")

    def test_file_is_not_a_directory(self):
        with self.assertRaises(CommandError) as cm:
            run(["/etc/hosts"], self.ctx)
        self.assertEqual(str(cm.exception),
                         "cd: /etc/hosts: Not a directory")
        self.assertEqual(self.ctx.cwd, "/")

    def test_too_many_arguments(self):
        with self.assertRaises(CommandError) as cm:
            run(["a", "b", "c"], self.ctx)
        self.assertEqual(str(cm.exception), "cd: too many arguments")


if __name__ == "__main__":
    unittest.main()
