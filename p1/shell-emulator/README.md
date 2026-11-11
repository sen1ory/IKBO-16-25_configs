# Termial shell written in python

A modular shell composed of python modules to showcase how a shell works.

## Requirements

Python 3 (tested on 3.14.8). No extra packages.


## Running the shell

Run from the root `shell-emulator/` directory:

    python -m emulator

This starts an interactive prompt. Type `exit` (or press Ctrl-D) to quit.


### Options

| Option                  | Meaning                                       |
|---|---|
| `-v/--vfs-path FILE`       | load a virtual file system from a JSON file   |
| `-s/--startup-script FILE` | run a `.emu` script before the prompt appears |
| `-d/--debug`               | print debug info                              |

Example with a sample file system:

    python -m emulator --vfs-path vfs/deep.json

The sample files are in `vfs/`:

- `minimal.json`: a small tree
- `multi_file.json`: several files
- `deep.json`: nested directories (`/etc`, `/home/user/projects`)
- `broken_*.json`: invalid files, for testing error messages


### Sample startup scripts

A `.emu` file holds one command per line. Blank lines and lines starting with `#` are skipped. Each command is echoed with the prompt, as if you had typed it.

    python -m emulator --vfs-path vfs/deep.json --startup-script scripts/startup/all_stage3.emu

- The first error stops the script and the shell exits with code 1.
- An `exit N` line ends the script with code N, and the interactive prompt does not start.
- If the script finishes without an error or an exit, the interactive prompt starts.


### Debug output

The shell prints two `[DEBUG]` lines at startup showing the VFS and script paths.


## Commands

| Command             | Notes                                                       |
|---|---|
| `ls [-l] [PATH...]` | list a directory or show a file; `-l` gives the long format |
| `cd [PATH]`         | change directory; with no argument, go to `/`               |
| `exit [CODE]`       | quit with an optional numeric exit code                     |


## Tests

Run all tests from the `shell-emulator/` directory:

    python -m unittest

Run one test module, for example the `ls` tests:

    python -m unittest tests.commands.test_ls
