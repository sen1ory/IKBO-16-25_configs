import argparse
import sys

from . import repl
from .errors import VFSError
from .loader import load_vfs
from .script import run_script


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Shell emulator with a virtual file system.",
    )
    parser.add_argument("-v", "--vfs-path",
                        help="path to the VFS JSON file")
    parser.add_argument("-s", "--startup-script",
                        help="script to run before the prompt")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="print debug info")
    return parser.parse_args(argv)


def print_debug(args):
    if args.debug:
        print(f"[DEBUG] vfs_path       = {args.vfs_path or '(not set)'}")
        print(f"[DEBUG] startup_script = {args.startup_script or '(not set)'}")


def main(argv=None):
    args = parse_args(argv)
    print_debug(args)
    ctx = repl.Context()

    # first and foremost handle the vfs init
    if args.vfs_path:
        try:
            ctx.vfs = load_vfs(args.vfs_path)
        except VFSError as e:
            print(f"emulator: {e}")
            return 1

    # running a script
    if args.startup_script:
        try:
            code = run_script(args.startup_script, ctx)
        except OSError as e:
            print(f"emulator: cannot read "
                  f"'{args.startup_script}': {e.strerror}")
            return 1
        except UnicodeDecodeError:
            print(f"emulator: '{args.startup_script}' is not valid UTF-8")
            return 1
        if code is not None:
            return code

    # run repl
    return repl.run(ctx)


if __name__ == "__main__":
    sys.exit(main())
