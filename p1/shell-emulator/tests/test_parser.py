import os
import unittest

from emulator.errors import ParseError
from emulator.parser import parse


class ParserTest(unittest.TestCase):
    # ── generic ──────────────────────────────────────────────────────────
    def test_simple(self):
        self.assertEqual(parse("ls -l /tmp"),
                         ["ls", "-l", "/tmp"])

    def test_empty_line(self):
        self.assertEqual(parse(""), [])
        self.assertEqual(parse("   "), [])

    # ── quoting ──────────────────────────────────────────────────────────
    def test_quotes(self):
        self.assertEqual(parse('ls "a b" \'c d\''), ["ls", "a b", "c d"])

    def test_unbalanced_quotes(self):
        with self.assertRaises(ParseError):
            parse('ls "abc')
        with self.assertRaises(ParseError):
            parse("ls 'abc")

    # ── envvars ──────────────────────────────────────────────────────────
    def test_env_variable(self):
        os.environ["EMU_TEST"] = "value"
        self.assertEqual(parse("cd $EMU_TEST"), ["cd", "value"])
        self.assertEqual(parse("cd ${EMU_TEST}x"), ["cd", "valuex"])

    def test_double_quotes_expand(self):
        os.environ["EMU_TEST"] = "value"
        self.assertEqual(parse('echo "$EMU_TEST"'), ["echo", "value"])

    def test_single_quotes_do_not_expand(self):
        os.environ["EMU_TEST"] = "value"
        self.assertEqual(parse("echo '$EMU_TEST'"), ["echo", "$EMU_TEST"])

    def test_undefined_variable_is_empty(self):
        os.environ.pop("EMU_NOPE", None)
        self.assertEqual(parse("ls $EMU_NOPE"), ["ls"])
        self.assertEqual(parse('ls "a$EMU_NOPE"'), ["ls", "a"])


if __name__ == "__main__":
    unittest.main()
