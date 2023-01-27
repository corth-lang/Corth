from collections import deque

import typing
import enum_lib
import token_lib
import log_lib
import parser_lib
import data_types_lib

import os


# TODO: Add comparison operators
# TODO: Add macros
# TODO: Change dump to a library procedure
# TODO: Add checks for the stack size for every instruction
# TODO: Add let
# TODO: Remake the stack, so that the pointer positions are already compiled
# TODO: Remake PUSHSTR
# TODO: Add PUSHSTRC
# TODO: Allow multiple DO's


enum_lib.reset()
PROCEDURE = enum_lib.step()

# Call stack size is 0x4000

# Procedure format: (PROCEDURE, (arguments), (returns))

"""
proc <name> 
    <in-types> 
  returns
    <out-types> 
  in
    <codes>
end
"""



def error(message):
    log_lib.log("ERROR", message)


def error_on_token(token, message):
    error(f"({token.address}) {message}")

            
def compile_nasm_program(file_name: str, program: typing.Generator, debug_mode: bool = False, allocate_space: int = 0x4000): 
    data = deque()
    compiled_modules = []

    names = {}
   
    with open(file_name, "w") as file:
        file.write("")

    with open(file_name, "a") as file:
        file.write(f"segment .text\n\n")
        file.write(f"global _start\n")

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
        file.write("    mov     QWORD [callptr], callstack\n")
        file.write("    add     QWORD [callptr], 0x4000\n\n")
        
        file.write("    xchg    rsp, [callptr]\n")
        file.write("    call    proc_main\n")
        file.write("    xchg    rsp, [callptr]\n\n")
        
        file.write("    mov     rax, 60\n")
        file.write("    pop     rdi\n")
        file.write("    syscall\n\n")

        if compile_module(file, program, data, names, compiled_modules, debug_mode):
            error(f"Could not compile main source")
            return True

        if "main" not in names:
            error(f"Entry point is required, define a main function")
            return True
    
        file.write(f"segment .data\n")
    
        for i, command in enumerate(data):
            file.write(f"    data_{i}: {command}\n")
    
        file.write(f"segment .bss\n")
        file.write(f"    memory:     resb {allocate_space}\n")
        file.write(f"    callstack:  resq 0x4000\n")
        file.write(f"    callptr:    resq 1\n")

        return False


def parse_and_compile_module_or_package(file, path: str, data, names, compiled_modules, debug_mode: bool = False):
    if path in compiled_modules:
        if debug_mode:
            log_lib.log("DEBUG", f"Skipping compiling the module or package '{path}'")

        return False
    
    if os.path.isdir(path):
        for item in os.listdir(path):
            parse_and_compile_module_or_package(file, path + item, data, names, compiled_modules, debug_mode)

        return False
    
    elif os.path.isfile(path):        
        parser = parser_lib.Parser()
        parser.parse_file(path)

        if parser.errors:
            error(f"Could not parse module; there were {parser.errors} errors")
            return True

        if debug_mode:
            log_lib.log("DEBUG", f"Compiling module '{path}'")

        compiled_modules.append(path)
        
        file.write(f";; ######## MODULE '{path}' ########\n\n")
        found_error = compile_module(file, iter(parser.program), data, names, compiled_modules, debug_mode)
        file.write(f";; ######## ENDMODULE '{path}' ########\n\n")

        if found_error:
            error(f"Could not compile module '{path}'")
            return True

        if debug_mode:
            log_lib.log("DEBUG", f"Successfully compiled module '{module_token.arg}'")

        return False

    else:
        error(f"Invalid module path, '{path}'")
        return True


