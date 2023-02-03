from collections import deque

import typing
import enum_lib
import token_lib
import log_lib
import parser_lib
import data_types_lib

import os

# TODO: Add bitwise logic
# TODO: Add boolean logic

# TODO: Remake the stack, so that the pointer positions are already compiled (requires work because calling procedures will dynamically change the stack)
# TODO: Allow multiple DO's (not sure but could be useful)

# TODO: Add logging file specification
# TODO: Add in file nasm macros (would help make the compiler much smaller since the macros will be defined in the libraries instead of the compiler)

# TODO: Change pushf for better performance
# TODO: Add return
# TODO: Make enumerations named so they can be debugged in the console easily

# TODO: Add dynamic memory allocation (or local memory allocation)
# TODO: Add let (probably requires local memory allocation)

# TODO: Add library search locations
# TODO: Remove data
# TODO: Add compile time static execution
# TODO: Add pointer type and pointer type constant

# TODO: Change the memory size compilation
# TODO: Add structs (maybe)


# -- Constant name types --
enum_lib.reset()
PROCEDURE = enum_lib.step()
GLOBAL_MEMORY = enum_lib.step()
MACRO = enum_lib.step()

global_memory_pointer = 0

# Call stack size is 0x4000
# Memory size is also 0x4000


def error(message):
    log_lib.log("ERROR", message)


def error_on_token(token, message):
    error(f"({token.address}) {message}")

            
def compile_nasm_program(file_name: str, program: deque, debug_mode: bool = False): 
    data = deque()
    compiled_modules = []

    names = {}
   
    with open(file_name, "w") as file:
        file.write("")

    with open(file_name, "a") as file:
        file.write(f"segment .text\n\n")
        file.write(f"global _start\n")

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
        file.write(f"    memory:     resb 0x4000\n")
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
        
        file.write(f";; ####### MODULE '{path}' ######\n\n")
        found_error = compile_module(file, deque(parser.program), data, names, compiled_modules, debug_mode)
        file.write(f";; ####### ENDMODULE '{path}' ######\n\n")

        if found_error:
            error(f"Could not compile module '{path}'")
            return True

        if debug_mode:
            log_lib.log("DEBUG", f"Successfully compiled module '{module_token.arg}'")

        return False

    else:
        error(f"Invalid module path, '{path}'")
        return True


def compile_module(file, program: deque, data: deque, names: dict, compiled_modules: list, debug_mode: bool = False):
    global global_memory_pointer
    
    while True:
        try:                
            token = program.popleft()

        except IndexError:
            break

        if token.type is token_lib.INCLUDE:
            # Get the next token
            try:
                module_token = program.popleft()

            except IndexError:
                error_on_token(token, f"Expected name after include")
                return True

            if module_token.type is not token_lib.NAME:
                error_on_token(module_token, f"Expected name after include; got {module_token.type}")
                return True

            found_error = parse_and_compile_module_or_package(file, module_token.arg, data, names, compiled_modules, debug_mode)

            if found_error:
                return True

        elif token.type is token_lib.MEMORY:
            try:
                memory_name = program.popleft()

            except IndexError:
                error(f"Expected NAME after MEMORY; but no token was found")
                return True            

            if memory_name.type is not token_lib.NAME:
                error_on_token(memory_name, f"Expected NAME after MEMORY; got '{token.type}'")
                return True
            
            if memory_name.arg in names:
                error_on_token(memory_name, f"'{memory_name.arg}' was already defined before as a {names[memory_name.arg][0]}")
                return True

            stack = deque()

            if compile_time_execution(program, stack, token_lib.END, names, debug_mode):
                error_on_token(token, f"Could not compile memory size for '{memory_name.arg}'")

            if len(stack) != 1:
                error_on_token(memory_size, f"Expected only one INT for memory size")
                return True

            names[memory_name.arg] = GLOBAL_MEMORY, global_memory_pointer

            global_memory_pointer += stack[0]

        elif token.type is token_lib.MACRO:
            try:
                macro_name = program.popleft()

            except IndexError:
                error(f"Expected NAME after MACRO; but no token was found")

            macro = deque()
            
            if load_macro(program, macro, debug_mode):
                error_on_token(macro_name, f"Could not load macro")
                return True

            # When deques' extendleft is called, it reverses the argument deque
            # Because of that, we reverse it before saving the macro
            macro.reverse()

            names[macro_name.arg] = MACRO, macro

        elif token.type is token_lib.PROC:
            try:                
                procedure_name = program.popleft()

            except IndexError:
                error(f"Expected NAME after PROC; but no token was found")
                return True

            if procedure_name.type is not token_lib.NAME:
                error_on_token(procedure_name, f"Expected NAME after PROC; got '{token.type}'")
                return True
            
            if procedure_name.arg in names:
                error_on_token(procedure_name, f"'{procedure_name.arg}' was already defined before as a {names[procedure_name.arg][0]}")
                return True

            arguments = deque()

            if get_types(program, arguments, token_lib.RETURNS):
                return True

            returns = deque()

            if get_types(program, returns, token_lib.IN):
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
            file.write(f"    xchg    rsp, [callptr]\n\n")

            found_error = compile_procedure(file, program, data, names, arguments, returns, debug_mode)

            file.write(f"    xchg    rsp, [callptr]\n")
            file.write(f"    ret\n\n")
            file.write(f";; ==== ENDPROC '{procedure_name.arg}' ====\n\n")
            
            if found_error:
                error(f"Could not compile procedure, '{procedure_name.arg}'")
                return True

        elif token.type is token_lib.NAME:
            if token.arg not in names:
                error_on_token(token, f"'{token.arg}' is undefined")
                return True

            call_type, *args = names[token.arg]

            if call_type is MACRO:
                macro, = args

                stack.extendleft(macro)

            else:
                error_on_token(token, f"Can not call '{token.arg}' here")
                return True

        else:
            error_on_token(token, f"Expected PROC or INCLUDE; got '{token.type}'")
            return True

    return False


