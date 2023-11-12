#! /usr/bin/python3 -B

from collections import deque

import sys
import argparse

import compiler_lib
import parser_lib
import log_lib


def compile_command():
    parser = parser_lib.Parser()
    parser.parse_file(args.source)

    if parser.errors:
        log_lib.log("INFO", f"There were {parser.errors} parser errors, stopped compilation")
        sys.exit(1)
        return

    else:
        log_lib.log("INFO", "Successfully parsed")

    if compiler_lib.compile_nasm_program("output.asm", deque(parser.program), args.debug):
        log_lib.log("INFO", f"Error on NASM creation, stopped compilation")
        sys.exit(1)
        return

    else:
        log_lib.log("INFO", "NASM file has been successfully created")
    
    nasm_return = log_lib.command(("nasm", "./output.asm", "-f", "elf64", "-o", "./output.o")).returncode

    if nasm_return:
        log_lib.log("INFO", f"Error on NASM compilation, stopped compilation")
        sys.exit(1)
        return
    
    ld_return = log_lib.command(("ld", "./output.o", "-o", args.output)).returncode

    if not args.keep:
        log_lib.command(("rm", "./output.asm"))

    if ld_return:
        log_lib.log("INFO", f"Error on binding, stopped compilation")
        sys.exit(1)
        return

    log_lib.command(("rm", "./output.o"))
    
    if args.run:
        log_lib.command((f"./{args.output}",))
    

def test_command():
    import quick_test

    error_count = quick_test.quick_test()

    sys.exit(error_count)


parser = argparse.ArgumentParser(
    prog="Corth",
    description="Corth compiler"
)

subparsers = parser.add_subparsers(
    title="Commands"
)

# TODO: merge print-tokens and debug-parser into debug, and add debug options

compile_parser = subparsers.add_parser("compile", help="Compile a Corth file into an executable")
compile_parser.add_argument("source", help="Source file name")
compile_parser.add_argument("-o", "--output", help="Output file name", default="output")
compile_parser.add_argument("-r", "--run", help="Run after compilation", action="store_true")
compile_parser.add_argument("-k", "--keep", help="Keep the NASM file", action="store_true")
compile_parser.add_argument("-d", "--debug", help="Debug mode", action="store_true")
compile_parser.set_defaults(func=compile_command)

test_parser = subparsers.add_parser("quick-test", help="Try to compile every example and print the errors")
test_parser.set_defaults(func=test_command)

args = parser.parse_args()

if "func" in dir(args):
    args.func()
