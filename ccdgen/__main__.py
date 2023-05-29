import argparse
import json
import os
import re
import subprocess
import sys


def create_parser() -> argparse.ArgumentParser:
    """Creates argument parser

    Returns:
        Argument parser
    """
    DESCRIPTION = 'Generates compilation databases from the standard output of make'
    
    NCOLS = os.get_terminal_size().columns
    formatter = lambda prog: argparse.HelpFormatter(prog, 
                                                    max_help_position=NCOLS)

    parser = argparse.ArgumentParser(prog='ccdgen',
                                     description=DESCRIPTION,
                                     formatter_class=formatter)

    parser.add_argument('--compiler',
                        '-c',
                        metavar='COMPILER',
                        type=str,
                        required=False,
                        help='specify compiler',
                        default=None)

    parser.add_argument('--dir',
                        '-d',
                        metavar='DIR',
                        type=str,
                        required=False,
                        help='working directory to run make from',
                        default=os.getcwd())

    parser.add_argument('--extensions',
                        '-e', 
                        metavar='EXT', 
                        type=str,
                        nargs='+',
                        required=True,
                        help='file extension(s) for source files')

    parser.add_argument('--output',
                        '-o',
                        metavar='FILE',
                        required=False,
                        help='output file',
                        default='compile_commands.json')

    parser.add_argument('build_command',
                        metavar='--',
                        type=str,
                        nargs=argparse.REMAINDER,
                        help='build command',
                        default=[])

    return parser


def make(command: list[str] = []) -> str:
    """Runs `make` and captures stdout

    Args:
        command:    build command

    Returns:
        str:    captured stdout
    """

    CODEC = 'utf-8' # TODO: is this always the case?

    make_commands = ['--always-make', '--dry-run']

    try:
        result = subprocess.run(command + make_commands, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
        ret = None

    except FileNotFoundError as e:
        print(f'No such command: {e.filename}')
        sys.exit(1)

    try:
        result.check_returncode()
        ret = result.stdout.decode(CODEC)
        print(ret)

    except subprocess.CalledProcessError as e:
        msg = result.stderr.decode(CODEC)
        print(msg, end='')
        sys.exit(1)

    return ret


def parse_compile_commands(make_stdout: str, 
                           compiler: str,
                           extensions: list[str]) -> dict:
    """Parses compile commands from stdout of `make`

    Args:
        make_stdout:    stdout from `make` call
        compiler:       name of compiler
        extensions:     list of file extensions which are being compiled

    Returns:
        Compile commands as a list of dictionaries
    """
    MAX_EXTENSION_LEN = max([len(ext) for ext in extensions])

    compile_db = []

    for line in make_stdout.splitlines():
            
        if compiler is None:
            compiler = detect_compiler(line)

        if compiler is None or compiler not in line:
            continue

        file = None
        tokens = line.split(' ')

        for token in tokens:
            if any(end in token[-MAX_EXTENSION_LEN:] for end in extensions):
                file = token.strip('\" ')
                file = os.path.abspath(file)
                break

        if file is None:
            continue

        tokens[-1] = file # use abs path for file in compiler command
        command = ' '.join(tokens)
        command = replace_relative_paths(command)

        db_entry = {
            "directory": os.path.dirname(file),
            "command": command,
            "file": os.path.basename(file)
        }
        
        compile_db.append(db_entry)

    if compiler is None:
        print('Could not detect compiler')
        sys.exit(1)

    return compile_db

def replace_relative_paths(command: str) -> str:
    """Replaces any relative paths with absolute paths

    Currently only checks for include paths starting with -I

    Args:
        command:    Compiler command from `make` output

    Returns:
        Command with relative paths replaced
    """

    matches = re.findall(r'-I(?:\.\.\/)+[^-\s]+', command)

    for m in matches:
        relative_path = m[2:]  # remove '-I' prefix
        absolute_path = os.path.abspath(relative_path)
        command = command.replace(m, '-I' + absolute_path)
    
    return command

def detect_compiler(line: str) -> str | None:
    """Tries to detect the name of a compiler in a line of text

    Currently checks for:
        gcc, g++, clang, clang++, cc

    Args:
        line:   Line of text (from make stdout)

    Returns:
        Name of compiler, or None if no matches
    """
    
    COMPILERS = [
        'gcc', 'g++', 'clang', 'clang++', 'cc',
    ]

    for token in line.split(' '):
        for compiler in COMPILERS:
            if token[-len(compiler):] == compiler:
                print(f'Detected compiler: {token}')
                return token

    return None


if __name__ == '__main__':

    parser = create_parser()
    config = parser.parse_args(sys.argv[1:])

    build_command = config.build_command
    if len(build_command) > 0 and build_command[0] == '--': # ignore '--'
        build_command = build_command[1:]

    # run make and capture the output
    os.chdir(config.dir)

    make_output = make(build_command)

    # parse the output to generate compile database
    compile_db = parse_compile_commands(make_output, 
                                        config.compiler, 
                                        config.extensions)

    # save result to file
    with open(config.output, 'w') as file:
        file.write(json.dumps(compile_db, indent=4))
        file.write('\n')