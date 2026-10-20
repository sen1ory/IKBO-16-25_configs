import sys

from . import repl


def main():
    ctx = repl.Context()
    return repl.run(ctx)


if __name__ == "__main__":
    sys.exit(main())
