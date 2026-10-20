from ..errors import CommandError
from . import cd, exit, ls


# command name -> handler function run(args, ctx)
COMMANDS = {
    "ls": ls.run,
    "cd": cd.run,
    "exit": exit.run,
}


def dispatch(tokens, ctx):
    """Run the command in tokens[0] with the rest as arguments."""
    name = tokens[0]
    handler = COMMANDS.get(name)
    if handler is None:
        raise CommandError(f"{name}: command not found")
    return handler(tokens[1:], ctx)
