from collections import deque

import enum_lib
import token_lib


# TODO: Add type checker
            
def compile_nasm_program(file_name, program):
    start_level = 0
    levels = deque()
   
    with open(file_name, "w") as file:
        file.write("")

    with open(file_name, "a") as file:
        file.write(f"    global  _start\n")
        file.write(f"    segment .text\n")

        file.write("dump:\n")
        file.write("    mov     r9, -3689348814741910323\n")
        file.write("    sub     rsp, 40\n")
        file.write("    mov     BYTE [rsp+31], 10\n")
        file.write("    lea     rcx, [rsp+30]\n")
        file.write(".L2:\n")
        file.write("    mov     rax, rdi\n")
        file.write("    lea     r8, [rsp+32]\n")
        file.write("    mul     r9\n")
        file.write("    mov     rax, rdi\n")
        file.write("    sub     r8, rcx\n")
        file.write("    shr     rdx, 3\n")
        file.write("    lea     rsi, [rdx+rdx*4]\n")
        file.write("    add     rsi, rsi\n")
        file.write("    sub     rax, rsi\n")
        file.write("    add     eax, 48\n")
        file.write("    mov     BYTE [rcx], al\n")
        file.write("    mov     rax, rdi\n")
        file.write("    mov     rdi, rdx\n")
        file.write("    mov     rdx, rcx\n")
        file.write("    sub     rcx, 1\n")
        file.write("    cmp     rax, 9\n")
        file.write("    ja      .L2\n")
        file.write("    lea     rax, [rsp+32]\n")
        file.write("    mov     edi, 1\n")
        file.write("    sub     rdx, rax\n")
        file.write("    xor     eax, eax\n")
        file.write("    lea     rsi, [rsp+32+rdx]\n")
        file.write("    mov     rdx, r8\n")
        file.write("    mov	    rax, 1\n")
        file.write("    syscall\n")
        file.write("    add     rsp, 40\n")
        file.write("    ret\n\n")
        file.write("_start:\n")

        for token in program:
            if token.type is token_lib.PUSH8:
                file.write("    " * len(levels) + f"    ;; -- PUSH {token.arg} --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, {token.arg}\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

            elif token.type is token_lib.ADD:
                file.write("    " * len(levels) + f"    ;; -- ADD --\n\n")
                file.write("    " * len(levels) + f"    pop     rbx\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    add     rax, rbx\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

            elif token.type is token_lib.SUB:
                file.write("    " * len(levels) + f"    ;; -- SUB --\n\n")
                file.write("    " * len(levels) + f"    pop     rbx\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    sub     rax, rbx\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

            elif token.type is token_lib.DUMP:
                file.write("    " * len(levels) + f"    ;; -- DUMP --\n\n")
                file.write("    " * len(levels) + f"    pop     rdi\n")
                file.write("    " * len(levels) + f"    call    dump\n\n")

            elif token.type is token_lib.DUMPCHAR:
                file.write("    " * len(levels) + f"    ;; -- DUMPCHAR --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, 1\n")
                file.write("    " * len(levels) + f"    mov     rdi, 1\n")
                file.write("    " * len(levels) + f"    mov     rsi, rsp\n")
                file.write("    " * len(levels) + f"    mov     rdx, 1\n")
                file.write("    " * len(levels) + f"    add     rsp, 8\n")
                file.write("    " * len(levels) + f"    syscall\n\n")

            elif token.type is token_lib.DUP:
                file.write("    " * len(levels) + f"    ;; -- DUP --\n\n")
                file.write("    " * len(levels) + f"    push    QWORD [rsp]\n\n")

            elif token.type is token_lib.SWP:
                file.write("    " * len(levels) + f"    ;; -- SWP --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    xchg    rax, [rsp]\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

            elif token.type is token_lib.IF:
                file.write("    " * len(levels) + f"    ;; -- IF ({start_level}) --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    cmp     rax, 0\n")
                file.write("    " * len(levels) + f"    je      .L{start_level}\n\n")

                levels.append((start_level, token_lib.IF))  # Save the level
                start_level += 1

            elif token.type is token_lib.ELSE:
                assert len(levels), "Invalid syntax"
               
                level, start = levels.pop()

                assert start is token_lib.IF, f"Invalid syntax, tryed to end '{start}' with ELSE"
               
                file.write("    " * len(levels) + f"    ;; -- ELSE ({level}, {start_level}) --\n\n")
                file.write("    " * len(levels) + f"    jmp     .L{start_level}\n")
                file.write("    " * len(levels) + f"    .L{level}:\n\n")

                levels.append((start_level, token_lib.ELSE))
                start_level += 1

            elif token.type is token_lib.END:
                assert len(levels), "Invalid syntax"
               
                level, start = levels.pop()

                if start in (token_lib.IF, token_lib.ELSE):
                    file.write("    " * len(levels) + f"    ;; -- ENDIF ({level}) --\n\n")
                    file.write("    " * len(levels) + f"    .L{level}:\n\n")

                elif start is token_lib.DO:
                    level2, start2 = levels.pop()

                    assert start2 is token_lib.WHILE, "Invalid syntax"
                    
                    file.write("    " * len(levels) + f"    ;; -- ENDWHILE ({level2}, {level}) --\n\n")
                    file.write("    " * len(levels) + f"    jmp     .L{level2}\n")
                    file.write("    " * len(levels) + f"    .L{level}:\n\n")

                elif start is token_lib.WHILE:
                    assert False, f"You probably forgot a do"

                else:
                    assert False, f"Unknown starter for END; got '{start}'"

            elif token.type is token_lib.WHILE:
                file.write("    " * len(levels) + f"    ;; -- WHILE ({start_level}) --\n\n")
                file.write("    " * len(levels) + f"    .L{start_level}:\n\n")

                levels.append((start_level, token_lib.WHILE))
                start_level += 1

            elif token.type is token_lib.DO:
                file.write("    " * len(levels) + f"    ;; -- DO ({start_level}) --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    cmp     rax, 0\n")
                file.write("    " * len(levels) + f"    je      .L{start_level}\n\n")

                levels.append((start_level, token_lib.DO))
                start_level += 1

            elif token.type is token_lib.INC:
                file.write("    " * len(levels) + f"    ;; -- INC --\n\n")
                file.write("    " * len(levels) + f"    inc     QWORD [rsp]\n\n")

            elif token.type is token_lib.DEC:
                file.write("    " * len(levels) + f"    ;; -- DEC --\n\n")
                file.write("    " * len(levels) + f"    dec     QWORD [rsp]\n\n")

            elif token.type is token_lib.ROT:
                file.write("    " * len(levels) + f"    ;; -- ROT --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, [rsp + 16]\n")
                file.write("    " * len(levels) + f"    xchg    rax, [rsp]\n")
                file.write("    " * len(levels) + f"    xchg    rax, [rsp + 8]\n")
                file.write("    " * len(levels) + f"    mov     [rsp + 16], rax\n\n")

            elif token.type is token_lib.DROP:
                file.write("    " * len(levels) + f"    ;; -- DROP -- \n\n")
                file.write("    " * len(levels) + f"    add     rsp, 8")
               
            else:
                assert False, f"token_lib.Token type {token.type} is unknown."

        assert len(levels) == 0, "Invalid syntax"

        file.write("    mov     rax, 60\n")
        file.write("    mov     rdi, 0\n")
        file.write("    syscall\n")


