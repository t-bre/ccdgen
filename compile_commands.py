import json
import os
import subprocess

if __name__ == '__main__':

    COMPILER = 'gcc'
    MAKE_DIR = './test'
    OUTPUT_DIR = './test/build'
    OUTPUT_FILE = 'compile_commands.json'

    # run make and capture the output
    os.chdir(MAKE_DIR)
    
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
        
        if COMPILER not in line:
            continue

        file = None
        for token in line.split(' '):
            if any(end in token[-3:] for end in ['.c', '.s', '.S']):
                file = token.strip('\" ')
                file = os.path.abspath(file)
                break

        if file is None:
            continue

        db_entry = {
            "directory": MAKE_DIR,
            "command": line,
            "file": file
        }
        
        compile_db.append(db_entry)

    # output result
    with open(OUTPUT_FILE, 'w') as file:
        file.write(json.dumps(compile_db, indent=4))