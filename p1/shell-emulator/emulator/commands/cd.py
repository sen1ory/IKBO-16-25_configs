from ..errors import CommandError


def run(args, ctx):
    """
    `cd` stub
    """
    if len(args) > 1:
        raise CommandError("cd: too many arguments")
    # stub
    return f"cd {args}"
