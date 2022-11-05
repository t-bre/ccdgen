# Compile Commands Generator

## About

A simple Python script to generate a `compile_commands.json` database by
capturing the output of `make`. This script was originally created to provide
compilation databases for `make` based [C/C++ projects in Visual Studio Code](https://code.visualstudio.com/docs/cpp/c-cpp-properties-schema-reference).

## Usage

```sh
python compile_commands.py
```

The script relies on the Python standard library modules `json`, `os` and 
`subprocess`.

<!-- TODO: example as a vscode task -->

## Limitations

- This script relies on `make` printing the compiler commands it runs to 
  stdout. If compiler commands are prefixed in the Makefile with `@` or 
  `make` is run in silent mode, the output cannot be captured.
- The build must succeed to generate a full compilation database, though 
  warnings are not a problem.

## Other Tools

- [CMake](https://cmake.org) can be used as is to generate 
  `compile_commands.json` by adding `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` when 
  calling it.
- [Bear](https://github.com/rizsotto/Bear) is much more advanced tool for 
  generating compilation databases for `clang` tooling.