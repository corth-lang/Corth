import enum_lib
import token_lib
import log_lib



# -- MODES --
enum_lib.reset()
EXPECT_IDLE_MODE = enum_lib.step()
IDLE_MODE = enum_lib.step()

KEYWORD_MODE = enum_lib.step()

CHAR_MODE = enum_lib.step()
CHAR_ESCAPE_MODE = enum_lib.step()
CHAR_EXPECT_END_MODE = enum_lib.step()

MACRO_ARG_MODE = enum_lib.step()

SLASH_MODE = enum_lib.step()
INLINE_COMMENT_MODE = enum_lib.step()

MULTI_COMMENT_ASTERISK_MODE = enum_lib.step()
MULTI_COMMENT_MODE = enum_lib.step()

ZERO_MODE = enum_lib.step()

BINARY_MODE = enum_lib.step()
OCTAL_MODE = enum_lib.step()
DECIMAL_MODE = enum_lib.step()
HEXADECIMAL_MODE = enum_lib.step()

EXPECT_BINARY_MODE = enum_lib.step()
EXPECT_OCTAL_MODE = enum_lib.step()
EXPECT_HEXADECIMAL_MODE = enum_lib.step()

STRING_MODE = enum_lib.step()
STRING_ESCAPE_MODE = enum_lib.step()
STRING_HEXADECIMAL1_MODE = enum_lib.step()
STRING_HEXADECIMAL2_MODE = enum_lib.step()

# TODO: Add minus
# TODO: Create Parser class
# TODO: Add c-strings

ESCAPES = {
    "n": "\n",
    "s": " ",
    "t": "\t",
    '"': '"',
    "'": "'",
    "b": "\b",
    "\\": "\\"
}

REPLACE = {
    "-": "__minus__",
    "*": "__asterisk__"
}

BINARY_DIGITS = "01"
OCTAL_DIGITS = BINARY_DIGITS + "234567"
DECIMAL_DIGITS = OCTAL_DIGITS + "89"
HEXADECIMAL_DIGITS = DECIMAL_DIGITS + "abcdefABCDEF"

BINARY_FORMAT = "bB"
OCTAL_FORMAT = "oO"
HEXADECIMAL_FORMAT = "xX"

END_OF_TOKEN = " \n\t"


