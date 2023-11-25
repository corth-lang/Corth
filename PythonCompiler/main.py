#! /usr/bin/python3 -B

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
    import os
    import subprocess

    dev_null = "/dev/null"

    errors = False
    
    if args.compiler:
        process = subprocess.run(["./Corth/build/corth", "compile-nasm", "./Corth/compiler/corth.corth", dev_null], capture_output=True)

        output = process.stdout.decode()
        error = process.stderr.decode()

        if process.returncode:
            errors = True
                
            print(f"Got '{process.returncode}' while trying to compile Corth compiler to NASM.")
            print(f"stdout:")
            print(output)
            print(f"stderr:")
            print(error)

            if args.once:
                sys.exit(1)

    if args.examples:
        for item in os.listdir("./examples/"):
            full_path = os.path.join("./examples/", item)

            process = subprocess.run(['./Corth/build/corth', 'compile-nasm', full_path, dev_null], capture_output=True)

            output = process.stdout.decode()
            error = process.stderr.decode()

            if process.returncode:
                errors = True
                
                print(f"File '{full_path}' returned error code '{process.returncode}'")
                print(f"stdout:")
                print(output)
                print(f"stderr:")
                print(error)

                if args.once:
                    sys.exit(1)

    sys.exit(errors)


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

test_parser = subparsers.add_parser("test", help="Test the compiler or examples")
test_parser.add_argument("-c", "--compiler", help="Try to compile ./Corth/compiler/corth.corth", action="store_true")
test_parser.add_argument("-e", "--examples", help="Try to compile examples in ./examples", action="store_true")
test_parser.add_argument("-o", "--once", help="Break after one fail", action="store_true")
test_parser.set_defaults(func=test_command)

args = parser.parse_args()

if "func" in dir(args):
    args.func()