def get_types(program, types, end):
     while True:
         try:
             token = program.popleft()

         except IndexError:
             error(f"Expected type or {end}; but no token was found")
             return True

         if token.type is token_lib.TYPE:
             types.append(token.arg)

         elif token.type is end:
             return False

         elif token.type is NAME:
            if token.arg not in names:
                error_on_token(token, f"'{token.arg}' is undefined")
                return True

            call_type, *args = names[token.arg]

            if call_type is MACRO:
                macro, = args

                stack.extendleft(macro)

            else:
                error_on_token(token, f"Can not call '{token.arg}' here")
                return True

         else:
             error_on_token(token, f"Expected TYPE or {end}; got '{token.type}'")
             return True
         

def print_stack(stack):
    for i, data in enumerate(stack):
        print(f"{str(i).ljust(2, ' ')} | {data}")


def load_macro(program, macro, debug_mode: bool = False):
    while True:
        if not program:
            error("Found no ENDMACRO")
            return True
        
        token = program.popleft()

        if token.type is token_lib.ENDMACRO:
            return False

        elif token.type is token_lib.MACRO:
            error_on_token(token, "Right now, creating macros that creates macros is not allowed")
            return True

        else:
            macro.append(token)


def compile_time_execution(program, stack, end, names, debug_mode: bool = False):
    while True:
        if not program:
            error("Found no ENDMEMORY")
            return True

        token = program.popleft()

        if token.type is end:
            return False

        elif token.type is token_lib.NAME:
            if token.arg not in names:
                error_on_token(token, f"'{token.arg}' is undefined")
                return True

            call_type, *args = names[token.arg]

            if call_type is MACRO:
                macro, = args

                program.extendleft(macro)

            else:
                error_on_token(token, f"Can not call '{token.arg}' here")

        elif token.type is token_lib.PUSH8:
            stack.append(token.arg)

        elif token.type is token_lib.ADD:
            stack.append(stack.pop() + stack.pop())

        elif token.type is token_lib.SUB:
            stack.append(-stack.pop() + stack.pop())

        elif token.type is token_lib.MUL:
            stack.append(stack.pop() * stack.pop())

        else:
            error_on_token(token, f"This operation is not available in compile-time execution")
            return True


