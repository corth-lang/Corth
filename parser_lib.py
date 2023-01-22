import enum_lib
import token_lib



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
DECIMAL_MODE = enum_lib.step()

BINARY_MODE = enum_lib.step()
EXPECT_HEXADECIMAL_MODE = enum_lib.step()

HEXADECIMAL_MODE = enum_lib.step()
EXPECT_BINARY_MODE = enum_lib.step()

STRING_MODE = enum_lib.step()
STRING_MODE_ESCAPE_MODE = enum_lib.step()

# TODO: Add minus
# TODO: Add different size numbers

ESCAPES = {
    "n": "\n",
    "s": " ",
    "t": "\t",
    '"': '"',
    "'": "'"
}


def parse_file(file_name, debug_mode=False):
    mode = IDLE_MODE
    token = ""

    with open(file_name) as file:
        while True:            
            char = file.read(1)

            if debug_mode:
                # TODO: Make all characters visible
                print(f"'{char}' | {str(mode).rjust(2, ' ')} | {token}")

            if char == "":
                if mode in (IDLE_MODE, EXPECT_IDLE_MODE, INLINE_COMMENT_MODE, MULTI_COMMENT_MODE, MULTI_COMMENT_ASTERISK_MODE):
                    return

                elif mode is KEYWORD:
                    yield token_lib.Token(token_lib.KEYWORD, token)

                elif mode in (CHAR_MODE, CHAR_ESCAPE_MODE, CHAR_EXPECT_END_MODE):
                    assert False, "Reached EOF while parsing a char"
                    
                elif mode is SLASH_MODE:
                    yield token_lib.Token(token_lib.KEYWORD, "/")

                elif mode is ZERO_MODE:
                    yield token_lib.Token(token_lib.PUSH8, 0)

                elif mode is DECIMAL_MODE:
                    yield token_lib.Token(token_lib.PUSH8, int(token))

                elif mode is BINARY_MODE:
                    yield token_lib.Token(token_lib.PUSH8, int(token, 2))

                elif mode is EXPECT_BINARY_MODE:
                    assert False, "Reached EOF while parsing a binary number"

                elif mode is HEXADECIMAL_MODE:
                    yield token_lib.Token(token_lib.PUSH8, int(token, 16))

                elif mode is EXPECT_HEXADECIMAL_MODE:
                    assert False, "Reached EOF while parsing a hexadecimal number"

                else:
                    assert False, f"Reached EOF in mode {mode}"
                    

            if mode is EXPECT_IDLE_MODE:
                assert char in " \n\t", f"Expected end of token; got '{char}'"
                mode = IDLE_MODE

            elif mode is IDLE_MODE:
                if char in " \n\t":
                    continue

                elif char == "0":
                    mode = ZERO_MODE
                    token = ""

                elif char in "123456789":
                    mode = DECIMAL_MODE
                    token = char

                elif char == "'":
                    mode = CHAR_MODE

                elif char == '"':
                    mode = STRING_MODE
                    token = ""

                elif char == "/":
                    mode = SLASH_MODE

                else:
                    mode = KEYWORD_MODE
                    token = char

            elif mode is ZERO_MODE:
                if char in " \n\t":
                    yield token_lib.Token(token_lib.PUSH8, 0)
                    mode = IDLE_MODE

                elif char == "b":
                    mode = EXPECT_BINARY_MODE

                elif char == "x":
                    mode = EXPECT_HEXADECIMAL_MODE

                else:
                    assert False, f"Expected end of token, b or x; got '{char}'"

            elif mode is DECIMAL_MODE:
                if char in " \n\t":
                    yield token_lib.Token(token_lib.PUSH8, int(token))
                    mode = IDLE_MODE

                elif char in "0123456789":
                    token += char

                else:
                    assert False, f"Expected end of token or decimal; got '{char}'"

            elif mode is EXPECT_BINARY_MODE:
                assert char in "01", f"Expected 0 or 1; got '{char}'"
                token += char
                mode = BINARY_MODE

            elif mode is BINARY_MODE:
                if char in "01":
                    token += char

                elif char in " \n\t":
                    program.append(token_lib.Token(token_lib.PUSH8, int(token, 2)))
                    mode = IDLE_MODE

                else:
                    assert False, f"Expected end of token, 0 or 1; got '{char}'"

            elif mode is EXPECT_HEXADECIMAL_MODE:
                assert char in "0123456789ABCDEFabcdef", f"Expected decimal or ABCDEF; got '{char}'"
                token += char
                mode = HEXADECIMAL_MODE

            elif mode is HEXADECIMAL_MODE:
                if char in "0123456789ABCDEFabcdef":
                    token += char

                elif char in " \n\t":
                    yield token_lib.Token(token_lib.PUSH8, int(token, 16))
                    mode = IDLE_MODE

                else:
                    assert False, f"Expected end of token or hexadecimal; got '{char}'"

            elif mode is KEYWORD_MODE:
                if char in " \n\t":
                    assert token in token_lib.KEYWORDS, f"Unknown keyword, '{token}'"

                    yield token_lib.Token(token_lib.KEYWORDS[token])
                    mode = IDLE_MODE

                else:
                    token += char

            elif mode is CHAR_MODE:
                if char == "\\":
                    mode = CHAR_ESCAPE_MODE

                else:
                    token = char
                    mode = CHAR_EXPECT_END_MODE

            elif mode is CHAR_ESCAPE_MODE:
                assert char in ESCAPES, f"Invalid escape sequence; got \\{char}"

                token = ESCAPES[char]
                mode = CHAR_EXPECT_END_MODE

            elif mode is CHAR_EXPECT_END_MODE:
                assert (char == "'"), f"Only one character expected inside ''"

                yield token_lib.Token(token_lib.PUSH8, ord(token))
                mode = EXPECT_IDLE_MODE

            elif mode is SLASH_MODE:
                if char == "/":
                    mode = INLINE_COMMENT_MODE

                elif char == "*":
                    mode = MULTI_COMMENT_MODE

                elif char in " \n\t":
                    yield token_lib.Token(token_lib.KEYWORD, "/")

                else:
                    token = "/" + char
                    mode = KEYWORD_MODE

            elif mode is INLINE_COMMENT_MODE:
                if char in "\n":
                    mode = IDLE_MODE

            elif mode is MULTI_COMMENT_MODE:
                if char == "*":
                    mode = MULTI_COMMENT_ASTERISK_MODE

            elif mode is MULTI_COMMENT_ASTERISK_MODE:
                if char == "/":
                    mode = EXPECT_IDLE_MODE

                else:
                    mode = MULTI_COMMENT_MODE

            elif mode is STRING_MODE:
                if char == '"':
                    mode = EXPECT_IDLE_MODE
                    yield token_lib.Token(token_lib.PUSHSTR, token)

                elif char == "\\":
                    mode = STRING_ESCAPE_MODE

                else:
                    token += char

            elif mode is STRING_ESCAPE_MODE:
                assert char in ESCAPES, f"Invalid escape sequence; got \\{char}"

                token += ESCAPES[char]
                mode = STRING_MODE

            else:
                assert False, f"Mode '{mode}' is unknown"