def compile_module(file, program, data: deque, names: dict, compiled_modules: list, debug_mode: bool = False):    
    while True:
        try:                
            token = next(program)

        except StopIteration:
            break

        if token.type is token_lib.INCLUDE:
            # Get the next token
            try:
                module_token = next(program)

            except StopIteration:
                error_on_token(token, f"Expected name after include")
                return True

            if module_token.type is not token_lib.NAME:
                error_on_token(module_token, f"Expected name after include; got {module_token.type}")
                return True

            found_error = parse_and_compile_module_or_package(file, module_token.arg, data, names, compiled_modules, debug_mode)

            if found_error:
                return True

        elif token.type is token_lib.PROC:
            try:                
                procedure_name = next(program)

            except StopIteration:
                error(f"Expected NAME after PROC; but no token was found")
                return True

            if procedure_name.type is not token_lib.NAME:
                error_on_token(procedure_name, f"Expected NAME after PROC; got '{token.type}'")
                return True
            
            if procedure_name.arg in names:
                error_on_token(procedure_name, f"'{procedure_name.arg}' was already defined before as a {names[procedure_name.arg][0]}")
                return True

            arguments = deque()
            
            while True:
                try:
                    token = next(program)

                except StopIteration:
                    error(f"Expected type or RETURNS; but no token was found")
                    return True

                if token.type is token_lib.TYPE:
                    arguments.append(token.arg)

                elif token.type is token_lib.RETURNS:
                    break

                else:
                    error_on_token(token, f"Expected TYPE or RETURNS; got '{token.type}'")
                    return True

            returns = deque()
            
            while True:
                try:
                    token = next(program)

                except StopIteration:
                    error(f"Expected type or IN; but no token was found")
                    return True

                if token.type is token_lib.TYPE:
                    returns.append(token.arg)

                elif token.type is token_lib.IN:
                    break

                else:
                    error_on_token(token, f"Expected TYPE or IN; got '{token.type}'")
                    return True

            names[procedure_name.arg] = PROCEDURE, tuple(arguments), tuple(returns)

            if (
                    procedure_name.arg == "main" and (
                        len(returns) != 1 or
                        returns[0] != data_types_lib.INT
                    )
            ):
                error(f"Procedure main must return exactly one INT")
                return True

            file.write(f";; ==== PROC '{procedure_name.arg}' ====\n\n")
            file.write(f"proc_{procedure_name.arg}:\n\n")
            file.write(f"    xchg    rsp, [callptr]\n")

            found_error = compile_procedure(file, program, data, names, arguments, returns, debug_mode)

            file.write(f"    xchg    rsp, [callptr]\n")
            file.write(f"    ret\n\n")
            file.write(f";; ==== ENDPROC '{procedure_name.arg}' ====\n\n")
            
            if found_error:
                error(f"Could not compile procedure, '{procedure_name.arg}'")
                return True

        else:
            error_on_token(token, f"Expected PROC or INCLUDE; got '{token.type}'")
            return True

    return False


def print_stack(stack):
    for i, data in enumerate(stack):
        print(f"{str(i).ljust(2, ' ')} | {data}")


