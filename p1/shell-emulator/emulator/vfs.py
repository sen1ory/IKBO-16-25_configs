from .errors import VFSError


class Node:
    """Attributes shared by files and directories."""

    def __init__(self, name, owner, group, mode, mtime):
        self.name = name
        self.owner = owner
        self.group = group
        self.mode = mode
        self.mtime = mtime


class FileNode(Node):
    """A file. content is str for text and bytes for binary."""

    def __init__(self, name, owner, group, mode, mtime, content):
        super().__init__(name, owner, group, mode, mtime)
        self.content = content


class DirNode(Node):
    """A directory. children maps each name to its node."""

    def __init__(self, name, owner, group, mode, mtime, children=None):
        super().__init__(name, owner, group, mode, mtime)
        self.children = children or {}


class VFS:
    """An in-memory file system with a name and a root directory."""

    def __init__(self, name, root):
        self.name = name
        self.root = root

    def normalize(self, cwd, path):
        """Return the absolute path, with . and .. handled."""
        if not path.startswith("/"):
            path = cwd + "/" + path
        parts = []
        for part in path.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return "/" + "/".join(parts)

    def resolve(self, cwd, path):
        """
        Return the node at path, or raise VFSError
        if it cannot be reached.
        """
        node = self.root
        for part in self.normalize(cwd, path).split("/"):
            if not part:
                continue
            if not isinstance(node, DirNode):
                raise VFSError("Not a directory")
            if part not in node.children:
                raise VFSError("No such file or directory")
            node = node.children[part]

        # a trailing slash only works on directories
        if path.endswith("/") and not isinstance(node, DirNode):
            raise VFSError("Not a directory")
        return node
