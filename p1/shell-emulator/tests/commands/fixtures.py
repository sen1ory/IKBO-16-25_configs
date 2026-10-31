from datetime import datetime

from emulator.repl import Context
from emulator.vfs import DirNode, FileNode, VFS

TIME = datetime(2024, 1, 1)


def d(name, children=None, owner="root", mtime=TIME):
    return DirNode(name, owner, owner, "rwxr-xr-x", mtime, children)


def f(name, content, owner="root", mode="rw-r--r--", mtime=TIME):
    return FileNode(name, owner, owner, mode, mtime, content)


def make_ctx():
    """A context at / with a small tree for the command tests."""
    root = d("", {
        "etc": d("etc", {
            "hosts": f("hosts", "127.0.0.1 localhost\n",
                       mtime=datetime(2024, 1, 2, 10, 5)),
        }),
        "home": d("home", {
            "user": d("user", {
                "notes.txt": f("notes.txt", "hi\n", owner="user",
                               mtime=datetime(2024, 3, 4, 9, 30)),
                "logo.png": f("logo.png", b"\x89PNG", owner="user",
                              mode="rw-------",
                              mtime=datetime(2024, 3, 5, 12, 0)),
            }, owner="user"),
        }),
        "readme.txt": f("readme.txt", "Welcome\n",
                        mtime=datetime(2024, 1, 6, 8, 0)),
        "tmp": d("tmp"),
    })
    return Context(VFS("vfs", root))