class Parser:
    def __init__(self):
        self.file = None
        self.file_name = None
        self.mode = None
        self.token = None
        self.char = None

        self.line_no = None
        self.col_no = None

        self.errors = 0

        self.program = []
    
    def get_push8(self, base):
        number = int(self.token, base)
        self.syntax_error_if_not(0 <= number <= 0xFFFFFFFFFFFFFFFF, f"Number with base {base} too big for int; got '{self.token}'")
                        
        self.program.append(token_lib.Token(self.get_position(), token_lib.PUSH8, number))
    
    def expect_base(self, allowed_digits, next_mode):        
        if self.char not in allowed_digits:
            self.syntax_error(f"Expected {', '.join(allowed_digits[:-1]) or {allowed_digits[-1]}}; got '{self.char}'")
            self.token += "0"
            self.mode = EXPECT_IDLE_MODE
    
        else:       
            self.token += self.char
            self.mode = next_mode
    
    def parse_base(self, allowed_digits, base):        
        if self.char in END_OF_TOKEN:
            self.get_push8(base)
            self.mode = IDLE_MODE
    
        elif self.char in allowed_digits:
            self.token += self.char
    
        else:
            self.syntax_error(f"Expected {', '.join(allowed_digits)} or EOT; got '{self.char}'")
            self.mode = EXPECT_IDLE_MODE
    
    def get_keyword(self):
        if self.token in token_lib.KEYWORDS:
            self.program.append(token_lib.Token(self.get_position(), token_lib.KEYWORDS[self.token]))

        elif self.token in token_lib.TYPE_NAMES:
            self.program.append(token_lib.Token(self.get_position(), token_lib.TYPE, token_lib.TYPE_NAMES[self.token]))
    
        else:
            for x, y in REPLACE.items():
                self.token = self.token.replace(x, y)
                
            self.program.append(token_lib.Token(self.get_position(), token_lib.NAME, self.token))

    def get_macro_arg(self):
        self.program.append(token_lib.Token(self.get_position(), token_lib.MACRO_ARG, self.token))
    
    def syntax_error(self, error):
        self.errors += 1
        self.log_with_position("ERROR", error)
    
    def syntax_error_if_not(self, condition, error):
        if not condition:
            self.syntax_error(error)
    
    def get_position(self):
        return f"in {self.file_name} at {self.line_no}:{self.col_no}"
    
    def log_with_position(self, type_, message):
        log_lib.log(type_, f"({self.get_position()}) {message}")
    
    def parse_file(self, file_name, debug_mode=False):
        self.file_name = file_name
        
        self.mode = IDLE_MODE
        self.token = ""
    
        self.errors = 0

        self.col_no = 0
        self.line_no = 1

        self.program.clear()
    
        with open(self.file_name) as file:
            while True:            
                self.char = file.read(1)
    
                if self.char == "\n":
                    self.line_no += 1
                    self.col_no = 0
    
                else:
                    self.col_no += 1
    
                if debug_mode:
                    # TODO: Make all self.characters visible
                    self.log_with_position("DEBUG", f"'{self.char}' | {str(self.mode).rjust(2, ' ')} | {self.token}")
    
                if self.char == "":
                    if self.mode in (IDLE_MODE, EXPECT_IDLE_MODE, INLINE_COMMENT_MODE, MULTI_COMMENT_MODE, MULTI_COMMENT_ASTERISK_MODE):
                        pass
    
                    elif self.mode is KEYWORD_MODE:
                        self.get_keyword()
                        
                    elif self.mode is SLASH_MODE:
                        self.get_keyword()
                        
                    elif self.mode in (BINARY_MODE, ZERO_MODE):
                        self.get_push8(2)
    
                    elif self.mode is DECIMAL_MODE:
                        self.get_push8(10)
    
                    elif self.mode is HEXADECIMAL_MODE:
                        self.get_push8(16)
                                            
                    elif self.mode in (CHAR_MODE, CHAR_ESCAPE_MODE, CHAR_EXPECT_END_MODE):
                        self.syntax_error("Reached EOF while parsing a char")
    
                    elif self.mode is EXPECT_BINARY_MODE:
                        self.syntax_error("Reached EOF while parsing a binary number")
    
                    elif self.mode is EXPECT_OCTAL_MODE:
                        self.syntax_error("Reached EOF while parsing an octal number")
    
                    elif self.mode is EXPECT_HEXADECIMAL_MODE:
                        self.syntax_error("Reached EOF while parsing a hexadecimal number")
    
                    else:
                        self.syntax_error(f"Reached EOF in self.mode {self.mode}")
    
                    return
    
                if self.mode is EXPECT_IDLE_MODE:
                    self.syntax_error_if_not(self.char in END_OF_TOKEN, "Expected EOT; got '{self.char}'")
                        
                    self.mode = IDLE_MODE
    
                elif self.mode is IDLE_MODE:
                    if self.char in END_OF_TOKEN:
                        continue

                    elif self.char == "$":
                        self.mode = MACRO_ARG_MODE
                        self.token = "$"
    
                    elif self.char == "0":
                        self.mode = ZERO_MODE
                        self.token = "0"
    
                    elif self.char in DECIMAL_DIGITS:
                        self.mode = DECIMAL_MODE
                        self.token = self.char
    
                    elif self.char == "'":
                        self.mode = CHAR_MODE
    
                    elif self.char == '"':
                        self.mode = STRING_MODE
                        self.token = ""
    
                    elif self.char == "/":
                        self.token = "/"
                        self.mode = SLASH_MODE
    
                    else:
                        self.mode = KEYWORD_MODE
                        self.token = self.char
    
                elif self.mode is ZERO_MODE:
                    if self.char in END_OF_TOKEN:
                        self.get_push8(10)
                        self.mode = IDLE_MODE
    
                    elif self.char in BINARY_FORMAT:
                        self.token = ""
                        self.mode = EXPECT_BINARY_MODE
    
                    elif self.char in OCTAL_FORMAT:
                        self.token = ""
                        self.mode = EXPECT_OCTAL_MODE
    
                    elif self.char in HEXADECIMAL_FORMAT:
                        self.token = ""
                        self.mode = EXPECT_HEXADECIMAL_MODE
                    else:
                        self.syntax_error(f"Expected EOT, b, o or  x; got '{self.char}'")
    
                elif self.mode is EXPECT_BINARY_MODE:
                    self.expect_base(BINARY_DIGITS, BINARY_MODE)
    
                elif self.mode is EXPECT_OCTAL_MODE:
                    self.expect_base(OCTAL_DIGITS, OCTAL_MODE)
                    
                elif self.mode is EXPECT_HEXADECIMAL_MODE:
                    self.expect_base(HEXADECIMAL_DIGITS, HEXADECIMAL_MODE)
    
                elif self.mode is BINARY_MODE:
                    self.parse_base(BINARY_DIGITS, 2)
                    
                elif self.mode is OCTAL_MODE:
                    self.parse_base(OCTAL_DIGITS, 8)
    
                elif self.mode is DECIMAL_MODE:
                    self.parse_base(DECIMAL_DIGITS, 10)           
    
                elif self.mode is HEXADECIMAL_MODE:
                    self.parse_base(HEXADECIMAL_DIGITS, 16)

                elif self.mode is MACRO_ARG_MODE:
                    if self.char in END_OF_TOKEN:
                        self.get_macro_arg()

                        self.mode = IDLE_MODE

                    else:
                        self.token += self.char
                    
                elif self.mode is KEYWORD_MODE:
                    if self.char in END_OF_TOKEN:
                        self.get_keyword()
                            
                        self.mode = IDLE_MODE
    
                    else:
                        self.token += self.char
    
                elif self.mode is CHAR_MODE:
                    self.token = self.char
                    self.mode = CHAR_ESCAPE_MODE if self.char == "\\" else CHAR_EXPECT_END_MODE
    
                elif self.mode is CHAR_ESCAPE_MODE:
                    if self.char not in ESCAPES:
                        self.syntax_error(f"Invalid escape sequence; got \\{self.char}")
                        self.token = "*"
    
                    else:
                        self.token = ESCAPES[self.char]
                        
                    self.mode = CHAR_EXPECT_END_MODE
    
                elif self.mode is CHAR_EXPECT_END_MODE:
                    if self.char != "'":
                        self.syntax_error(f"Only one character expected inside ''")
    
                    else:
                        self.program.append(token_lib.Token(self.get_position(), token_lib.PUSH8, ord(self.token)))
                        
                    self.mode = EXPECT_IDLE_MODE
    
                elif self.mode is SLASH_MODE:
                    if self.char == "/":
                        self.mode = INLINE_COMMENT_MODE
    
                    elif self.char == "*":
                        self.mode = MULTI_COMMENT_MODE
    
                    elif self.char in END_OF_TOKEN:
                        self.get_keyword()

                        self.mode = IDLE_MODE
    
                    else:
                        self.token += self.char
                        self.mode = KEYWORD_MODE
    
                elif self.mode is INLINE_COMMENT_MODE:
                    if self.char == "\n":
                        self.mode = IDLE_MODE
    
                elif self.mode is MULTI_COMMENT_MODE:
                    if self.char == "*":
                        self.mode = MULTI_COMMENT_ASTERISK_MODE
    
                elif self.mode is MULTI_COMMENT_ASTERISK_MODE:
                    self.mode = (EXPECT_IDLE_MODE if self.char == "/" else MULTI_COMMENT_MODE)
    
                elif self.mode is STRING_MODE:
                    if self.char == '"':
                        self.mode = EXPECT_IDLE_MODE
                        self.program.append(token_lib.Token(self.get_position(), token_lib.PUSHSTR, self.token))
    
                    elif self.char == "\\":
                        self.mode = STRING_ESCAPE_MODE
    
                    else:
                        self.token += self.char
    
                elif self.mode is STRING_ESCAPE_MODE:
                    if self.char == "x":
                        self.mode = STRING_HEXADECIMAL1_MODE
                        
                    elif self.char not in ESCAPES:
                        self.syntax_error(f"Invalid escape sequence; got \\{self.char}")
                        self.token += "*"
                        self.mode = STRING_MODE
    
                    else:
                        self.token += ESCAPES[self.char]
                        self.mode = STRING_MODE
    
                elif self.mode is STRING_HEXADECIMAL1_MODE:
                    if self.char not in HEXADECIMAL_DIGITS:
                        self.syntax_error(f"Expected a hexadecimal in string hexadecimal expression; got {self.char}")
                        self.token += "0"
    
                    else:
                        self.token += self.char
    
                    self.mode = STRING_HEXADECIMAL2_MODE
    
                elif self.mode is STRING_HEXADECIMAL2_MODE:
                    if self.char not in HEXADECIMAL_DIGITS:
                        self.syntax_error(f"Expected a hexadecimal in string hexadecimal expression; got {self.char}")
                        self.token += "0"
    
                    else:
                        self.token += self.char
    
                    self.token = self.token[:-2] + chr(int(self.token[-2:], 16))
                    
                    self.mode = STRING_MODE
    
                else:
                    self.syntax_error(f"Unknown mode, {self.mode}")
    
