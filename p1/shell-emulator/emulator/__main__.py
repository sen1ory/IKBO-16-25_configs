import argparse
import sys

from . import repl


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Shell emulator with a virtual file system.",
    )
    parser.add_argument("--vfs-path",
                        help="path to the VFS JSON file")
    parser.add_argument("--startup-script",
                        help="script to run before the prompt")
    return parser.parse_args(argv)


def print_debug(args):
    print(f"[DEBUG] vfs_path       = {args.vfs_path or '(not set)'}")
    print(f"[DEBUG] startup_script = {args.startup_script or '(not set)'}")


def main(argv=None):
    args = parse_args(argv)
    print_debug(args)
    ctx = repl.Context()
    return repl.run(ctx)


if __name__ == "__main__":
    sys.exit(main())
