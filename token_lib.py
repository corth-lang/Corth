import enum_lib


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
MACRO_ARG = enum_lib.step()
KEYWORDS = {
    # Outer keywords
    "include": (INCLUDE := enum_lib.step()),
    "memory": (MEMORY := enum_lib.step()),
    "and": (AND := enum_lib.step()),
    "macro": (MACRO := enum_lib.step()),
    "endmacro": (ENDMACRO := enum_lib.step()),
    "proc": (PROC := enum_lib.step()),
    "--": (RETURNS := enum_lib.step()),
    "in": (IN := enum_lib.step()),
    "return": (RETURN := enum_lib.step()),

    # In procedure keywords
    "if": (IF := enum_lib.step()),
    "end": (END := enum_lib.step()),
    "else": (ELSE := enum_lib.step()),
    "while": (WHILE := enum_lib.step()),
    "do": (DO := enum_lib.step()),
    "break": (BREAK := enum_lib.step()),
    "let": (LET := enum_lib.step()),
    
    # Arithmetic operators
    "+": (ADD := enum_lib.step()),

    # Signed operations
    "**": (FULLMUL := enum_lib.step()),
    "/%": (DIVMOD := enum_lib.step()),

    # Unsigned operations
    "u**": (UFULLMUL := enum_lib.step()),
    "u/%": (UDIVMOD := enum_lib.step()),

    # Bitwise operators
    "||": (BOR := enum_lib.step()),
    "!!": (BNOT := enum_lib.step()),

    # Comparison operators
    "!=": (NOT_EQUAL := enum_lib.step()),
    "<": (LESS_THAN := enum_lib.step()),

    # Boolean singletons
    "false": (FALSE := enum_lib.step()),
    "true": (TRUE := enum_lib.step()),

    # Memory operators
    "@8": (LOAD := enum_lib.step()),
    "!8": (STORE := enum_lib.step()),
    "@64": (LOAD8 := enum_lib.step()),
    "!64": (STORE8 := enum_lib.step()),

    # System calls
    "syscall6": (SYSCALL6 := enum_lib.step()),

    # Debug tools
    # These don't have an effect on the compiled program, but helps to debug programs
    "?stack": (DEBUG_STACK := enum_lib.step()),
}
TYPE_NAMES = {
    "int": 0,
    "bool": 1,
}

