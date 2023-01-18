import sys
import corth
import argparse


def compile_command():
    corth.compile_program(args.source, args.output)

    
def compile_nasm_command():
    corth.compile_nasm_program(args.source, args.output)


def print_tokens():
    corth.print_tokens(args.source)


def simulate_command():
    program = corth.Corth()
    program.parse_file(args.source)
    program.simulate_program()


def test_command():
    assert False, "Tests are not implemented yet"


parser = argparse.ArgumentParser(
    prog="Corth",
    description="Corth compiler and simulator"
)

subparsers = parser.add_subparsers(
    title="Commands"
)

compile_parser = subparsers.add_parser("print-tokens", help="Compile a Corth file and print the tokens")
compile_parser.add_argument("source", help="Source file name")
compile_parser.set_defaults(func=print_tokens)

compile_parser = subparsers.add_parser("compile-nasm", help="Compile a Corth file into a NASM file")
compile_parser.add_argument("source", help="Source file name")
compile_parser.add_argument("-o", "--output", help="Output file name", default="output")
compile_parser.set_defaults(func=compile_nasm_command)

compile_parser = subparsers.add_parser("compile", help="Compile a Corth file into an executable")
compile_parser.add_argument("source", help="Source file name")
compile_parser.add_argument("-o", "--output", help="Output file name", default="output")
compile_parser.set_defaults(func=compile_command)

simulate_parser = subparsers.add_parser("simulate", help="Simulate a Corth program")
simulate_parser.add_argument("source", help="Source file name")
simulate_parser.set_defaults(func=simulate_command)

test_parser = subparsers.add_parser("test", help="Run unit tests")
test_parser.set_defaults(func=test_command)

args = parser.parse_args()
args.func()
