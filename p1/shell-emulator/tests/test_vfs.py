import unittest
from datetime import datetime

from emulator.errors import VFSError
from emulator.vfs import DirNode, FileNode, VFS

TIME = datetime(2024, 1, 1)


def d(name, children=None):
    return DirNode(name, "root", "root", "rwxr-xr-x", TIME, children)


def f(name, content=""):
    return FileNode(name, "root", "root", "rw-r--r--", TIME, content)


class VFSTest(unittest.TestCase):
    # ── setup ──────────────────────────────────────────────────────────

    def setUp(self):
        # /etc
        self.etc = d("etc", {"hosts": f("hosts", "127.0.0.1 localhost")})
        # /home/user/notes.txt with hi inside
        self.notes = f("notes.txt", "hi")
        self.user = d("user", {"notes.txt": self.notes})
        self.home = d("home", {"user": self.user})
        # /{etc,home}
        self.root = d("", {"etc": self.etc, "home": self.home})
        # wire up demo with / as root
        self.vfs = VFS("demo", self.root)

    # ── normalize ──────────────────────────────────────────────────────

    def test_normalize_relative_with_dots(self):
        self.assertEqual(
            self.vfs.normalize("/home", "./user/../user/"),
            "/home/user",
        )

    def test_normalize_dotdot_at_root_stays_root(self):
        self.assertEqual(self.vfs.normalize("/", ".."), "/")

    # ── resolve: valid paths ───────────────────────────────────────────

    def test_resolve_root(self):
        self.assertIs(self.vfs.resolve("/", "/"), self.root)

    def test_resolve_absolute(self):
        self.assertEqual(self.vfs.resolve("/", "/etc/hosts").name, "hosts")

    def test_resolve_relative(self):
        self.assertIs(self.vfs.resolve("/home", "user/notes.txt"), self.notes)

    def test_resolve_dotdot(self):
        self.assertIs(self.vfs.resolve("/home/user", "../../etc"), self.etc)

    def test_resolve_dot(self):
        self.assertIs(self.vfs.resolve("/etc", "."), self.etc)

    def test_resolve_trailing_slash_on_directory(self):
        self.assertIs(self.vfs.resolve("/", "/etc/"), self.etc)

    # ── resolve: errors ────────────────────────────────────────────────

    def test_missing_path(self):
        with self.assertRaises(VFSError) as cm:
            self.vfs.resolve("/", "/nope")
        self.assertEqual(str(cm.exception), "No such file or directory")

    def test_missing_path_below_missing_dir(self):
        with self.assertRaises(VFSError) as cm:
            self.vfs.resolve("/", "/nope/x")
        self.assertEqual(str(cm.exception), "No such file or directory")

    def test_file_used_as_directory(self):
        with self.assertRaises(VFSError) as cm:
            self.vfs.resolve("/", "/etc/hosts/x")
        self.assertEqual(str(cm.exception), "Not a directory")

    def test_trailing_slash_on_file(self):
        with self.assertRaises(VFSError) as cm:
            self.vfs.resolve("/", "/etc/hosts/")
        self.assertEqual(str(cm.exception), "Not a directory")


if __name__ == "__main__":
    unittest.main()
