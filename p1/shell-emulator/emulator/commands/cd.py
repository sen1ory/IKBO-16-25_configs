from ..errors import CommandError, VFSError
from ..vfs import DirNode


def run(args, ctx):
    """Change the current directory. With no argument, go to /."""
    if len(args) > 1:
        raise CommandError("cd: too many arguments")
    path = args[0] if args else "/"
    try:
        node = ctx.vfs.resolve(ctx.cwd, path)
    except VFSError as e:
        raise CommandError(f"cd: {path}: {e}")
    if not isinstance(node, DirNode):
        raise CommandError(f"cd: {path}: Not a directory")
    ctx.cwd = ctx.vfs.normalize(ctx.cwd, path)
