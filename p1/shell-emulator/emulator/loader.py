import base64
import binascii
import json
from datetime import datetime

from .errors import VFSError
from .vfs import DirNode, FileNode, VFS


def load_vfs(path):
    """Read a VFS JSON file and build a VFS. Raises VFSError on any problem."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise VFSError(f"vfs file not found: {path}")
    except json.JSONDecodeError as e:
        raise VFSError(f"vfs file is not valid JSON: {e}")

    if not isinstance(data, dict) or "root" not in data:
        raise VFSError("vfs structure error: missing 'root'")

    name = data.get("name", "vfs")
    if not isinstance(name, str):
        raise VFSError("vfs structure error: 'name' must be a string")

    root = build_node("", data["root"], "root")
    if not isinstance(root, DirNode):
        raise VFSError("vfs structure error: 'root' must be a directory")
    return VFS(name, root)


def build_node(name, data, where):
    """Turn one JSON object into a FileNode or DirNode, checking each field."""
    if not isinstance(data, dict):
        raise VFSError(
            f"vfs structure error at {where}: node must be an object"
        )

    for key in ("type", "owner", "group", "mtime"):
        if key not in data:
            raise VFSError(f"vfs structure error at {where}: missing '{key}'")

    owner = data["owner"]
    group = data["group"]
    mode = data.get("mode", "rw-r--r--")
    mtime = parse_mtime(data["mtime"], where)

    kind = data["type"]
    if kind == "dir":
        children = {}
        for child_name, child in data.get("children", {}).items():
            check_name(child_name, where)
            children[child_name] = build_node(
                child_name, child, f"{where}/{child_name}"
            )
        return DirNode(name, owner, group, mode, mtime, children)

    if kind == "file":
        content = read_content(data, where)
        return FileNode(name, owner, group, mode, mtime, content)

    raise VFSError(f"vfs structure error at {where}: unknown type '{kind}'")


def read_content(data, where):
    """Return text as str, or base64 data decoded to bytes."""
    if "content" not in data or "encoding" not in data:
        raise VFSError(
            f"vfs structure error at {where}: "
            "file needs 'encoding' and 'content'"
        )

    encoding = data["encoding"]
    content = data["content"]
    if not isinstance(content, str):
        raise VFSError(
            f"vfs structure error at {where}: 'content' must be a string"
        )

    if encoding == "text":
        return content
    if encoding == "base64":
        try:
            return base64.b64decode(content, validate=True)
        except (binascii.Error, ValueError):
            raise VFSError(f"vfs error at {where}: invalid base64 content")

    raise VFSError(
        f"vfs structure error at {where}: unknown encoding '{encoding}'"
    )


def parse_mtime(value, where):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise VFSError(f"vfs structure error at {where}: bad mtime '{value}'")


def check_name(name, where):
    if not name or "/" in name or name in (".", ".."):
        raise VFSError(f"vfs structure error at {where}: bad name '{name}'")
