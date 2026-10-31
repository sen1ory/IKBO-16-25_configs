import unittest

from emulator.commands import dispatch
from emulator.errors import CommandError
from emulator.repl import Context


class DispatchTest(unittest.TestCase):
    # ── setup ──────────────────────────────────────────────────────────

    def setUp(self):
        self.ctx = Context()

    # ── generic ────────────────────────────────────────────────────────

    def test_prompt(self):
        self.assertEqual(self.ctx.prompt(), "vfs:/$ ")

    def test_unknown_command(self):
        with self.assertRaises(CommandError) as cm:
            dispatch(["foo"], self.ctx)
        self.assertEqual(str(cm.exception), "foo: command not found")


if __name__ == "__main__":
    unittest.main()
