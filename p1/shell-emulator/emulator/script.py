from .errors import ExitShell, ShellError
from .repl import execute


def run_script(path, ctx):
    """
    Run a script line by line, as if each line was typed.

    Returns the exit code if the script ends the shell (exit or error),
    or None if the script finished and the interactive loop should start.
    """
    # utf-8-sig also strips a bom written by some windows editors
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()

    for number, line in enumerate(lines, start=1):
        text = line.strip()
        # skip blank lines and comments
        if not text or text.startswith("#"):
            continue

        print(f"{ctx.prompt()}{text}")
        try:
            execute(text, ctx)
        except ExitShell as e:
            return e.code
        except ShellError as e:
            # stop at the first error
            print(f"Script error at line {number}: {e}")
            return 1

    return None
