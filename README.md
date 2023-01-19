# Corth
A programming language made with inspiration of Porth, which is a programming language made with inspiration of Forth.

parser_lib.py contains the parser, which returns a list of tokens.
compiler_lib.py contains the compiler, which creates the NASM program.

main.py contains options to compile, simulate and debug.
example.corth is an example program to show the language.

## How to use?

To compile a Corth program to an executable,

    python3 main.py compile <source>

For more information,

    python3 main.py -h
