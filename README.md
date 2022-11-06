# Compile Commands Database GENerator

## About

A simple Python script to generate a [`compile_commands.json` database](https://clang.llvm.org/docs/JSONCompilationDatabase.html) 
by capturing the output of `make`. This script was originally created to provide
compilation databases for `make` based [C/C++ projects in Visual Studio Code](https://code.visualstudio.com/docs/cpp/c-cpp-properties-schema-reference).

## Installation

[Latest PyPi release](https://pypi.org/project/ccdgen/0.0.1/)
```sh
pip install ccdgen
```

## Usage

Command line:
```sh
python compile_commands.py 
    [-h] 
    [--compiler COMPILER] 
    [--dir DIR] 
    --extensions EXT [EXT ...] 
    [--output FILE] 
    [--target TARGET] 
    [--clean-target CLEAN_TARGET] 
    [--no-clean] 
    ...
```

Arguments:

| Option               | Default                 | Description                          |
|----------------------|-------------------------|--------------------------------------|
| `-h`, `--help`       |                         | Show help message and exit           |
| `-c`, `--compiler`   | (auto detect)           | Specify compiler                     |
| `-d`, `--dir`        | ./                      | Working directory to run `make` from |
| `-e`, `--extensions` |                         | Extension(s) for source files        |
| `-o`, `--output`     | ./compile_commands.json | Output file                          |
| `t`, `--target`      | all                     | `make` build target                  |
| `--clean-target`     | clean                   | Custom build cleaning target         |
| `--no-clean`         |                         | Don't run build cleaning command     |

Additional arguments (any, other than the target) can be passed to `make` by adding them at the end of the command following a double dash (`--`). For example, to run `make all -j` as the build command:

```sh
python compile_commands.py --extensions .c --target all -- -j
```

Example Visual Studio Code task:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "compile_commands.py",
            "type": "shell",
            "command": "python",
            "osx": {
                "command": "python3"
            },
            "args": [
                "../src/compile_commands.py",
                "--extensions", ".c",
                "--target", "all",
                "--", "-j"
            ]
        }
    ]
}
```

## Limitations

- The script relies on the Python standard library modules `argparse`, `json`, 
  `os`, `subprocess` and `sys`.
- This script relies on `make` echoing the compiler commands it runs to 
  stdout. If compiler commands are prefixed in the Makefile with `@` or 
  `make` is run in silent mode, the output cannot be captured.
- The build must succeed to generate a full compilation database, though 
  warnings are not a problem.
- Currently only tested with Python 3.10 on macOS Ventura.

## Other Tools

- [CMake](https://cmake.org) (since version 2.8.5) can be used as is to generate 
  `compile_commands.json` by adding `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` when 
  calling it. This only works for Unix Makefile builds.
- [Bear](https://github.com/rizsotto/Bear) is much more advanced tool for 
  generating compilation databases for `clang` tooling. macOS, Linux and FreeBSD
  are currently supported.