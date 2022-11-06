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
    DESCRIPTION = 'Generates a compilation database from the output of make'
    
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('--compiler',
                        '-c',
                        metavar='COMPILER',
                        type=str,
                        required=True, # TODO: add compiler detection?
                        help='compiler')

    parser.add_argument('--dir',
                        '-d',
                        metavar='DIR',
                        type=str,
                        required=False,
                        help='working directory to run `make` from',
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

    # this is to allow users to run their own clean command
    # (e.g. if the makefile doesn't have the "clean" target)
    parser.add_argument('--no-clean',
                        required=False,
                        action='store_true',
                        help='don\'t run `make clean`',
                        default=False)

    parser.add_argument('--clean-target',
                        type=str,
                        required=False,
                        help='custom `make` target for cleaning build',
                        default='clean')

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

    # TODO: allow target and args to be specified
    #       -j is definitely not always portable
    result = subprocess.run(['make', target, '-j'], 
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


if __name__ == '__main__':

    parser = create_parser()
    config = parser.parse_args(sys.argv[1:])

    MAX_EXTENSION_LEN = max([len(ext) for ext in config.extensions])

    # run make and capture the output
    os.chdir(config.dir)
    
    if not config.no_clean:
        make(config.clean_target)
    
    make_output = make('all')

    # parse the output to generate compile database
    compile_db = []

    for line in make_output.splitlines():
        
        if config.compiler not in line:
            continue

        file = None
        for token in line.split(' '):
            if any(end in token[-MAX_EXTENSION_LEN:] for end in config.extensions):
                file = token.strip('\" ')
                file = os.path.abspath(file)
                break

        if file is None:
            continue

        db_entry = {
            "directory": os.path.dirname(file),
            "command": line, # TODO: this needs to be shell escaped
            "file": os.path.basename(file)
        }
        
        compile_db.append(db_entry)

    # output result
    with open(config.output, 'w') as file:
        file.write(json.dumps(compile_db, indent=4))
        file.write('\n')