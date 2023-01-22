from collections import deque

import enum_lib
import token_lib


# TODO: Change the compiler, so that it considers types of arguments
# TODO: Add comparison operators


enum_lib.reset()
QWORD = enum_lib.step()
BOOL = enum_lib.step()

            
def compile_nasm_program(file_name, program, debug_mode=False):
    start_level = 0
    levels = deque()

    stack = deque()
   
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
            if debug_mode:
                print(f"{repr(token).ljust(20, ' ')} | {stack}")
            
            if token.type is token_lib.PUSH8:
                file.write("    " * len(levels) + f"    ;; -- PUSH {token.arg} --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, {token.arg}\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

                stack.append(QWORD)

            elif token.type is token_lib.ADD:
                assert stack.pop() is QWORD and stack[-1] is QWORD, "ADD expects two QWORDs"
                
                file.write("    " * len(levels) + f"    ;; -- ADD --\n\n")
                file.write("    " * len(levels) + f"    pop     rbx\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    add     rax, rbx\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

            elif token.type is token_lib.SUB:
                assert stack.pop() is QWORD and stack[-1] is QWORD, "SUB expects two QWORDs"
                
                file.write("    " * len(levels) + f"    ;; -- SUB --\n\n")
                file.write("    " * len(levels) + f"    pop     rbx\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    sub     rax, rbx\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

            elif token.type is token_lib.DUMP:
                assert stack.pop() is QWORD, "DUMP expects a QWORD"
                
                file.write("    " * len(levels) + f"    ;; -- DUMP --\n\n")
                file.write("    " * len(levels) + f"    pop     rdi\n")
                file.write("    " * len(levels) + f"    call    dump\n\n")

            elif token.type is token_lib.DUMPCHAR:
                assert stack.pop() is QWORD, "DUMPCHAR expects a QWORD"
                
                file.write("    " * len(levels) + f"    ;; -- DUMPCHAR --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, 1\n")
                file.write("    " * len(levels) + f"    mov     rdi, 1\n")
                file.write("    " * len(levels) + f"    mov     rsi, rsp\n")
                file.write("    " * len(levels) + f"    mov     rdx, 1\n")
                file.write("    " * len(levels) + f"    add     rsp, 8\n")
                file.write("    " * len(levels) + f"    syscall\n\n")

            elif token.type is token_lib.DUP:
                # TODO: DUP should allow any argument
                assert stack[-1] is QWORD, "DUP expects a QWORD"
                stack.append(QWORD)
                
                file.write("    " * len(levels) + f"    ;; -- DUP --\n\n")
                file.write("    " * len(levels) + f"    push    QWORD [rsp]\n\n")

            elif token.type is token_lib.SWP:
                # TODO: SWP should allow any arguments
                assert stack[-1] is QWORD and stack[-2] is QWORD, "SWP expects two QWORDs"
                
                file.write("    " * len(levels) + f"    ;; -- SWP --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    xchg    rax, [rsp]\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

            elif token.type is token_lib.IF:
                assert stack.pop() in (QWORD, BOOL), "IF expects a QWORD or a BOOL"
                
                file.write("    " * len(levels) + f"    ;; -- IF ({start_level}) --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    test    rax, rax\n")
                file.write("    " * len(levels) + f"    je      .L{start_level}\n\n")

                levels.append((start_level, token_lib.IF, stack.copy()))  # Save the level and a copy of the stack
                start_level += 1

            elif token.type is token_lib.ELSE:
                assert len(levels), "Invalid syntax"
               
                level, start, old_stack = levels.pop()

                assert start is token_lib.IF, f"Invalid syntax, tried to end '{start}' with ELSE"
               
                file.write("    " * len(levels) + f"    ;; -- ELSE ({level}, {start_level}) --\n\n")
                file.write("    " * len(levels) + f"    jmp     .L{start_level}\n")
                file.write("    " * len(levels) + f"    .L{level}:\n\n")

                levels.append((start_level, token_lib.ELSE, stack))  # Add the new stack, no need to copy
                stack = old_stack  # And change the stack to the new one
                start_level += 1

            elif token.type is token_lib.END:
                assert len(levels), "Invalid syntax"
               
                level, start, old_stack = levels.pop()

                if start in (token_lib.IF, token_lib.ELSE):
                    assert old_stack == stack, "In an if-end, there should not be any change in stack"
                    
                    file.write("    " * len(levels) + f"    ;; -- ENDIF ({level}) --\n\n")
                    file.write("    " * len(levels) + f"    .L{level}:\n\n")

                elif start is token_lib.DO:
                    level2, start2, old_stack2 = levels.pop()

                    assert start2 is token_lib.WHILE, "Invalid syntax"
                    assert stack == old_stack2, "In a while-end, there should not be any change in stack"
                    
                    file.write("    " * len(levels) + f"    ;; -- ENDWHILE ({level2}, {level}) --\n\n")
                    file.write("    " * len(levels) + f"    jmp     .L{level2}\n")
                    file.write("    " * len(levels) + f"    .L{level}:\n\n")

                elif start is token_lib.WHILE:
                    assert False, f"You probably forgot to add DO (while COND do CODE end)"

                else:
                    assert False, f"Unknown starter for END; got '{start}'"

            elif token.type is token_lib.WHILE:                
                file.write("    " * len(levels) + f"    ;; -- WHILE ({start_level}) --\n\n")
                file.write("    " * len(levels) + f"    .L{start_level}:\n\n")

                levels.append((start_level, token_lib.WHILE, stack.copy()))
                start_level += 1

            elif token.type is token_lib.DO:
                assert stack.pop() in (QWORD, BOOL), "DO expects a QWORD or a BOOL"
                
                file.write("    " * len(levels) + f"    ;; -- DO ({start_level}) --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    test    rax, rax\n")
                file.write("    " * len(levels) + f"    je      .L{start_level}\n\n")

                levels.append((start_level, token_lib.DO, None))
                start_level += 1

            elif token.type is token_lib.INC:
                assert stack[-1] is QWORD, "INC expects a QWORD"
                
                file.write("    " * len(levels) + f"    ;; -- INC --\n\n")
                file.write("    " * len(levels) + f"    inc     QWORD [rsp]\n\n")

            elif token.type is token_lib.DEC:
                assert stack[-1] is QWORD, "DEC expects a QWORD"
                                
                file.write("    " * len(levels) + f"    ;; -- DEC --\n\n")
                file.write("    " * len(levels) + f"    dec     QWORD [rsp]\n\n")

            elif token.type is token_lib.ROT:
                # TODO: ROT should allow any argument
                assert stack[-1] is QWORD and stack[-2] is QWORD and stack[-3] is QWORD, "ROT expects three QWORDS"
                
                file.write("    " * len(levels) + f"    ;; -- ROT --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, [rsp + 16]\n")
                file.write("    " * len(levels) + f"    xchg    rax, [rsp]\n")
                file.write("    " * len(levels) + f"    xchg    rax, [rsp + 8]\n")
                file.write("    " * len(levels) + f"    mov     [rsp + 16], rax\n\n")

            elif token.type is token_lib.DROP:
                # TODO: DROP should allow any argument
                assert stack.pop() is QWORD, "DROP expects a QWORD"
                
                file.write("    " * len(levels) + f"    ;; -- DROP -- \n\n")
                file.write("    " * len(levels) + f"    add     rsp, 8\n\n")

            elif token.type is token_lib.BREAK:
                copy = levels.copy()
                copy.reverse()
                
                for level, start, old_stack in copy:
                    if start is token_lib.DO:
                        break

                else:
                    assert False, f"BREAK should be used inside WHILE"
                
                file.write("    " * len(levels) + f"    ;; -- BREAK ({level}) --\n\n")
                file.write("    " * len(levels) + f"    jmp     .L{level}\n\n")

            elif token.type is token_lib.EQUAL:
                assert stack.pop() is QWORD and stack.pop() is QWORD, "EQUAL expects two QWORDs"
                stack.append(BOOL)
                
                file.write("    " * len(levels) + f"    ;; -- EQUAL --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    pop     rbx\n")
                file.write("    " * len(levels) + f"    sub     rax, rbx\n")
                file.write("    " * len(levels) + f"    pushf\n")
                file.write("    " * len(levels) + f"    and     QWORD [rsp], 0x40\n\n")

            elif token.type is token_lib.NOT_EQUAL:
                assert stack.pop() is QWORD and stack.pop() is QWORD, "NOT_EQUAL expects two QWORDs"
                stack.append(BOOL)
                
                file.write("    " * len(levels) + f"    ;; -- NOT EQUAL --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    sub     [rsp], rax\n\n")

            elif token.type is token_lib.NOT:
                assert stack.pop() in (QWORD, BOOL), "NOT expects a QWORD or a BOOL"
                stack.append(BOOL)

                file.write("    " * len(levels) + f"    ;; -- NOT --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    test    rax, rax\n")
                file.write("    " * len(levels) + f"    pushf\n")
                file.write("    " * len(levels) + f"    and     QWORD [rsp], 0x40\n\n")

            elif token.type is token_lib.FALSE:
                stack.append(BOOL)

                file.write("    " * len(levels) + f"    ;; -- FALSE --\n\n")
                file.write("    " * len(levels) + f"    xor     rax, rax\n")
                file.write("    " * len(levels) + f"    push    rax\n\n") 

            elif token.type is token_lib.TRUE:
                stack.append(BOOL)

                file.write("    " * len(levels) + f"    ;; -- TRUE --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, 1\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

            elif token.type is token_lib.QWORD:
                old = stack.pop()
                
                if old.type is BOOL:
                    # For false, returns 0
                    # For true, returns 0x40 (64)
                    
                    file.write("    " * len(levels) + f"    ;; -- QWORD (BOOL) --\n\n")
                    file.write("    " * len(levels) + f"    pop     rax\n")
                    file.write("    " * len(levels) + f"    test    rax, rax\n")
                    file.write("    " * len(levels) + f"    pushf\n")
                    file.write("    " * len(levels) + f"    and     QWORD [rsp], 0x40\n\n")

                else:
                    assert False, "Unknown type for QWORD"

            elif token.type is token_lib.BOOL:
                old = stack.pop()

                if old.type is QWORD:
                    # For 0, returns false
                    # For anything else, returns true

                    file.write("    " * len(levels) + f"    ;; -- BOOL (QWORD) --\n\n")
                    file.write("    " * len(levels) + f"    pop     rax\n")
                    file.write("    " * len(levels) + f"    test    rax, rax\n")
                    file.write("    " * len(levels) + f"    pushf\n")
                    file.write("    " * len(levels) + f"    and     QWORD [rsp], 0x40\n\n")
                    file.write("    " * len(levels))

                else:
                    assert False, "Unknown type for BOOL"
               
            else:
                assert False, f"token_lib.Token type {token.type} is unknown."

        assert len(levels) == 0, "There were openers that were not closed"
        assert len(stack) == 0, "There were values in the stack"

        file.write("    mov     rax, 60\n")
        file.write("    mov     rdi, 0\n")
        file.write("    syscall\n")


