import unittest

from emulator.commands.ls import run
from emulator.errors import CommandError

from .fixtures import make_ctx


class LsTest(unittest.TestCase):
    # ── setup ──────────────────────────────────────────────────────────

    def setUp(self):
        self.ctx = make_ctx()

    # ── names only ─────────────────────────────────────────────────────

    def test_no_args_lists_cwd(self):
        self.assertEqual(run([], self.ctx), "etc\nhome\nreadme.txt\ntmp")

    def test_no_args_uses_cwd(self):
        self.ctx.cwd = "/home/user"
        self.assertEqual(run([], self.ctx), "logo.png\nnotes.txt")

    def test_directory_argument(self):
        self.assertEqual(run(["/etc"], self.ctx), "hosts")

    def test_relative_argument(self):
        self.ctx.cwd = "/home"
        self.assertEqual(run(["user"], self.ctx), "logo.png\nnotes.txt")

    def test_file_argument_shows_its_name(self):
        self.assertEqual(run(["/etc/hosts"], self.ctx), "/etc/hosts")

    def test_empty_directory_prints_nothing(self):
        self.assertEqual(run(["/tmp"], self.ctx), "")

    def test_several_directories_get_headings(self):
        self.assertEqual(
            run(["/etc", "/home/user"], self.ctx),
            "/etc:\nhosts\n\n/home/user:\nlogo.png\nnotes.txt",
        )

    # ── long format ────────────────────────────────────────────────────

    def test_long_file(self):
        self.assertEqual(
            run(["-l", "/etc/hosts"], self.ctx),
            "-rw-r--r-- root root     20 Jan 02 10:05 /etc/hosts",
        )

    def test_long_directory_shows_owner_mode_and_dirs(self):
        self.assertEqual(
            run(["-l", "/"], self.ctx),
            "\n".join([
                "drwxr-xr-x root root      0 Jan 01 00:00 etc",
                "drwxr-xr-x root root      0 Jan 01 00:00 home",
                "-rw-r--r-- root root      8 Jan 06 08:00 readme.txt",
                "drwxr-xr-x root root      0 Jan 01 00:00 tmp",
            ]),
        )

    def test_long_binary_file_size_is_bytes(self):
        self.assertEqual(
            run(["-l", "/home/user"], self.ctx),
            "\n".join([
                "-rw------- user user      4 Mar 05 12:00 logo.png",
                "-rw-r--r-- user user      3 Mar 04 09:30 notes.txt",
            ]),
        )

    # ── errors ─────────────────────────────────────────────────────────

    def test_missing_path(self):
        with self.assertRaises(CommandError) as cm:
            run(["/nope"], self.ctx)
        self.assertEqual(str(cm.exception),
                         "ls: /nope: No such file or directory")

    def test_file_used_as_directory(self):
        with self.assertRaises(CommandError) as cm:
            run(["/etc/hosts/x"], self.ctx)
        self.assertEqual(str(cm.exception),
                         "ls: /etc/hosts/x: Not a directory")

    def test_empty_path(self):
        with self.assertRaises(CommandError) as cm:
            run([""], self.ctx)
        self.assertEqual(str(cm.exception),
                         "ls: '': No such file or directory")

    def test_invalid_option(self):
        with self.assertRaises(CommandError) as cm:
            run(["-a"], self.ctx)
        self.assertEqual(str(cm.exception), "ls: invalid option -- 'a'")


if __name__ == "__main__":
    unittest.main()
