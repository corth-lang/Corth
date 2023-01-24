from collections import deque

import typing
import enum_lib
import token_lib
import log_lib


# TODO: Create Compiler class
# TODO: Add comparison operators
# TODO: Add BYTE type
# TODO: Change BOOL type so that it is 1 bytes, not 4
# TODO: Add file operations
# TODO: Remove all error_if_not's in the compiler


enum_lib.reset()
QWORD = enum_lib.step()
BOOL = enum_lib.step()
ADDR = enum_lib.step()


def error(message):
    log_lib.log("ERROR", message)


def error_on_token(token, message):
    error(log_lib.log("ERROR", f"({token.address}) {message}"))


def error_if_not(token, condition, message):
    if not condition:
        error_on_token(token, message)

            
def compile_nasm_program(file_name: str, program: typing.Generator, debug_mode: bool = False, allocate_space: int = 0x4000): 
    start_level = 0
    levels = deque()

    stack = deque()
   
    with open(file_name, "w") as file:
        file.write("")

    with open(file_name, "a") as file:
        file.write(f"global  _start\n")
        file.write(f"segment .text\n\n")

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

        while True:
            try:                
                token = next(program)

            except StopIteration:
                break
            
            if debug_mode:
                log_lib.log("DEBUG", f"{repr(token).ljust(20, ' ')} | {stack}")
            
            if token.type is token_lib.PUSH8:
                file.write("    " * len(levels) + f"    ;; -- PUSH8 {token.arg} --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, {token.arg}\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

                stack.append(QWORD)

            elif token.type is token_lib.ADD:
                if not(stack.pop() in (QWORD, ADDR) and stack[-1] in (QWORD, ADDR)):
                    error_on_token(token, "ADD expects two QWORDs or ADDRs")
                    return True
                
                file.write("    " * len(levels) + f"    ;; -- ADD --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    add     [rsp], rax\n")

            elif token.type is token_lib.SUB:
                if not(stack.pop() in (QWORD, ADDR) and stack[-1] in (QWORD, ADDR)):
                    error_on_token(token, "SUB expects two QWORDs or ADDRs")
                    return True
                
                file.write("    " * len(levels) + f"    ;; -- SUB --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    sub     QWORD [rsp], rax\n")

            elif token.type is token_lib.DUMP:
                if not(stack.pop() in (QWORD, ADDR)):
                    error_on_token(token, "DUMP expects a QWORD or an ADDR")
                    return True
                
                file.write("    " * len(levels) + f"    ;; -- DUMP --\n\n")
                file.write("    " * len(levels) + f"    pop     rdi\n")
                file.write("    " * len(levels) + f"    call    dump\n\n")

            elif token.type is token_lib.DUMPCHAR:
                if not(token, stack.pop() is QWORD):
                    error_on_token(token, "DUMPCHAR expects a QWORD")
                    return True
                
                file.write("    " * len(levels) + f"    ;; -- DUMPCHAR --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, 1\n")
                file.write("    " * len(levels) + f"    mov     rdi, 1\n")
                file.write("    " * len(levels) + f"    mov     rsi, rsp\n")
                file.write("    " * len(levels) + f"    mov     rdx, 1\n")
                file.write("    " * len(levels) + f"    add     rsp, 8\n")
                file.write("    " * len(levels) + f"    syscall\n\n")

            elif token.type is token_lib.DUP:
                # TODO: DUP should allow any argument
                if not(stack[-1] in (QWORD, ADDR)):
                    error_on_token(token, "DUP expects a QWORD")
                    return True
                    
                stack.append(stack[-1])
                
                file.write("    " * len(levels) + f"    ;; -- DUP --\n\n")
                file.write("    " * len(levels) + f"    push    QWORD [rsp]\n\n")

            elif token.type is token_lib.SWP:
                # TODO: SWP should allow any arguments
                if not (stack[-1] is QWORD and stack[-2] is QWORD):
                    error_on_token(token, "SWP expects two QWORDs")
                    return True
                
                file.write("    " * len(levels) + f"    ;; -- SWP --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    xchg    rax, [rsp]\n")
                file.write("    " * len(levels) + f"    push    rax\n\n")

            elif token.type is token_lib.IF:
                if not (stack.pop() is BOOL):
                    error_on_token(token, "IF expects a BOOL")
                    return True
                
                file.write("    " * len(levels) + f"    ;; -- IF ({start_level}) --\n\n")
                file.write("    " * len(levels) + f"    pop     ax\n")
                file.write("    " * len(levels) + f"    test    ax, ax\n")
                file.write("    " * len(levels) + f"    je      .L{start_level}\n\n")

                levels.append((start_level, token_lib.IF, stack.copy()))  # Save the level and a copy of the stack
                start_level += 1

            elif token.type is token_lib.ELSE:
                if not len(levels):
                    error_on_token(token, "Invalid syntax")
                    return True
               
                level, start, old_stack = levels.pop()

                if start is token_lib.IF:
                    error_on_token(token, f"Invalid syntax, tried to end '{start}' with ELSE")
                    return True
               
                file.write("    " * len(levels) + f"    ;; -- ELSE ({level}, {start_level}) --\n\n")
                file.write("    " * len(levels) + f"    jmp     .L{start_level}\n")
                file.write("    " * len(levels) + f"    .L{level}:\n\n")

                levels.append((start_level, token_lib.ELSE, stack))  # Add the new stack, no need to copy
                stack = old_stack  # And change the stack to the new one
                start_level += 1

            elif token.type is token_lib.END:
                if not len(levels):
                    error_on_token(token, "Invalid syntax")
                    return True
               
                level, start, old_stack = levels.pop()

                if start in (token_lib.IF, token_lib.ELSE):
                    if old_stack != stack:
                        error_on_token(token, "Stack changed inside an if-end")
                        return True
                    
                    file.write("    " * len(levels) + f"    ;; -- ENDIF ({level}) --\n\n")
                    file.write("    " * len(levels) + f"    .L{level}:\n\n")

                elif start is token_lib.DO:
                    level2, start2, old_stack2 = levels.pop()

                    if start2 is not token_lib.WHILE:
                        error_on_token(token, "Invalid syntax")
                        return True
                        
                    if stack != old_stack2:
                        error_on_token(token, "Stack change inside a while-end")
                        return True
                    
                    file.write("    " * len(levels) + f"    ;; -- ENDWHILE ({level2}, {level}) --\n\n")
                    file.write("    " * len(levels) + f"    jmp     .L{level2}\n")
                    file.write("    " * len(levels) + f"    .L{level}:\n\n")

                elif start is token_lib.WHILE:
                    error_on_token(token, f"You probably forgot to add DO (while COND do CODE end)")
                    return True

                else:
                    error_on_token(token, f"Unknown starter for END; got '{start}'")
                    return True

            elif token.type is token_lib.WHILE:                
                file.write("    " * len(levels) + f"    ;; -- WHILE ({start_level}) --\n\n")
                file.write("    " * len(levels) + f"    .L{start_level}:\n\n")

                levels.append((start_level, token_lib.WHILE, stack.copy()))
                start_level += 1

            elif token.type is token_lib.DO:
                if stack.pop() is not BOOL:
                    error_on_token(token, "DO expects a BOOL")
                    return True
                
                file.write("    " * len(levels) + f"    ;; -- DO ({start_level}) --\n\n")
                file.write("    " * len(levels) + f"    pop     ax\n")
                file.write("    " * len(levels) + f"    test    ax, ax\n")
                file.write("    " * len(levels) + f"    je      .L{start_level}\n\n")

                levels.append((start_level, token_lib.DO, None))
                start_level += 1

            elif token.type is token_lib.INC:
                if stack[-1] is not QWORD:
                    error_on_token(token, "INC expects a QWORD")
                    return True
                
                file.write("    " * len(levels) + f"    ;; -- INC --\n\n")
                file.write("    " * len(levels) + f"    inc     QWORD [rsp]\n\n")

            elif token.type is token_lib.DEC:
                if stack[-1] is not QWORD:
                    error_on_token(token, "DEC expects a QWORD")
                    return True
                                
                file.write("    " * len(levels) + f"    ;; -- DEC --\n\n")
                file.write("    " * len(levels) + f"    dec     QWORD [rsp]\n\n")

            elif token.type is token_lib.ROT:
                # TODO: ROT should allow any argument
                if not (stack[-1] is QWORD and stack[-2] is QWORD and stack[-3] is QWORD):
                    error_on_token(token, "ROT expects three QWORDS")
                    return True
                
                file.write("    " * len(levels) + f"    ;; -- ROT --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, [rsp + 16]\n")
                file.write("    " * len(levels) + f"    xchg    rax, [rsp]\n")
                file.write("    " * len(levels) + f"    xchg    rax, [rsp + 8]\n")
                file.write("    " * len(levels) + f"    mov     [rsp + 16], rax\n\n")

            elif token.type is token_lib.DROP:
                # TODO: DROP should allow any argument
                if stack.pop() is not QWORD:
                    error_on_token(token, "DROP expects a QWORD")
                    return True
                
                file.write("    " * len(levels) + f"    ;; -- DROP -- \n\n")
                file.write("    " * len(levels) + f"    add     rsp, 8\n\n")

            elif token.type is token_lib.BREAK:
                copy = levels.copy()
                copy.reverse()
                
                for level, start, old_stack in copy:
                    if start is token_lib.DO:
                        break

                else:
                    error_on_token(token, f"BREAK should be used inside WHILE")
                    return
                
                file.write("    " * len(levels) + f"    ;; -- BREAK ({level}) --\n\n")
                file.write("    " * len(levels) + f"    jmp     .L{level}\n\n")

            elif token.type is token_lib.EQUAL:
                if not (stack.pop() is QWORD and stack.pop() is QWORD):
                    error_on_token(token, "EQUAL expects two QWORDs")
                    return True
                    
                stack.append(BOOL)
                
                file.write("    " * len(levels) + f"    ;; -- EQUAL --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    pop     rbx\n")
                file.write("    " * len(levels) + f"    sub     rax, rbx\n")
                file.write("    " * len(levels) + f"    pushf\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    and     ax, 0x40\n")
                file.write("    " * len(levels) + f"    push    ax\n\n")

            elif token.type is token_lib.NOT_EQUAL:
                if not (stack.pop() is QWORD and stack.pop() is QWORD):
                    error_on_token(token, "NOT_EQUAL expects two QWORDs")
                    return True
                    
                stack.append(BOOL)
                
                file.write("    " * len(levels) + f"    ;; -- NOT EQUAL --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    pop     rbx\n")
                file.write("    " * len(levels) + f"    sub     rax, rbx\n\n")
                file.write("    " * len(levels) + f"    pushf\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    and     ax, 0x40\n")
                file.write("    " * len(levels) + f"    xor     ax, 0x40\n")
                file.write("    " * len(levels) + f"    push    ax\n\n")

            elif token.type is token_lib.NOT:
                if stack.pop() is not BOOL:
                    error_on_token(token, "NOT expects a BOOL")
                    return True
                
                stack.append(BOOL)

                file.write("    " * len(levels) + f"    ;; -- NOT --\n\n")
                file.write("    " * len(levels) + f"    pop     ax\n")
                file.write("    " * len(levels) + f"    test    ax, ax\n")
                file.write("    " * len(levels) + f"    pushf\n")
                file.write("    " * len(levels) + f"    and     QWORD [rsp], 0x40\n\n")

            elif token.type is token_lib.FALSE:
                stack.append(BOOL)

                file.write("    " * len(levels) + f"    ;; -- FALSE --\n\n")
                file.write("    " * len(levels) + f"    xor     ax, ax\n")
                file.write("    " * len(levels) + f"    push    ax\n\n") 

            elif token.type is token_lib.TRUE:
                stack.append(BOOL)

                file.write("    " * len(levels) + f"    ;; -- TRUE --\n\n")
                file.write("    " * len(levels) + f"    mov     ax, 1\n")
                file.write("    " * len(levels) + f"    push    ax\n\n")

            elif token.type is token_lib.QWORD:
                old = stack.pop()
                stack.append(QWORD)
                
                if old is BOOL:
                    # For false, returns 0
                    # For true, returns 0x40 (64)
                    
                    file.write("    " * len(levels) + f"    ;; -- QWORD (BOOL) --\n\n")
                    file.write("    " * len(levels) + f"    mov     ax, WORD [rsp]\n")
                    file.write("    " * len(levels) + f"    push    ax\n\n")
                    file.write("    " * len(levels) + f"    push    ax\n\n")
                    file.write("    " * len(levels) + f"    push    ax\n\n")

                else:
                    error_on_token(token, "Unknown type for QWORD")
                    return True

            elif token.type is token_lib.BOOL:
                old = stack.pop()
                stack.append(BOOL)
                
                if old is QWORD:
                    # For 0, returns false
                    # For anything else, returns true

                    file.write("    " * len(levels) + f"    ;; -- BOOL (QWORD) --\n\n")
                    file.write("    " * len(levels) + f"    pop     ax\n")
                    file.write("    " * len(levels) + f"    or      WORD [rsp], ax\n\n")
                    file.write("    " * len(levels) + f"    pop     ax\n")
                    file.write("    " * len(levels) + f"    or      WORD [rsp], ax\n\n")
                    file.write("    " * len(levels) + f"    pop     ax\n")
                    file.write("    " * len(levels) + f"    or      WORD [rsp], ax\n\n")

                else:
                    error_on_token(token, "Unknown type for BOOL")
                    return True

            elif token.type is token_lib.ADDR:
                stack.append(ADDR)

                file.write("    " * len(levels) + f"    ;; -- ADDR --\n\n")
                file.write("    " * len(levels) + f"    push    memory\n\n")

            elif token.type is token_lib.READ8:
                if stack.pop() is not ADDR:
                    error_on_token(token, "READ8 expects an ADDR")
                    return True
                
                stack.append(QWORD)

                file.write("    " * len(levels) + f"    ;; -- READ8 --\n\n")
                file.write("    " * len(levels) + f"    mov     rax, QWORD [rsp]\n")
                file.write("    " * len(levels) + f"    mov     rax, QWORD [rax]\n")
                file.write("    " * len(levels) + f"    mov     [rsp], rax\n\n")

            elif token.type is token_lib.WRITE8:
                if not (stack.pop() is QWORD and stack.pop() is ADDR):
                    error_on_token(token, "WRITE8 expects an ADDR and a QWORD")
                    return True

                file.write("    " * len(levels) + f"    ;; -- WRITE8 --\n\n")
                file.write("    " * len(levels) + f"    pop     rax\n")
                file.write("    " * len(levels) + f"    pop     rbx\n")
                file.write("    " * len(levels) + f"    mov     [rbx], rax\n\n")
               
            else:
                error_on_token(token, f"token_lib.Token type {token.type} is unknown.")

        if len(levels):
            error("There were openers that were not closed")
            return True
                               
        if len(stack):
            error("There were values in the stack")
            return True

        file.write(f"    mov     rax, 60\n")
        file.write(f"    mov     rdi, 0\n")
        file.write(f"    syscall\n\n")

        file.write(f"segment .bss\n")
        file.write(f"    memory: resb {allocate_space}\n")

        return False
