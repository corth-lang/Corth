import enum_lib
import data_types_lib


class Token:
    def __init__(self, address, type_, arg=None):
        self.address = address
        self.type = type_
        self.arg = arg

    def __repr__(self):
        if self.arg is None:
            return f"type='{self.type}'"

        else:
            return f"type='{self.type}' ({self.arg})"

    def copy(self):
        return Token(self.address, self.type, self.arg)


# TODO: Add syscalls from 4 to 6

# -- TOKEN TYPES --
enum_lib.reset()
PUSH8 = enum_lib.step()
PUSHSTR = enum_lib.step()
PUSHSTRC = enum_lib.step()
NAME = enum_lib.step()
TYPE = enum_lib.step()
KEYWORDS = {
    # Arithmetic operators
    "+": (ADD := enum_lib.step()),
    "-": (SUB := enum_lib.step()),
    "*": (MUL := enum_lib.step()),
    "*2": (MUL2 := enum_lib.step()),
    "**": (FULLMUL := enum_lib.step()),
    "u*": (UMUL := enum_lib.step()),
    "u*2": (UMUL2 := enum_lib.step()),
    "u**": (UFULLMUL := enum_lib.step()),
    "/%": (DIVMOD := enum_lib.step()),
    "/": (DIV := enum_lib.step()),
    "%": (MOD := enum_lib.step()),
    "u/%": (UDIVMOD := enum_lib.step()),
    "u/": (UDIV := enum_lib.step()),
    "u%": (UMOD := enum_lib.step()),

    # Bitwise operators
    "&&": (BAND := enum_lib.step()),
    "||": (BOR := enum_lib.step()),
    "^^": (BXOR := enum_lib.step()),
    "!!": (BNOT := enum_lib.step()),
    "<<32": (SHIFTL32 := enum_lib.step()),
    ">>32": (SHIFTR32 := enum_lib.step()),
    "<<4": (SHIFTL4 := enum_lib.step()),
    ">>4": (SHIFTR4 := enum_lib.step()),

    # Quick arithmetics
    "inc": (INC := enum_lib.step()),
    "dec": (DEC := enum_lib.step()),

    # Outer keywords
    "include": (INCLUDE := enum_lib.step()),
    "memory": (MEMORY := enum_lib.step()),
    "macro": (MACRO := enum_lib.step()),
    "endmacro": (ENDMACRO := enum_lib.step()),
    "proc": (PROC := enum_lib.step()),
    "--": (RETURNS := enum_lib.step()),
    "in": (IN := enum_lib.step()),

    # In procedure keywords
    "if": (IF := enum_lib.step()),
    "end": (END := enum_lib.step()),
    "else": (ELSE := enum_lib.step()),
    "while": (WHILE := enum_lib.step()),
    "do": (DO := enum_lib.step()),
    "break": (BREAK := enum_lib.step()),

    # Stack operators
    "dup": (DUP := enum_lib.step()),
    "swp": (SWP := enum_lib.step()),
    "rot": (ROT := enum_lib.step()),
    "drop": (DROP := enum_lib.step()),

    # Comparison operators
    "=": (EQUAL := enum_lib.step()),
    "!=": (NOT_EQUAL := enum_lib.step()),
    "<": (LESS_THAN := enum_lib.step()),
    ">": (GREATER_THAN := enum_lib.step()),
    "<=": (LESS_EQUAL := enum_lib.step()),
    ">=": (GREATER_EQUAL := enum_lib.step()),

    # Boolean artihmetic
    "&": (LAND := enum_lib.step()),  # Not implemented in the compiler yet
    "|": (LOR := enum_lib.step()),  # Not implemented in the compiler yet
    "^": (LXOR := enum_lib.step()),  # Not implemented in the compiler yet
    "!": (NOT := enum_lib.step()),
    "false": (FALSE := enum_lib.step()),
    "true": (TRUE := enum_lib.step()),

    # Memory operators
    "load": (LOAD := enum_lib.step()),
    "store": (STORE := enum_lib.step()),
    "load8": (LOAD8 := enum_lib.step()),
    "store8": (STORE8 := enum_lib.step()),

    # System calls
    "syscall0": (SYSCALL0 := enum_lib.step()),
    "syscall1": (SYSCALL1 := enum_lib.step()),
    "syscall2": (SYSCALL2 := enum_lib.step()),
    "syscall3": (SYSCALL3 := enum_lib.step()),

    # Debug tools
    # These don't have an effect on the compiled program, but helps to debug programs
    "?stack": (DEBUG_STACK := enum_lib.step()),
}
TYPE_NAMES = {
    "int": data_types_lib.INT,
    "bool": data_types_lib.BOOL,
}

