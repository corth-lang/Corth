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
STRING_MODE_ESCAPE_MODE = enum_lib.step()

# TODO: Add minus
# TODO: Create Parser class

ESCAPES = {
    "n": "\n",
    "s": " ",
    "t": "\t",
    '"': '"',
    "'": "'"
}

BINARY_DIGITS = "01"
OCTAL_DIGITS = BINARY_DIGITS + "234567"
DECIMAL_DIGITS = OCTAL_DIGITS + "89"
HEXADECIMAL_DIGITS = DECIMAL_DIGITS + "abcdefABCDEF"

WORD_FORMAT = "wW"
DWORD_FORMAT = "uU"

BINARY_FORMAT = "bB"
OCTAL_FORMAT = "oO"
HEXADECIMAL_FORMAT = "xX"

END_OF_TOKEN = " \n\t"

mode = None
token = ""
char = ""

line_no = 1
col_no = 0

file_name = None

errors = 0


def get_push2(base):
    number = int(token)
    syntax_error_if_not(0 <= number <= 0xFFFF, f"Number with base {base} too big for WORD; got '{token}'")
                    
    return token_lib.Token(get_position(), token_lib.PUSH2, number)


def get_push4(base):
    number = int(token)
    syntax_error_if_not(0 <= number <= 0xFFFFFFFF, f"Number with base {base} too big for DWORD; got '{token}'")
                    
    return token_lib.Token(get_position(), token_lib.PUSH4, number)


def get_push8(base):
    number = int(token)
    syntax_error_if_not(0 <= number <= 0xFFFFFFFFFFFFFFFF, f"Number with base {base} too big for QWORD; got '{token}'")
                    
    return token_lib.Token(get_position(), token_lib.PUSH8, number)


def expect_base(allowed_digits, next_mode):
    global token
    global mode
    
    if char not in allowed_digits:
        syntax_error(f"Expected {', '.join(allowed_digits[:-1]) or {allowed_digits[-1]}}; got '{char}'")
        token += "0"
        mode = EXPECT_IDLE_MODE

    else:       
        token += char
        mode = next_mode


def parse_base(allowed_digits, base):
    global mode
    global token
    
    if char in END_OF_TOKEN:
        yield get_push8(base)
        mode = IDLE_MODE

    elif char in allowed_digits:
        token += char

    elif char in WORD_FORMAT:
        yield get_push2(10)
        mode = EXPECT_IDLE_MODE

    elif char in DWORD_FORMAT:
        yield get_push4(10)
        mode = EXPECT_IDLE_MODE

    else:
        syntax_error(f"Expected {', '.join(allowed_digits)} or EOT; got '{char}'")
        mode = EXPECT_IDLE_MODE


def get_keyword():
    if token in token_lib.KEYWORDS:
        return token_lib.Token(get_position(), token_lib.KEYWORDS[token])

    else:
        return token_lib.Token(get_position(), token_lib.NAME, token)


def syntax_error(error):
    global errors
    
    errors += 1
    log_with_position("ERROR", error)


def syntax_error_if_not(condition, error):
    if not condition:
        syntax_error(error)


def get_position():
    return f"in {file_name} at {line_no}:{col_no}"


def log_with_position(type_, message):
    log_lib.log(type_, f"({get_position()}) {message}")


