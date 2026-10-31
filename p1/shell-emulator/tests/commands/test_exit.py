import unittest

from emulator.commands.exit import run
from emulator.errors import CommandError, ExitShell

from .fixtures import make_ctx


class ExitTest(unittest.TestCase):
    # ── setup ──────────────────────────────────────────────────────────

    def setUp(self):
        self.ctx = make_ctx()

    # ── valid codes ────────────────────────────────────────────────────

    def test_default_code(self):
        with self.assertRaises(ExitShell) as cm:
            run([], self.ctx)
        self.assertEqual(cm.exception.code, 0)

    def test_with_code(self):
        with self.assertRaises(ExitShell) as cm:
            run(["3"], self.ctx)
        self.assertEqual(cm.exception.code, 3)

    # ── errors ─────────────────────────────────────────────────────────

    def test_not_numeric(self):
        with self.assertRaises(CommandError) as cm:
            run(["abc"], self.ctx)
        self.assertEqual(str(cm.exception),
                         "exit: abc: numeric argument required")

    def test_too_many_arguments(self):
        with self.assertRaises(CommandError) as cm:
            run(["1", "2"], self.ctx)
        self.assertEqual(str(cm.exception), "exit: too many arguments")


if __name__ == "__main__":
    unittest.main()
