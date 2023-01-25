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


# TODO: Add syscalls from 0 to 6

# -- TOKEN TYPES --
enum_lib.reset()
PUSH1 = enum_lib.step()
PUSH2 = enum_lib.step()
PUSH4 = enum_lib.step()
PUSH8 = enum_lib.step()
PUSHSTR = enum_lib.step()
PUSHSTRC = enum_lib.step()
NAME = enum_lib.step()
TYPE = enum_lib.step()
KEYWORDS = {
    "+": (ADD := enum_lib.step()),
    "-": (SUB := enum_lib.step()),
    "dump": (DUMP := enum_lib.step()),  # Should be removed and remade in Corth
    "dup": (DUP := enum_lib.step()),
    "swp": (SWP := enum_lib.step()),
    "if": (IF := enum_lib.step()),
    "end": (END := enum_lib.step()),
    "else": (ELSE := enum_lib.step()),
    "while": (WHILE := enum_lib.step()),
    "do": (DO := enum_lib.step()),
    "inc": (INC := enum_lib.step()),
    "dec": (DEC := enum_lib.step()),
    "rot": (ROT := enum_lib.step()),
    "drop": (DROP := enum_lib.step()),
    "break": (BREAK := enum_lib.step()),
    "=": (EQUAL := enum_lib.step()),
    "!=": (NOT_EQUAL := enum_lib.step()),
    "!": (NOT := enum_lib.step()),
    "false": (FALSE := enum_lib.step()),
    "true": (TRUE := enum_lib.step()),
    "qword": (QWORD := enum_lib.step()),
    "bool": (BOOL := enum_lib.step()),
    "addr": (ADDR := enum_lib.step()),
    "load8": (LOAD8 := enum_lib.step()),
    "store8": (STORE8 := enum_lib.step()),
    "syscall0": (SYSCALL0 := enum_lib.step()),
    "syscall1": (SYSCALL1 := enum_lib.step()),
    "syscall2": (SYSCALL2 := enum_lib.step()),
    "syscall3": (SYSCALL3 := enum_lib.step()),
    "include": (INCLUDE := enum_lib.step()),
    "proc": (PROC := enum_lib.step()),
    "returns": (RETURNS := enum_lib.step()),
    "in": (IN := enum_lib.step()),
}
TYPE_NAMES = {
    "word-type": data_types_lib.WORD,
    "dword-type": data_types_lib.DWORD,
    "qword-type": data_types_lib.QWORD,
    "bool-type": data_types_lib.BOOL,
}

