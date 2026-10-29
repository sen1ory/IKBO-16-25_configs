from .parser import parse
from .commands import dispatch
from .errors import ExitShell, ShellError


# repl (read evaluate print loop) and state handling


class Context:
    """State shared by all commands."""

    def __init__(self, vfs_name="vfs"):
        self.vfs_name = vfs_name
        self.cwd = "/"

    def prompt(self):
        return f"{self.vfs_name}:{self.cwd}$ "


def execute(line, ctx):
    """Parse and run one line. Errors are raised to the caller."""
    tokens = parse(line)
    if not tokens:
        return
    output = dispatch(tokens, ctx)
    if output:
        print(output)


def run(ctx):
    """Interactive repl. Returns the exit code."""
    while True:
        # collect and handle input
        try:
            line = input(ctx.prompt())
        except EOFError:  # ctrl+d
            print()
            return 0
        except KeyboardInterrupt:  # ctrl+c just skips for the next prompt
            print()
            continue

        # execute and handle state
        try:
            execute(line, ctx)
        except ExitShell as e:
            return e.code
        except ShellError as e:
            print(e)
