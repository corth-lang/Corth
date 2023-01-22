import enum_lib


class Token:
    def __init__(self, type_, arg=None):
        self.type = type_
        self.arg = arg

    def __repr__(self):
        if self.arg is None:
            return f"type='{self.type}'"

        else:
            return f"type='{self.type}' ({self.arg})"


# -- TOKEN TYPES --
enum_lib.reset()
PUSH1 = enum_lib.step()
PUSH2 = enum_lib.step()
PUSH4 = enum_lib.step()
PUSH8 = enum_lib.step()
PUSHSTR = enum_lib.step()
KEYWORDS = {
    "+": (ADD := enum_lib.step()),
    "-": (SUB := enum_lib.step()),
    "dump": (DUMP := enum_lib.step()),
    "dumpchar": (DUMPCHAR := enum_lib.step()),
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
    "read8": (READ8 := enum_lib.step()),
    "write8": (WRITE8 := enum_lib.step())
}

