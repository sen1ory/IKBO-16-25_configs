from ..errors import CommandError, ExitShell


def run(args, ctx):
    """
    `exit` shell with exit code passed to `ExitShell`.

    Raises `CommandError` if more than one argument given
    or incorrect argument (non-numeric).
    """
    if len(args) > 1:
        raise CommandError("exit: too many arguments")
    code = 0
    if args:
        try:
            code = int(args[0])
        except ValueError:
            raise CommandError(f"exit: {args[0]}: numeric argument required")
    raise ExitShell(code)
