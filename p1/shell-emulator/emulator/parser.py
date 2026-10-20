import os
import re
import shlex

from .errors import ParseError

# matches $name and ${name}
VAR_RE = re.compile(r"\$(?:(\w+)|\{(\w+)\})")


def expand_vars(line):
    """
    Replace environment variables, except inside single quotes.

    Undefined variables become an empty string, like in a real shell.
    """
    result = ""
    in_single = False
    in_double = False
    i = 0
    while i < len(line):
        c = line[i]
        if c == "'" and not in_double:
            in_single = not in_single
        elif c == '"' and not in_single:
            in_double = not in_double
        elif c == "$" and not in_single:
            match = VAR_RE.match(line, i)
            if match:
                name = match.group(1) or match.group(2)
                result += os.environ.get(name, "")
                i = match.end()
                continue
        result += c
        i += 1
    return result


def parse(line):
    """Turn a command line into a list of tokens (command name first)."""
    line = expand_vars(line)
    try:
        return shlex.split(line)
    except ValueError:
        # shlex raises ValueError for an unclosed quote
        raise ParseError("syntax error: unbalanced quotes")