def compile_procedure(file, program, data: deque, names: dict, arguments: tuple, returns: tuple, debug_mode: bool = False):
    start_level = 0
    levels = deque()
    
    stack = deque()
    stack.extend(arguments)
    
    while True:
        try:                
            token = next(program)

        except StopIteration:
            error("Found no ENDPROC")
            return True
        
        if debug_mode:
            log_lib.log("DEBUG", f"{repr(token).ljust(20, ' ')} | {stack}")

        if token.type is token_lib.NAME:
            if token.arg not in names:
                error_on_token(token, f"'{token.arg}' is undefined")
                return True

            call_type, *args = names[token.arg]

            if call_type is PROCEDURE:
                arguments_, returns_ = args

                for i, expected in enumerate(arguments_[::-1]):
                    removed = stack.pop()
                    if removed != expected:
                        error_on_token(token, f"Call arguments are not satisfied; expected '{expected}', got '{removed}'")
                        return True

                stack.extend(returns_)
                
                file.write(f"    ;; -- CALL {token.arg} --\n\n")                
                file.write(f"    xchg    rsp, [callptr]\n")
                file.write(f"    call proc_{token.arg}\n\n")
                file.write(f"    xchg    rsp, [callptr]\n")

            else:
                error_on_token(token, f"Unknown call type; got '{call_type}'")
                return True
            
        elif token.type is token_lib.PUSH8:
            file.write(f"    ;; -- PUSH8 {token.arg} --\n\n")
            file.write(f"    mov     rax, {token.arg}\n")
            file.write(f"    push    rax\n\n")

            stack.append(data_types_lib.INT)

        elif token.type is token_lib.ADD:
            if (
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "ADD expects two INTs or ADDRs")
                return True

            file.write(f"    ;; -- ADD --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    add     [rsp], rax\n")

        elif token.type is token_lib.SUB:
            if (
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "SUB expects two INTs")
                return True

            file.write(f"    ;; -- SUB --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    sub     QWORD [rsp], rax\n")

        elif token.type is token_lib.DUMP:
            if len(stack) < 1 or stack.pop() is not data_types_lib.INT:
                error_on_token(token, "DUMP expects a INT")
                return True

            file.write(f"    ;; -- DUMP --\n\n")
            file.write(f"    pop     rdi\n")
            file.write(f"    call    dump\n\n")

        elif token.type is token_lib.DUP:
            if len(stack) < 1:
                error_on_token(token, "DUP expects a INT")
                return True

            stack.append(stack[-1])

            file.write(f"    ;; -- DUP --\n\n")
            file.write(f"    push    QWORD [rsp]\n\n")

        elif token.type is token_lib.SWP:
            if len(stack) < 2:
                error_on_token(token, "SWP expects two arguments")
                return True

            file.write(f"    ;; -- SWP --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    xchg    rax, [rsp]\n")
            file.write(f"    push    rax\n\n")

        elif token.type is token_lib.IF:
            if stack.pop() is not data_types_lib.BOOL:
                error_on_token(token, "IF expects a BOOL")
                return True

            file.write(f"    ;; -- IF ({start_level}) --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    test    rax, rax\n")
            file.write(f"    je      .L{start_level}\n\n")

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

            file.write(f"    ;; -- ELSE ({level}, {start_level}) --\n\n")
            file.write(f"    jmp     .L{start_level}\n")
            file.write(f".L{level}:\n\n")

            levels.append((start_level, token_lib.ELSE, stack))  # Add the new stack, no need to copy
            stack = old_stack  # And change the stack to the new one
            start_level += 1

        elif token.type is token_lib.END:                    
            if len(levels):
                level, start, old_stack = levels.pop()

                if start in (token_lib.IF, token_lib.ELSE):
                    if old_stack != stack:
                        error_on_token(token, "Stack changed inside an if-end")
                        return True

                    file.write(f"    ;; -- ENDIF ({level}) --\n\n")
                    file.write(f".L{level}:\n\n")

                elif start is token_lib.DO:
                    level2, start2, old_stack2 = levels.pop()

                    if start2 is not token_lib.WHILE:
                        error_on_token(token, "Invalid syntax")
                        return True

                    if stack != old_stack2:
                        error_on_token(token, "Stack changed inside a while-end")
                        log_lib.log("INFO", "Expected")
                        print_stack(old_stack2)
                        log_lib.log("INFO", "Got")
                        print_stack(stack)
                        return True

                    file.write(f"    ;; -- ENDWHILE ({level2}, {level}) --\n\n")
                    file.write(f"    jmp     .L{level2}\n")
                    file.write(f".L{level}:\n\n")

                    stack = old_stack

                elif start is token_lib.WHILE:
                    error_on_token(token, f"You probably forgot to add DO (while COND do CODE end)")
                    return True

                else:
                    error_on_token(token, f"Unknown starter for END; got '{start}'")
                    return True

            else:
                # End of proc
                if stack == returns:
                    return False
                    
                error("Procedure does not obey its returns")

                log_lib.log("INFO", "Expected")
                print_stack(returns)

                log_lib.log("INFO", "Got")
                print_stack(stack)

                return True

        elif token.type is token_lib.WHILE:                
            file.write(f"    ;; -- WHILE ({start_level}) --\n\n")
            file.write(f".L{start_level}:\n\n")

            levels.append((start_level, token_lib.WHILE, stack.copy()))
            start_level += 1

        elif token.type is token_lib.DO:
            if len(stack) < 1 or stack.pop() is not data_types_lib.BOOL:
                error_on_token(token, "DO expects a BOOL")
                return True

            file.write(f"    ;; -- DO ({start_level}) --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    test    rax, rax\n")
            file.write(f"    je      .L{start_level}\n\n")

            levels.append((start_level, token_lib.DO, stack.copy()))
            start_level += 1

        elif token.type is token_lib.INC:
            if len(stack) < 1 or stack[-1] is not data_types_lib.INT:
                error_on_token(token, "INC expects a INT")
                return True

            file.write(f"    ;; -- INC --\n\n")
            file.write(f"    inc     QWORD [rsp]\n\n")

        elif token.type is token_lib.DEC:
            if len(stack) < 1 or stack[-1] is not data_types_lib.INT:
                error_on_token(token, "DEC expects a INT")
                return True

            file.write(f"    ;; -- DEC --\n\n")
            file.write(f"    dec     QWORD [rsp]\n\n")

        elif token.type is token_lib.ROT:
            if len(stack) < 3:
                error_on_token(token, "ROT expects three arguments")
                return True

            file.write(f"    ;; -- ROT --\n\n")
            file.write(f"    mov     rax, [rsp + 16]\n")
            file.write(f"    xchg    rax, [rsp]\n")
            file.write(f"    xchg    rax, [rsp + 8]\n")
            file.write(f"    mov     [rsp + 16], rax\n\n")

        elif token.type is token_lib.DROP:
            if len(stack) < 1:
                error_on_token(token, "DROP expects one argument")
                return True

            stack.pop()

            file.write(f"    ;; -- DROP -- \n\n")
            file.write(f"    add     rsp, 8\n\n")

        elif token.type is token_lib.BREAK:
            copy = levels.copy()
            copy.reverse()

            for level, start, old_stack in copy:
                if start is token_lib.DO:
                    break

            else:
                error_on_token(token, f"BREAK should be used inside WHILE")
                return True

            if stack != old_stack:
                error_on_token(token, f"Stack changed between the DO and BREAK")               

                log_lib.log("INFO", "Expected")
                print_stack(old_stack)
                log_lib.log("INFO", "Got")
                print_stack(stack)
                
                return True

            file.write(f"    ;; -- BREAK ({level}) --\n\n")
            file.write(f"    jmp     .L{level}\n\n")

        elif token.type is token_lib.EQUAL:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT
            ):
                error_on_token(token, "EQUAL expects two INTs")
                return True

            stack.append(data_types_lib.BOOL)

            file.write(f"    ;; -- EQUAL --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    sub     rax, rbx\n")
            file.write(f"    pushf\n")
            file.write(f"    and     QWORD [rsp], 0x40\n")

        elif token.type is token_lib.NOT_EQUAL:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT
            ):
                error_on_token(token, "NOT_EQUAL expects two INTs")
                return True

            stack.append(data_types_lib.BOOL)

            file.write(f"    ;; -- NOT EQUAL --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    sub     [rsp], rax\n\n")

        elif token.type is token_lib.NOT:
            if stack.pop() is not data_types_lib.BOOL:
                error_on_token(token, "NOT expects a BOOL")
                return True

            stack.append(data_types_lib.BOOL)

            file.write(f"    ;; -- NOT --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    test    rax, rax\n")
            file.write(f"    pushf\n")
            file.write(f"    and     QWORD [rsp], 0x40\n\n")

        elif token.type is token_lib.FALSE:
            stack.append(data_types_lib.BOOL)

            file.write(f"    ;; -- FALSE --\n\n")
            file.write(f"    xor     rax, rax\n")
            file.write(f"    push    rax\n\n") 

        elif token.type is token_lib.TRUE:
            stack.append(data_types_lib.BOOL)

            file.write(f"    ;; -- TRUE --\n\n")
            file.write(f"    mov     rax, 1\n")
            file.write(f"    push    rax\n\n")
            
        elif token.type is token_lib.ADDR:
            stack.append(data_types_lib.INT)

            file.write(f"    ;; -- ADDR --\n\n")
            file.write(f"    push    memory\n\n")

        elif token.type is token_lib.LOAD8:
            if stack[-1] is not data_types_lib.INT:
                error_on_token(token, "LOAD8 expects a INT")
                return True

            file.write(f"    ;; -- LOAD8 --\n\n")
            file.write(f"    mov     rax, INT [rsp]\n")
            file.write(f"    mov     rax, INT [rax]\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.STORE8:
            if (
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT
            ):
                error_on_token(token, "STORE8 expects an ADDR and a INT")
                return True

            file.write(f"    ;; -- STORE8 --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     [rbx], rax\n\n")

        elif token.type is token_lib.LOAD:
            if stack[-1] is not data_types_lib.INT:
                error_on_token(token, "LOAD expects a INT")
                return True

            file.write(f"    ;; -- LOAD --\n\n")
            file.write(f"    xor     rax, rax\n")
            file.write(f"    mov     rbx, QWORD [rsp]\n")
            file.write(f"    mov     al, BYTE [rbx]\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.STORE:
            if stack.pop() is not data_types_lib.INT or stack.pop() is not data_types_lib.INT:
                error_on_token(token, "STORE expects two INTs")
                return True

            file.write(f"    ;; -- STORE --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     [rbx], al\n\n") 

        elif token.type is token_lib.SYSCALL0:
            if stack[-1] is not data_types_lib.INT:
                error_on_token(token, "SYSCALL0 expects a INT")
                return True

            file.write(f"    ;; -- SYSCALL0 --\n\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    syscall\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.SYSCALL1:
            if (
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "SYSCALL1 expects two INTs")
                return True

            file.write(f"    ;; -- SYSCALL1 --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    mov     rdi, [rsp]\n")
            file.write(f"    syscall\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.SYSCALL2:
            if (
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
                ):
                error_on_token(token, "SYSCALL2 expects three INTs")
                return True

            file.write(f"    ;; -- SYSCALL2 --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    pop     rsi\n")
            file.write(f"    mov     rdi, [rsp]\n")
            file.write(f"    syscall\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.SYSCALL3:
            if (
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "SYSCALL3 expects four INTs")
                return True

            file.write(f"    ;; -- SYSCALL3 --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    pop     rdx\n")
            file.write(f"    pop     rsi\n")
            file.write(f"    mov     rdi, [rsp]\n")
            file.write(f"    syscall\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.PUSHSTR:
            file.write(f"    ;; -- PUSHSTR (data_{len(data)}) --\n\n")
            file.write(f"    push    data_{len(data)}\n")
            file.write(f"    push    {len(token.arg)}\n\n")

            stack.append(data_types_lib.INT)
            stack.append(data_types_lib.INT)

            data.append(f"db " + ", ".join(map(str, map(ord, token.arg))) + ", 0")

        elif token.type is token_lib.DEBUG_STACK:
            log_lib.log("DEBUG", f"({token.address}) Reached ?stack")
            print_stack(stack)

        else:
            error_on_token(token, f"Token type {token.type} is unknown.")
            return True
