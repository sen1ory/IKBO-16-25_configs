class ShellError(Exception):
    """Base class for errors that are shown to the user as a message."""


class ParseError(ShellError):
    pass


class CommandError(ShellError):
    pass


class VFSError(ShellError):
    """A lookup in the VFS failed. The message has no command prefix."""


class ExitShell(Exception):
    """Raised by the exit command to stop the emulator."""

    def __init__(self, code=0):
        super().__init__(code)
        self.code = code
