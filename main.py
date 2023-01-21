import sys
import argparse

import compiler_lib
import parser_lib
import log_lib


def compile_command():
    log_lib.command(("python3", "main.py", "compile-nasm", args.source) + (("-d",) if args.debug else ()))
    log_lib.command(("nasm", "output.asm", "-f", "elf64", "-o", "output.o"))
    log_lib.command(("ld", "output.o", "-o", args.output))

    if not args.keep:
        log_lib.command(("rm", "output.asm"))
        log_lib.command(("rm", "output.o"))

    if args.run:
        log_lib.command((f"./{args.output}",))

    
def compile_nasm_command():
    program = parser_lib.parse_file(args.source)

    compiler_lib.compile_nasm_program(args.output, program, args.debug)


def print_tokens():
    program = parser_lib.parse_file(args.source)
    print(*program, sep="\n")
        

def debug_parser_command():
    program = parser_lib.parse_file(args.source, True)
    

def test_command():
    assert False, "Tests are not implemented yet"


parser = argparse.ArgumentParser(
    prog="Corth",
    description="Corth compiler"
)

subparsers = parser.add_subparsers(
    title="Commands"
)

# TODO: merge print-tokens and debug-parser into debug, and add debug options

tokens_parser = subparsers.add_parser("print-tokens", help="Parse a Corth file and print the tokens")
tokens_parser.add_argument("source", help="Source file name")
tokens_parser.set_defaults(func=print_tokens)

debug_parser = subparsers.add_parser("debug-parser", help="Parse a Corth file and show the parsing process")
debug_parser.add_argument("source", help="Source file name")
debug_parser.set_defaults(func=debug_parser_command)

compile_nasm_parser = subparsers.add_parser("compile-nasm", help="Compile a Corth file into a NASM file")
compile_nasm_parser.add_argument("source", help="Source file name")
compile_nasm_parser.add_argument("-o", "--output", help="Output file name", default="output.asm")
compile_nasm_parser.add_argument("-d", "--debug", help="Debug mode", action="store_true")
compile_nasm_parser.set_defaults(func=compile_nasm_command)

compile_parser = subparsers.add_parser("compile", help="Compile a Corth file into an executable")
compile_parser.add_argument("source", help="Source file name")
compile_parser.add_argument("-o", "--output", help="Output file name", default="output")
compile_parser.add_argument("-r", "--run", help="Run after compilation", action="store_true")
compile_parser.add_argument("-k", "--keep", help="Keep object and NASM files", action="store_true")
compile_parser.add_argument("-d", "--debug", help="Debug mode", action="store_true")
compile_parser.set_defaults(func=compile_command)

test_parser = subparsers.add_parser("test", help="Run unit tests")
test_parser.set_defaults(func=test_command)

args = parser.parse_args()

if "func" in dir(args):
    args.func()
