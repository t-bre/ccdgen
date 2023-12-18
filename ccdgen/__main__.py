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

        file_absolute = None
        file_relative = None
        tokens = line.split(' ')

        for token in tokens:
            if any(end in token[-MAX_EXTENSION_LEN:] for end in extensions):
                file = token.strip('\" ')
                file_relative = file
                file_absolute = os.path.abspath(file)
                break

        if file_absolute is None:
            continue
        
        command = ' '.join(tokens)
        command = replace_relative_paths(command)
        command = command.replace(file_relative, file_absolute)

        db_entry = {
            "directory": os.path.dirname(file_absolute),
            "command": command,
            "file": os.path.basename(file_absolute)
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

    # replace relative include paths
    matches = re.findall(r'-I([^\s]+)', command) # capture does not include -I

    for m in matches:
        # space in replacement ensures that include paths which are a subset of
        # another include path are not replaced in that path
        relative_path = m
        absolute_path = os.path.abspath(relative_path)
        command = command.replace(m + ' ', absolute_path + ' ')

    # replace relative file paths
    matches = re.findall(r'(\.\.\/)+([a-zA-z0-9\/]*)(\.)([a-zA-z0-9]+)', command)
    
    for m in matches:
        relative_path = ''.join(m)
        absolute_path = os.path.abspath(relative_path)

# python3 /Users/opses/Documents/Git/ccdgen/ccdgen/__main__.py --extensions .c --output /Users/opses/Documents/Git/verto-fw/mcu/compile_commands.json -- make -C /Users/opses/Documents/Git/verto-fw -j    
    
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

    # change working directory to that which make runs from
    # also check for make calling make (only 1 level deep)
    def chdir_if_make_does(make_cmd: str):
        make_dir_opts = ['-C', '--directory']
        for opt in make_dir_opts:
            try:
                idx = make_cmd.index(opt)
                cd_path = make_cmd[idx+1]
                print(f'Changed directory: {os.path.abspath(cd_path)}')
                os.chdir(cd_path)
            except ValueError:
                pass

    chdir_if_make_does(build_command)

    for line in make_output.splitlines():
        if '/bin/make' in line: # make probably called make if true
            chdir_if_make_does(line.split(' '))
            break

    # parse the output to generate compile database
    compile_db = parse_compile_commands(make_output, 
                                        config.compiler, 
                                        config.extensions)

    # save result to file
    with open(config.output, 'w') as file:
        file.write(json.dumps(compile_db, indent=4))
        file.write('\n')