def parse_file(debug_mode=False):
    global mode
    global token
    global char
    global errors

    global line_no, col_no
    
    mode = IDLE_MODE
    token = ""

    errors = 0

    with open(file_name) as file:
        while True:            
            char = file.read(1)

            if char == "\n":
                line_no += 1
                col_no = 0

            else:
                col_no += 1

            if debug_mode:
                # TODO: Make all characters visible
                log_with_position("DEBUG", f"'{char}' | {str(mode).rjust(2, ' ')} | {token}")

            if char == "":
                if mode in (IDLE_MODE, EXPECT_IDLE_MODE, INLINE_COMMENT_MODE, MULTI_COMMENT_MODE, MULTI_COMMENT_ASTERISK_MODE):
                    return

                elif mode is KEYWORD:
                    yield get_keyword()
                    
                elif mode is SLASH_MODE:
                    yield get_keyword()

                elif mode is (BINARY_MODE, ZERO_MODE):
                    yield get_push8(2)

                elif mode in DECIMAL_MODE:
                    yield get_push8(10)

                elif mode is HEXADECIMAL_MODE:
                    yield get_push8(16)

                elif mode in (CHAR_MODE, CHAR_ESCAPE_MODE, CHAR_EXPECT_END_MODE):
                    syntax_error("Reached EOF while parsing a char")

                elif mode is EXPECT_BINARY_MODE:
                    syntax_error("Reached EOF while parsing a binary number")

                elif mode is EXPECT_OCTAL_MODE:
                    syntax_error("Reached EOF while parsing a octal number")

                elif mode is EXPECT_HEXADECIMAL_MODE:
                    syntax_error("Reached EOF while parsing a hexadecimal number")

                else:
                    syntax_error(f"Reached EOF in mode {mode}")
                    

            if mode is EXPECT_IDLE_MODE:
                syntax_error_if_not(char in END_OF_TOKEN, "Expected EOT; got '{char}'")
                    
                mode = IDLE_MODE

            elif mode is IDLE_MODE:
                if char in END_OF_TOKEN:
                    continue

                elif char == "0":
                    mode = ZERO_MODE
                    token = "0"

                elif char in DECIMAL_DIGITS:
                    mode = DECIMAL_MODE
                    token = char

                elif char == "'":
                    mode = CHAR_MODE

                elif char == '"':
                    mode = STRING_MODE
                    token = ""

                elif char == "/":
                    token = "/"
                    mode = SLASH_MODE

                else:
                    mode = KEYWORD_MODE
                    token = char

            elif mode is ZERO_MODE:
                if char in END_OF_TOKEN:
                    yield get_push8(10)
                    mode = IDLE_MODE

                elif char in BINARY_FORMAT:
                    token = ""
                    mode = EXPECT_BINARY_MODE

                elif char in OCTAL_FORMAT:
                    token = ""
                    mode = EXPECT_OCTAL_MODE

                elif char in HEXADECIMAL_FORMAT:
                    token = ""
                    mode = EXPECT_HEXADECIMAL_MODE

                elif char in WORD_FORMAT:
                    yield get_push2(10)
                    mode = EXPECT_IDLE_MODE

                elif char in DWORD_FORMAT:
                    yield get_push4(10)
                    mode = EXPECT_IDLE_MODE

                else:
                    syntax_error(f"Expected EOT, b, o, x, w or u ; got '{char}'")

            elif mode is EXPECT_BINARY_MODE:
                expect_base(BINARY_DIGITS, BINARY_MODE)

            elif mode is EXPECT_OCTAL_MODE:
                expect_base(OCTAL_DIGITS, OCTAL_MODE)
                
            elif mode is EXPECT_HEXADECIMAL_MODE:
                expect_base(HEXADECIMAL_DIGITS, HEXADECIMAL_MODE)

            elif mode is BINARY_MODE:
                yield from parse_base(BINARY_DIGITS, 2)
                
            elif mode is OCTAL_MODE:
                yield from parse_base(OCTAL_DIGITS, 8)

            elif mode is DECIMAL_MODE:
                yield from parse_base(DECIMAL_DIGITS, 10)                

            elif mode is HEXADECIMAL_MODE:
                yield from parse_base(HEXADECIMAL_DIGITS, 16)
                
            elif mode is KEYWORD_MODE:
                if char in END_OF_TOKEN:
                    if token in token_lib.KEYWORDS:
                        yield token_lib.Token(get_position(), token_lib.KEYWORDS[token])

                    else:
                        yield token_lib.Token(get_position(), token_lib.NAME, token)
                        
                    mode = IDLE_MODE

                else:
                    token += char

            elif mode is CHAR_MODE:
                token = char
                mode = CHAR_ESCAPE_MODE if char == "\\" else CHAR_EXPECT_END_MODE

            elif mode is CHAR_ESCAPE_MODE:
                if char not in ESCAPES:
                    syntax_error(f"Invalid escape sequence; got \\{char}")
                    token = "*"

                else:
                    token = ESCAPES[char]
                    
                mode = CHAR_EXPECT_END_MODE

            elif mode is CHAR_EXPECT_END_MODE:
                if char != "'":
                    syntax_error(f"Only one character expected inside ''")

                else:
                    yield token_lib.Token(get_position(), token_lib.PUSH8, ord(token))
                    
                mode = EXPECT_IDLE_MODE

            elif mode is SLASH_MODE:
                if char == "/":
                    mode = INLINE_COMMENT_MODE

                elif char == "*":
                    mode = MULTI_COMMENT_MODE

                elif char in END_OF_TOKEN:
                    yield get_keyword()

                else:
                    token = "/" + char
                    mode = KEYWORD_MODE

            elif mode is INLINE_COMMENT_MODE:
                if char == "\n":
                    mode = IDLE_MODE

            elif mode is MULTI_COMMENT_MODE:
                if char == "*":
                    mode = MULTI_COMMENT_ASTERISK_MODE

            elif mode is MULTI_COMMENT_ASTERISK_MODE:
                mode = (EXPECT_IDLE_MODE if char == "/" else MULTI_COMMENT_MODE)

            elif mode is STRING_MODE:
                if char == '"':
                    mode = EXPECT_IDLE_MODE
                    yield token_lib.Token(get_position(), token_lib.PUSHSTR, token)

                elif char == "\\":
                    mode = STRING_ESCAPE_MODE

                else:
                    token += char

            elif mode is STRING_ESCAPE_MODE:
                if char not in ESCAPES:
                    syntax_error(f"Invalid escape sequence; got \\{char}")
                    token += "*"

                else:
                    token += ESCAPES[char]
                    
                mode = STRING_MODE

            else:
                syntax_error(f"Unknown mode, {mode}")
