from collections import deque
import subprocess


last_token_id = 0
basic_tokens = {}

def create_token_type():
    global last_token_id

    last_token_id += 1
    return last_token_id - 1


def create_basic_token(name, nasm_code):
    assert (name not in basic_tokens), f"{name} was already saved as a basic token"

    basic_tokens[name] = f"    ;; -- {name} --\n" + nasm_code
    

BASIC_TOKEN = create_token_type()
PUSH_TOKEN = create_token_type()

create_basic_token("+", f"""
    pop     rax
    pop     rbx
    add     rax, rbx
    push    rax
""")
create_basic_token("-", f"""
    pop     rbx
    pop     rax
    sub     rax, rbx
    push    rax
""")
create_basic_token("dump", f"""
    pop     rdi
    call    dump
""")
create_basic_token("dup", f"""
    pop     rax
    push    rax
    push    rax
""")
create_basic_token("swp", f"""
    pop     rax
    pop     rbx
    push    rax
    push    rbx
""")



class Token:
    def __init__(self, address, type_, arg=None):
        self.address = address  # Used for debugging
        self.type = type_
        self.arg = arg

    def __repr__(self):
        if self.value is None:
            return f"[{self.address}] type='{self.type}'"

        else:
            return f"[{self.address}] type='{self.type}' ({self.value})"


class Corth:
    def __init__(self):
        self.program = []

    def parse_file(self, file_name):
        self.program.clear()

        line_no = 1
        char_no = 1

        token = ""

        token_line_no = 1
        token_char_no = 1
        
        with open(file_name) as file:
            while True:
                char = file.read(1)

                if char == "":
                    self.create_token(token, file_name, line_no, token_char_no, char_no)
                    break

                if char in " \n\t":
                    self.create_token(token, file_name, line_no, token_char_no, char_no)
                    
                    token = ""

                    if char == "\n":
                        line_no += 1
                        char_no = 0

                else:
                    token += char

                char_no += 1

    def create_token(self, token, file_name, line_no, token_char_no, char_no):
        if token == "":
            return
        
        if token[0] in "0123456789":
            if token_char_no == char_no:
                address = f"in {file_name}, at .{line_no} {char_no}"

            else:
                address = f"in {file_name}, at .{line_no} {token_char_no}-{char_no}"

            self.program.append(Token(address, PUSH_TOKEN, int(token)))

        else:
            assert (token in basic_tokens), f"'{token}' is unknown"

            if token_char_no == char_no:
                address = f"in {file_name}, at .{line_no} {char_no}"

            else:
                address = f"in {file_name}, at .{line_no} {token_char_no}-{char_no}"

            self.program.append(Token(address, BASIC_TOKEN, token))

    def simulate_program(self):
        stack = deque()
        
        for token in self.program:
            if token.type is PUSH_TOKEN:
                stack.append(token.arg)

            elif token.type is BASIC_TOKEN:
                assert False, f"Simulating basic tokens is not implemented yet"

            else:
                assert False, f"Token type {token.type} is unknown.\nToken: {token}"

    def compile_nasm_program(self, output_name):
        compiled = """	
    global  _start
    segment .text

dump:
    mov	r9, -3689348814741910323
    sub     rsp, 40
    mov     BYTE [rsp+31], 10
    lea     rcx, [rsp+30]
.L2:
    mov     rax, rdi
    lea     r8, [rsp+32]
    mul     r9
    mov     rax, rdi
    sub     r8, rcx
    shr     rdx, 3
    lea     rsi, [rdx+rdx*4]
    add     rsi, rsi
    sub     rax, rsi
    add     eax, 48
    mov     BYTE [rcx], al
    mov     rax, rdi
    mov     rdi, rdx
    mov     rdx, rcx
    sub     rcx, 1
    cmp     rax, 9
    ja      .L2
    lea     rax, [rsp+32]
    mov     edi, 1
    sub     rdx, rax
    xor     eax, eax
    lea     rsi, [rsp+32+rdx]
    mov     rdx, r8
    mov	    rax, 1
    syscall
    add     rsp, 40
    ret

_start:
"""

        for token in self.program:
            if token.type is PUSH_TOKEN:
                compiled += f"""
    ;; -- PUSH {token.arg} --
    mov     rax, {token.arg}
    push    rax
"""
                
            elif token.type is BASIC_TOKEN:
                compiled += basic_tokens[token.arg]
                
            else:
                assert False, f"({token.address}) Token type {token.type} is unknown."

        compiled += """
    mov     rax, 60
    mov     rdi, 0
    syscall
"""

        with open(output_name, "w") as file:
            file.write(compiled)

        log("CMP", "Successfully compiled to NASM.")


def print_tokens(input_name):
    corth = Corth()

    corth.parse_file(input_name)
    print(*corth.program, sep="\n")


def compile_nasm_program(input_name, output_name):
    corth = Corth()

    corth.parse_file(input_name)
    corth.compile_nasm_program(output_name)

        
def compile_program(input_name, output_name):
    command(("python3", "main.py", "compile-nasm", input_name, "-o", "output.asm"))
    command(("nasm", "output.asm", "-f", "elf64", "-o", "output.o"))
    command(("rm", "output.asm"))
    command(("ld", "output.o", "-o", output_name))
    command(("rm", "output.o"))

    
def log(type_, message):
    print(f"[{type_}] {message}")

        
def command(command):
    log("CMD", command)
    subprocess.run(command)    
