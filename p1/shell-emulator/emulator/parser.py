import os
import re
import shlex

from .errors import ParseError

# matches $name and ${name}
VAR_RE = re.compile(r"\$(?:(\w+)|\{(\w+)\})")


def expand_vars(line):
    """
    Replace environment variables, except inside single quotes.
    Escaping handled with backslash:
    - when escaped, `'`, `"`, and `$` lose their semantic meaning;
    - everything escaped gets added to result as is.

    Undefined variables become an empty string.
    """

    result = ""
    escaped = False
    in_single = False
    in_double = False

    def handle_semantic():
        """
        Handles state and expansion for characters with non-literal meaning.
        """

        nonlocal result, in_single, in_double, i
        if c == "'" and not in_double:
            in_single = not in_single
        elif c == '"' and not in_single:
            in_double = not in_double
        elif c == "$" and not in_single:
            match = VAR_RE.match(line, i)
            if match:
                name = match.group(1) or match.group(2)
                result += os.environ.get(name, "")
                i = match.end()     # move iterator to first after match
                return True         # continue

        return False    # no continue

    i = 0
    while i < len(line):
        c = line[i]
        if not escaped:
            if c == '\\':
                i += 1
                escaped = True
                continue

            # handle semantic state and expansion
            # if expanded, will skip to after the envvar
            skip = handle_semantic()
            if skip:
                continue

        # handle literal character meaning
        result += c
        i += 1
        escaped = False

    return result


def parse(line):
    """Turn a command line into a list of tokens (command name first)."""

    line = expand_vars(line)
    try:
        return shlex.split(line)
    except ValueError:
        # shlex raises ValueError for an unclosed quote
        raise ParseError("syntax error: unbalanced quotes")
