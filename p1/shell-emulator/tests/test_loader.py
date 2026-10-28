import base64
import json
import os
import tempfile
import unittest

from emulator.errors import VFSError
from emulator.loader import load_vfs
from emulator.vfs import DirNode, FileNode

ROOT = {
    "type": "dir",
    "owner": "root",
    "group": "root",
    "mtime": "2024-01-01T00:00:00",
    "children": {
        "readme.txt": {
            "type": "file",
            "owner": "root",
            "group": "root",
            "mtime": "2024-01-02T10:00:00",
            "encoding": "text",
            "content": "hello",
        },
        "logo.bin": {
            "type": "file",
            "owner": "user",
            "group": "user",
            "mtime": "2024-01-03T10:00:00",
            "encoding": "base64",
            "content": base64.b64encode(b"\x89PNG\r\n").decode(),
        },
    },
}


class LoaderTest(unittest.TestCase):
    # ── setup ──────────────────────────────────────────────────────────

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    # ── helpers ────────────────────────────────────────────────────────

    def write_raw(self, text):
        path = os.path.join(self.tmp.name, "vfs.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def write_json(self, data):
        return self.write_raw(json.dumps(data))

    def load_error(self, path):
        with self.assertRaises(VFSError) as cm:
            load_vfs(path)
        return str(cm.exception)

    # ── valid files ────────────────────────────────────────────────────

    def test_loads_name_and_tree(self):
        vfs = load_vfs(self.write_json({"name": "demo", "root": ROOT}))
        self.assertEqual(vfs.name, "demo")
        self.assertIsInstance(vfs.root, DirNode)
        self.assertIsInstance(vfs.root.children["readme.txt"], FileNode)

    def test_name_defaults_to_vfs(self):
        vfs = load_vfs(self.write_json({"root": ROOT}))
        self.assertEqual(vfs.name, "vfs")

    def test_text_file_is_str(self):
        vfs = load_vfs(self.write_json({"root": ROOT}))
        self.assertEqual(vfs.root.children["readme.txt"].content, "hello")

    def test_base64_file_is_bytes(self):
        vfs = load_vfs(self.write_json({"root": ROOT}))
        self.assertEqual(
            vfs.root.children["logo.bin"].content,
            b"\x89PNG\r\n",
        )

    def test_metadata_is_kept(self):
        vfs = load_vfs(self.write_json({"root": ROOT}))
        node = vfs.root.children["logo.bin"]
        self.assertEqual(node.owner, "user")
        self.assertEqual(node.group, "user")
        self.assertEqual(node.mtime.year, 2024)
        self.assertEqual(node.mtime.day, 3)

    def test_mode_defaults_when_missing(self):
        vfs = load_vfs(self.write_json({"root": ROOT}))
        self.assertEqual(vfs.root.children["readme.txt"].mode, "rw-r--r--")

    # ── file level errors ──────────────────────────────────────────────

    def test_file_not_found(self):
        msg = self.load_error(os.path.join(self.tmp.name, "nope.json"))
        self.assertIn("vfs file not found", msg)

    def test_invalid_json(self):
        msg = self.load_error(self.write_raw("{ broken"))
        self.assertIn("not valid JSON", msg)

    # ── structure errors ───────────────────────────────────────────────

    def test_missing_root(self):
        msg = self.load_error(self.write_json({"name": "demo"}))
        self.assertIn("missing 'root'", msg)

    def test_root_must_be_dir(self):
        bad = dict(ROOT, type="file", encoding="text", content="x")
        msg = self.load_error(self.write_json({"root": bad}))
        self.assertIn("'root' must be a directory", msg)

    def test_unknown_type(self):
        link = {"type": "link", "owner": "a", "group": "a",
                "mtime": "2024-01-01T00:00:00"}
        bad = dict(ROOT, children={"x": link})
        msg = self.load_error(self.write_json({"root": bad}))
        self.assertIn("unknown type 'link'", msg)

    def test_missing_field(self):
        bad = dict(ROOT)
        del bad["owner"]
        msg = self.load_error(self.write_json({"root": bad}))
        self.assertIn("missing 'owner'", msg)

    def test_bad_mtime(self):
        bad = dict(ROOT, mtime="yesterday")
        msg = self.load_error(self.write_json({"root": bad}))
        self.assertIn("bad mtime", msg)

    def test_name_with_slash(self):
        bad = dict(ROOT, children={"a/b": ROOT["children"]["readme.txt"]})
        msg = self.load_error(self.write_json({"root": bad}))
        self.assertIn("bad name 'a/b'", msg)

    # ── content errors ─────────────────────────────────────────────────

    def test_unknown_encoding(self):
        bad = dict(ROOT["children"]["readme.txt"], encoding="hex")
        root = dict(ROOT, children={"f": bad})
        msg = self.load_error(self.write_json({"root": root}))
        self.assertIn("unknown encoding 'hex'", msg)

    def test_bad_base64(self):
        bad = dict(ROOT["children"]["logo.bin"], content="!!!not base64")
        root = dict(ROOT, children={"f": bad})
        msg = self.load_error(self.write_json({"root": root}))
        self.assertIn("invalid base64", msg)


if __name__ == "__main__":
    unittest.main()
