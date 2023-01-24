import sys
import argparse

import compiler_lib
import parser_lib
import log_lib


def compile_command():
    parser = parser_lib.Parser()
    parser.parse_file(args.source)

    if parser.errors:
        log_lib.log("INFO", f"There were {parser_lib.errors} parser errors, stopped compilation")
        return

    else:
        log_lib.log("INFO", "Successfully parsed")

    if compiler_lib.compile_nasm_program("output.asm", iter(parser.program), args.debug, args.space):
        log_lib.log("INFO", f"Error on NASM creation, stopped compilation")
        return

    else:
        log_lib.log("INFO", "NASM file has been successfully created")
    
    log_lib.command(("nasm", "output.asm", "-f", "elf64", "-o", "output.o"))
    log_lib.command(("ld", "output.o", "-o", args.output))

    if not args.keep:
        log_lib.command(("rm", "output.asm"))
        log_lib.command(("rm", "output.o"))

    if args.run:
        log_lib.command((f"./{args.output}",))
    

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

compile_parser = subparsers.add_parser("compile", help="Compile a Corth file into an executable")
compile_parser.add_argument("source", help="Source file name")
compile_parser.add_argument("-o", "--output", help="Output file name", default="output")
compile_parser.add_argument("-r", "--run", help="Run after compilation", action="store_true")
compile_parser.add_argument("-k", "--keep", help="Keep object and NASM files", action="store_true")
compile_parser.add_argument("-d", "--debug", help="Debug mode", action="store_true")
compile_parser.add_argument("-s", "--space", help="Allowed memory usage", default="0x4000")
compile_parser.set_defaults(func=compile_command)

test_parser = subparsers.add_parser("test", help="Run unit tests")
test_parser.set_defaults(func=test_command)

args = parser.parse_args()

if "func" in dir(args):
    args.func()
