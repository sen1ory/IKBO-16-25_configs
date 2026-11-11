from ..errors import CommandError, VFSError
from ..vfs import DirNode, FileNode


def run(args, ctx):
    """
    List a directory, or show a file. Supports -l for long format.

    With no path, lists the current directory. With several directories,
    each listing gets a heading.
    """

    long_format = False
    paths = []
    for arg in args:
        if arg == "-l":
            long_format = True
        elif arg.startswith("-"):
            raise CommandError(f"ls: invalid option -- '{arg[1:]}'")
        else:
            paths.append(arg)
    if not paths:
        paths = [ctx.cwd]

    blocks = []
    for path in paths:
        node = lookup(path, ctx)
        if isinstance(node, DirNode):
            lines = [
                format_entry(name, child, long_format)
                for name, child in sorted(node.children.items())
            ]
            if len(paths) > 1:
                lines.insert(0, f"{path}:")
        else:
            lines = [format_entry(path, node, long_format)]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def lookup(path, ctx):
    """Find the node for a path, or raise CommandError."""
    if path == "":
        raise CommandError("ls: '': No such file or directory")
    try:
        return ctx.vfs.resolve(ctx.cwd, path)
    except VFSError as e:
        raise CommandError(f"ls: {path}: {e}")


def format_entry(name, node, long_format):
    if not long_format:
        return name
    kind = "d" if isinstance(node, DirNode) else "-"
    mtime = node.mtime.strftime("%b %d %H:%M")
    return (f"{kind}{node.mode} {node.owner} {node.group} "
            f"{size_of(node):>6} {mtime} {name}")


def size_of(node):
    """Size in bytes. Directories show 0."""
    if not isinstance(node, FileNode):
        return 0
    if isinstance(node.content, str):
        return len(node.content.encode("utf-8"))
    return len(node.content)