def compile_procedure(file, program, data: deque, names: dict, arguments: tuple, returns: tuple, debug_mode: bool = False):
    start_level = 0
    levels = deque()
    
    stack = deque()
    stack.extend(arguments)
    
    while True:
        if not program:
            error("Found no ENDPROC")
            return True

        token = program.popleft()

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
                file.write(f"    call    proc_{token.arg}\n")
                file.write(f"    xchg    rsp, [callptr]\n\n")

            elif call_type is GLOBAL_MEMORY:
                constant, = args

                stack.append(data_types_lib.INT)

                file.write(f"    ;; -- PUSH GLOBAL MEMORY {constant} --\n\n")
                file.write(f"    mov     rax, memory+{constant}\n")
                file.write(f"    push    rax\n\n")

            elif call_type is MACRO:
                macro, = args

                program.extendleft(macro)

            else:
                error_on_token(token, f"Unknown call type; got '{call_type}'")
                return True
            
        elif token.type is token_lib.PUSH8:
            file.write(f"    ;; -- PUSH8 {token.arg} --\n\n")
            file.write(f"    mov     rax, {token.arg}\n")
            file.write(f"    push    rax\n\n")

            stack.append(data_types_lib.INT)

        elif token.type is token_lib.BAND:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "BAND expects two INTs")
                return True

            file.write(f"    ;; -- BAND --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    and     [rsp], rax\n\n")

        elif token.type is token_lib.BOR:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "BOR expects two INTs")
                return True

            file.write(f"    ;; -- BOR --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    or      [rsp], rax\n\n")

        elif token.type is token_lib.BXOR:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "BXOR expects two INTs")
                return True

            file.write(f"    ;; -- BXOR --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    xor     [rsp], rax\n\n")

        elif token.type is token_lib.BNOT:
            if (
                    len(stack) < 1 or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "BNOT expects an INT")
                return True

            file.write(f"    ;; -- BNOT --\n\n")
            file.write(f"    not     [rsp]\n\n")

        elif token.type is token_lib.ADD:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "ADD expects two INTs")
                return True

            file.write(f"    ;; -- ADD --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    add     [rsp], rax\n\n")

        elif token.type is token_lib.SUB:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "SUB expects two INTs")
                return True

            file.write(f"    ;; -- SUB --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    sub     QWORD [rsp], rax\n\n")

        elif token.type is token_lib.DIVMOD:
            if (
                    len(stack) < 2 or
                    stack[-1] is not data_types_lib.INT or
                    stack[-2] is not data_types_lib.INT
            ):
                error_on_token(token, "DIVMOD expects two INTs")
                return True

            file.write(f"    ;; -- DIVMOD --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    mov     rbx, [rsp]\n")
            file.write(f"    mov     rax, [rsp+8]\n")
            file.write(f"    div     rbx\n")
            file.write(f"    mov     [rsp+8], rax\n")
            file.write(f"    mov     [rsp], rdx\n\n")

        elif token.type is token_lib.DIV:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "DIV expects two INTs")
                return True

            file.write(f"    ;; -- DIV --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    div     rbx\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.MOD:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "MOD expects two INTs")
                return True

            file.write(f"    ;; -- MOD --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    div     rbx\n")
            file.write(f"    mov     [rsp], rdx\n\n")

        elif token.type is token_lib.FULLMUL:
            if (
                    len(stack) < 2 or
                    stack[-1] is not data_types_lib.INT or
                    stack[-2] is not data_types_lib.INT
            ):
                error_on_token(token, "FULLMUL expects two INTs")
                return True

            file.write(f"    ;; -- FULLMUL --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    mov     rbx, [rsp]\n")
            file.write(f"    mov     rax, [rsp+8]\n")
            file.write(f"    mul     rbx\n")
            file.write(f"    mov     [rsp], rax\n")
            file.write(f"    mov     [rsp+8], rdx\n\n")

        elif token.type is token_lib.MUL:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "MUL expects two INTs")
                return True

            file.write(f"    ;; -- MUL --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    mul     rbx\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.MUL2:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack[-1] is not data_types_lib.INT
            ):
                error_on_token(token, "MUL2 expects two INTs")
                return True

            file.write(f"    ;; -- MUL2 --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    mul     rbx\n")
            file.write(f"    mov     [rsp], rdx\n\n")

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
            if len(stack) < 1 or stack.pop() is not data_types_lib.BOOL:
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

            if start is not token_lib.IF:
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
                error_on_token(token, "= expects two INTs")
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
                error_on_token(token, "!= expects two INTs")
                return True

            stack.append(data_types_lib.BOOL)

            file.write(f"    ;; -- NOT EQUAL --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    sub     [rsp], rax\n\n")

        elif token.type is token_lib.LESS_THAN:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT
            ):
                error_on_token(token, "< expects two INTs")
                return True

            stack.append(data_types_lib.BOOL)

            file.write(f"    ;; -- LESS THAN --\n\n")
            file.write(f"    pop    rbx\n")
            file.write(f"    pop    rax\n")
            file.write(f"    sub    rax, rbx\n")
            file.write(f"    pushf\n")
            file.write(f"    and    qword [rsp], 0x80\n\n")

        elif token.type is token_lib.GREATER_THAN:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT
            ):
                error_on_token(token, "> expects two INTs")
                return True

            stack.append(data_types_lib.BOOL)

            file.write(f"    ;; -- GREATER THAN --\n\n")
            file.write(f"    pop    rbx\n")
            file.write(f"    pop    rax\n")
            file.write(f"    sub    rbx, rax\n")
            file.write(f"    pushf\n")
            file.write(f"    and    qword [rsp], 0x80\n\n")

        elif token.type is token_lib.LESS_EQUAL:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT
            ):
                error_on_token(token, "<= expects two INTs")
                return True

            stack.append(data_types_lib.BOOL)

            file.write(f"    ;; -- GREATER THAN --\n\n")
            file.write(f"    pop    rbx\n")
            file.write(f"    pop    rax\n")
            file.write(f"    sub    rbx, rax\n")
            file.write(f"    pushf\n")
            file.write(f"    and    qword [rsp], 0x80\n")
            file.write(f"    xor    qword [rsp], 0x80\n\n")

        elif token.type is token_lib.GREATER_EQUAL:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT
            ):
                error_on_token(token, ">= expects two INTs")
                return True

            stack.append(data_types_lib.BOOL)

            file.write(f"    ;; -- GREATER EQUAL --\n\n")
            file.write(f"    pop    rbx\n")
            file.write(f"    pop    rax\n")
            file.write(f"    sub    rax, rbx\n")
            file.write(f"    pushf\n")
            file.write(f"    and    qword [rsp], 0x80\n")
            file.write(f"    xor    qword [rsp], 0x80\n\n")

        elif token.type is token_lib.NOT:
            if len(stack) < 1 or stack.pop() is not data_types_lib.BOOL:
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

        elif token.type is token_lib.LOAD8:
            if stack[-1] is not data_types_lib.INT:
                error_on_token(token, "LOAD8 expects a INT")
                return True

            file.write(f"    ;; -- LOAD8 --\n\n")
            file.write(f"    mov     rax, QWORD [rsp]\n")
            file.write(f"    mov     rax, QWORD [rax]\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.STORE8:
            if (
                    len(stack) < 2 or
                    stack.pop() is not data_types_lib.INT or
                    stack.pop() is not data_types_lib.INT
            ):
                error_on_token(token, "STORE8 expects two INTs")
                return True

            file.write(f"    ;; -- STORE8 --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     [rbx], rax\n\n")

        elif token.type is token_lib.LOAD:
            if len(stack) < 1 or stack[-1] is not data_types_lib.INT:
                error_on_token(token, "LOAD expects a INT")
                return True

            file.write(f"    ;; -- LOAD --\n\n")
            file.write(f"    xor     rax, rax\n")
            file.write(f"    mov     rbx, QWORD [rsp]\n")
            file.write(f"    mov     al, BYTE [rbx]\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.STORE:
            if len(stack) < 2 or stack.pop() is not data_types_lib.INT or stack.pop() is not data_types_lib.INT:
                error_on_token(token, "STORE expects two INTs")
                return True

            file.write(f"    ;; -- STORE --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     [rbx], al\n\n") 

        elif token.type is token_lib.SYSCALL0:
            if len(stack) < 1 or stack[-1] is not data_types_lib.INT:
                error_on_token(token, "SYSCALL0 expects a INT")
                return True

            file.write(f"    ;; -- SYSCALL0 --\n\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    syscall\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.SYSCALL1:
            if (
                    len(stack) < 2 or
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
                    len(stack) < 3 or
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
                    len(stack) < 4 or
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

        elif token.type is token_lib.SHIFTL32:
            if len(stack) < 1:
                erroron_token(token, f"SHIFTL32 expects an INT")
                return True
            
            file.write(f"    ;; -- SHIFTL32 --\n\n")
            file.write(f"    shl     QWORD [rsp], 32\n\n")


        elif token.type is token_lib.SHIFTR32:
            if len(stack) < 1:
                error_on_token(token, f"SHIFTR32 expects an INT")
                return True
            
            file.write(f"    ;; -- SHIFTR32 --\n\n")
            file.write(f"    shr     QWORD [rsp], 32\n\n")

        elif token.type is token_lib.SHIFTL4:
            if len(stack) < 1:
                erroron_token(token, f"SHIFTL4 expects an INT")
                return True
            
            file.write(f"    ;; -- SHIFTL4 --\n\n")
            file.write(f"    shl     QWORD [rsp], 4\n\n")

        elif token.type is token_lib.SHIFTR4:
            if len(stack) < 1:
                error_on_token(token, f"SHIFTR4 expects an INT")
                return True
            
            file.write(f"    ;; -- SHIFTR4 --\n\n")
            file.write(f"    shr     QWORD [rsp], 4\n\n")

        else:
            error_on_token(token, f"Token type {token.type} is unknown.")
            return True
