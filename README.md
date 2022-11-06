# Compile Commands Database GENerator

[![PyPI status](https://img.shields.io/pypi/status/ccdgen.svg)](https://pypi.python.org/pypi/ccdgen/)
[![PyPi version](https://badgen.net/pypi/v/ccdgen/)](https://pypi.com/project/ccdgen)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ccdgen.svg)](https://pypi.python.org/pypi/ccdgen/)
[![GitHub license](https://img.shields.io/github/license/t-bre/ccdgen)](https://github.com/t-bre/ccdgen/blob/master/LICENSE)

## About

A Python script to generate a [`compile_commands.json` database](https://clang.llvm.org/docs/JSONCompilationDatabase.html) 
by capturing the output of `make`. This script was originally created to provide
compilation databases for `make` based [C/C++ projects in Visual Studio Code](https://code.visualstudio.com/docs/cpp/c-cpp-properties-schema-reference).

## Installation

[Latest PyPi release](https://pypi.org/project/ccdgen/0.0.1/)
```sh
pip install ccdgen
```

## Usage

```text
python3 -m ccdgen --extensions <arguments...> -- <your build command>
```


Arguments:

| Option               | Default                 | Description                          |
|----------------------|-------------------------|--------------------------------------|
| `-h`, `--help`       |                         | Show help message and exit           |
| `-c`, `--compiler`   | (auto detect)           | Specify compiler                     |
| `-d`, `--dir`        | ./                      | Working directory to run `make` from |
| `-e`, `--extensions` |                         | Extension(s) for source files        |
| `-o`, `--output`     | ./compile_commands.json | Output file                          |

For example, to run `make all` as the build command for a C project:

```sh
python3 -m ccdgen --extensions .c -- make all
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
                "-m", "ccdgen",
                "--extensions", ".c",
                "--", "make", "all"
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
