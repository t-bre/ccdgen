import argparse
import json
import os
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

    parser = argparse.ArgumentParser(description=DESCRIPTION,
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

    parser.add_argument('--target',
                        '-t',
                        metavar='TARGET',
                        type=str,
                        required=False,
                        help='make target',
                        default='all')

    parser.add_argument('make_args',
                        metavar='--',
                        type=str,
                        nargs=argparse.REMAINDER,
                        help='make arguments (excluding target)',
                        default=[])

    # this is to allow users to run their own clean command
    # (e.g. if the makefile doesn't have the "clean" target)
    parser.add_argument('--clean-target',
                        type=str,
                        required=False,
                        help='custom build cleaning target',
                        default='clean')

    parser.add_argument('--no-clean',
                        required=False,
                        action='store_true',
                        help='don\'t run clean command',
                        default=False)

    return parser


def make(target: str, args: list[str] = []) -> str:
    """Runs `make` and captures stdout

    Args:
        target: make target
        args:   extra aruguments for make

    Returns:
        str:    captured stdout
    """

    CODEC = 'utf-8' # TODO: is this always the case?

    result = subprocess.run(['make', target] + args, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
    ret = None

    try:
        result.check_returncode()
        ret = result.stdout.decode(CODEC)

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
        for token in line.split(' '):
            if any(end in token[-MAX_EXTENSION_LEN:] for end in extensions):
                file = token.strip('\" ')
                file = os.path.abspath(file)
                break

        if file is None:
            continue

        db_entry = {
            "directory": os.path.dirname(file),
            "command": line,
            "file": os.path.basename(file)
        }
        
        compile_db.append(db_entry)

    if compiler is None:
        print('Could not detect compiler')
        sys.exit(1)

    return compile_db


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
            if token == compiler or token[:-len(compiler)] == compiler:
                print(f'Detected compiler: {token}')
                return token

    return None


if __name__ == '__main__':

    parser = create_parser()
    config = parser.parse_args(sys.argv[1:])

    make_args = config.make_args
    if len(make_args) > 0 and make_args[0] == '--':
        make_args = make_args[1:]

    # run make and capture the output
    os.chdir(config.dir)
    
    if not config.no_clean:
        make(config.clean_target)
    
    make_output = make(config.target, make_args)

    # parse the output to generate compile database
    compile_db = parse_compile_commands(make_output, 
                                        config.compiler, 
                                        config.extensions)

    # save result to file
    with open(config.output, 'w') as file:
        file.write(json.dumps(compile_db, indent=4))
        file.write('\n')