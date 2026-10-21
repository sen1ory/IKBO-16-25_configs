import unittest

from emulator.commands import dispatch
from emulator.errors import CommandError, ExitShell
from emulator.repl import Context


class DispatchTest(unittest.TestCase):
    def setUp(self):
        self.ctx = Context()

    # ── generic ──────────────────────────────────────────────────────────
    def test_prompt(self):
        self.assertEqual(self.ctx.prompt(),
                         "vfs:/$ ")

    def test_unknown_command(self):
        with self.assertRaises(CommandError) as cm:
            dispatch(["foo"], self.ctx)
        self.assertEqual(str(cm.exception),
                         "foo: command not found")

    # ── ls ───────────────────────────────────────────────────────────────
    def test_ls_stub(self):
        self.assertEqual(dispatch(["ls", "-l", "/tmp"], self.ctx),
                         "ls ['-l', '/tmp']")

    def test_ls_no_args(self):
        self.assertEqual(dispatch(["ls"], self.ctx),
                         "ls []")

    # ── cd ───────────────────────────────────────────────────────────────
    def test_cd_stub(self):
        self.assertEqual(dispatch(["cd", "/etc"], self.ctx),
                         "cd ['/etc']")

    def test_cd_too_many_arguments(self):
        with self.assertRaises(CommandError) as cm:
            dispatch(["cd", "a", "b", "c"], self.ctx)
        self.assertEqual(str(cm.exception),
                         "cd: too many arguments")

    # ── exit ─────────────────────────────────────────────────────────────
    def test_exit_default_code(self):
        with self.assertRaises(ExitShell) as cm:
            dispatch(["exit"], self.ctx)
        self.assertEqual(cm.exception.code, 0)

    def test_exit_with_code(self):
        with self.assertRaises(ExitShell) as cm:
            dispatch(["exit", "3"], self.ctx)
        self.assertEqual(cm.exception.code, 3)

    def test_exit_bad_argument(self):
        with self.assertRaises(CommandError):
            dispatch(["exit", "abc"], self.ctx)
        with self.assertRaises(CommandError):
            dispatch(["exit", "1", "2"], self.ctx)


if __name__ == "__main__":
    unittest.main()
