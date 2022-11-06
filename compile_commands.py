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

    return parser
    

if __name__ == '__main__':

    parser = create_parser()
    config = parser.parse_args(sys.argv[1:])

    MAX_EXTENSION_LEN = max([len(ext) for ext in config.extensions])

    # run make and capture the output
    os.chdir(config.dir)
    
    subprocess.run(['make', 'clean'], 
                   stdout=subprocess.DEVNULL, 
                   stderr=subprocess.DEVNULL)
    
    make_output = subprocess.run(['make', 'all', '-j'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.DEVNULL)

    make_output = make_output.stdout.decode('utf-8')

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