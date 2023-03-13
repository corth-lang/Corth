from collections import deque

import os
import typing

import enum_lib
import token_lib
import log_lib
import parser_lib

# TODO: Add library search locations
# TODO: Add logging file specification

# TODO: Add the main parameters as array of char

# TODO: Add negative numbers

# TODO: Add pre-execution, which will allow static execution and different kinds of optimizations (this kinda does not work well with nasm macros)
# TODO: Change let so that the variables are stored in the registers, not the local memory (might require a bit of work)
# TODO: Add in file nasm macros (would help make the compiler much smaller since the macros will be defined in the libraries instead of the compiler)
# TODO: Add in-file half-corth (better version of nasm macros that is more useful with pre-execution)

# TODO: Add 'typedef <name> (<name> <type>). end' (typedef is useful for stack types)
# TODO: Add 'sizeof <type>'
# TODO: Add 'cast <type>', which will cast any type to <type> (only if they are the same size)
# TODO: Add file-descriptor type
# TODO: Add pointer type and change NULLPTR's type to ptr
# TODO: Add fixed type
# TODO: Add complex type
# TODO: Add string type

# TODO: Make names 'namespacable' (a name 'name' inside a module 'module' should be named 'module:name' when included, parser should be rewritten)
# TODO: Add from
# TODO: Add ELIF
# TODO: Change the stack format
# TODO: Change the parameter and variable names in the compiler so that they make sense

# (probably gonna leave these to the Corth rewrite)
# TODO: Make enumerations named so they can be debugged in the console easily
# TODO: Change the address format of tokens
# TODO: Remake the stack, so that the pointer positions are already compiled (requires work because calling procedures will dynamically change the stack)

"""
macro <name>
  <macro>
endmacro

proc <name>
  <type>. -- <type>
in
  <proc>
end

<cond> if
  <do>
end

<cond> if
  <do>
else
  <else>
end

while
  <cond>
do
  <do>
end

memory <name> <size> (and <name> <size>). end  // Globally allocates memory; never deallocates if global

memory <name> <size> (and <name> <size>). in   // Locally allocates memory and defines the name
  <code>
end                                            // Frees memory


// Possible additions
cast <type>                                    // This will cast any type to <type>, without any change in the byte representation

typedef <name> (<name> <type>). end            // Defines a stack data type
struct <name> (<name> <type>). end             // Defines a memory data type
sizeof <name>                                  // Returns the size of the type

struct complex
  fixed real
  fixed imag
end

memory a as complex
memory b as complex

// a -> pointer to that address
// a.real -> pointer to that address

a.real @64 b.real @64


include <name>
include <name> from <package>
"""


# -- Call types --
enum_lib.reset()
PROCEDURE = enum_lib.step()
GLOBAL_VARIABLE_ADDRESS = enum_lib.step()
LOCAL_VARIABLE_ADDRESS = enum_lib.step()
LET_VARIABLE = enum_lib.step()
MACRO = enum_lib.step()

# -- Data types --
enum_lib.reset()
INT_TYPE = enum_lib.step()
BOOL_TYPE = enum_lib.step()

# Call stack size is 0x4000
# Memory size is also 0x4000


def error(message):
    log_lib.log("ERROR", message)


def error_on_token(token, message):
    error(f"({token.address}) {message}")

            
def compile_nasm_program(file_name: str, program: deque, debug_mode: bool = False, allocate_local_memory: int = 0x40000, allocate_callstack: int = 0x40000):
    # 'data' stores all of the one use data, 'names' stores the global variables and names
    data = deque()
    names = {}
        
    compiled_modules = []
   
    with open(file_name, "w") as file:
        file.write("")

    with open(file_name, "a") as file:
        file.write(f"segment .text\n\n")
        file.write(f"global _start\n")

        file.write("_start:\n")
        file.write("    mov     QWORD [callptr], callstack\n")
        file.write("    add     QWORD [callptr], 0x4000\n")
        file.write("    mov     QWORD [local], memory\n\n")
        
        file.write("    xchg    rsp, [callptr]\n")
        file.write("    push    CORTH_endofprogram\n")
        file.write("    push    QWORD [local]\n")
        file.write("    xchg    rsp, [callptr]\n")
        file.write("    jmp     PROC_main\n")

        file.write("CORTH_endofprogram:\n")
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

        for name, data in names.items():
            call_type, *args = data

            if call_type is GLOBAL_VARIABLE_ADDRESS:
                size, = args
                
                file.write(f"    global_variable_{name}: resb {size}\n")

        # 'memory' is where the local variables are stored.
        # 'local' points to the first address of the procedure's memory block
        file.write(f"    memory:     resb {allocate_local_memory}\n")
        file.write(f"    local:      resq 1\n")
        
        file.write(f"    callstack:  resq {allocate_callstack}\n")
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


def extend_macro(program: deque, token, macro, debug_mode: bool = False):
    for module_token in macro:
        copy_token = module_token.copy()
        copy_token.address += f"\n    from {token.arg} {token.address}"
        program.appendleft(copy_token)


def compile_module(file, program: deque, data: deque, names: dict, compiled_modules: list, debug_mode: bool = False):
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
            sizes = {}

            if get_memory_size(program, sizes, token_lib.END, names, debug_mode):
                error_on_token(token, f"Could not compile memory size")
                return True

            for name, size in sizes.items():
                if name in names:
                    error(f"Global variable '{name}' was already defined")
                    return True
                
                names[name] = GLOBAL_VARIABLE_ADDRESS, size

        elif token.type is token_lib.MACRO:
            if len(program) < 1:
                error_on_token(token, f"Expected NAME after MACRO; but no token was found")
                return True

            macro_name = program.popleft()

            if macro_name.type is not token_lib.NAME:
                error_on_token(macro_name, f"Expected NAME after MACRO")

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

            if get_types(program, names, arguments, (token_lib.RETURNS,)):
                error_on_token(procedure_name, f"Could not load the type of arguments")
                return True

            returns = deque()

            if get_types(program, names, returns, (token_lib.IN,)):
                return True

            arguments.pop()
            returns.pop()

            names[procedure_name.arg] = PROCEDURE, tuple(arguments), tuple(returns)

            if (
                    procedure_name.arg == "main" and (
                        len(returns) != 1 or
                        returns[0] != INT_TYPE
                    )
            ):
                error(f"Procedure main must return exactly one INT")
                return True

            file.write(f";; ==== PROC '{procedure_name.arg}' ====\n\n")
            file.write(f"PROC_{procedure_name.arg}:\n\n")

            found_error = compile_procedure(file, program, data, names, arguments, returns, debug_mode)

            file.write(f".RETURN:\n")
            file.write(f"    xchg    rsp, [callptr]\n")
            file.write(f"    pop     QWORD [local]\n")
            file.write(f"    pop     rax\n")
            file.write(f"    xchg    rsp, [callptr]\n")
            file.write(f"    jmp     rax\n\n")
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

                extend_macro(program, token, macro, debug_mode)

            else:
                error_on_token(token, f"Can not call '{token.arg}' here")
                return True

        else:
            error_on_token(token, f"Expected PROC or INCLUDE; got '{token.type}'")
            return True

    return False


def get_types(program, names, types, ends):
    while True:
        if not program:
            error(f"Expected type or {ends}; but no token was found")
            return True

        token = program.popleft()

        if token.type is token_lib.TYPE:
            types.append(token.arg)

        elif token.type in ends:
            types.append(token.arg)
            return False

        elif token.type is token_lib.NAME:
           if token.arg not in names:
               error_on_token(token, f"'{token.arg}' is undefined")
               return True

           call_type, *args = names[token.arg]

           if call_type is MACRO:
               macro, = args

               extend_macro(program, token, macro)

           else:
               error_on_token(token, f"Can not call '{token.arg}' here")
               return True

        else:
            error_on_token(token, f"Expected TYPE or {ends}; got '{token.type}'")
            return True


def get_names(program, names):
    while True:
        if not program:
            error(f"Expected name or {ends}; but no token was found")
            return True

        token = program.popleft()

        if token.type is token_lib.NAME:
            names.append(token.arg)

        elif token.type is token_lib.IN:
            return False

        else:
            error_on_token(token, f"Expected NAME or IN, got '{token.type}'")
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


def get_memory_size(program, sizes, end, names, debug_mode: bool = False):
    while True:
        if not program:
            error(f"Expected NAME")
            return True

        variable_name = program.popleft().arg
            
        stack = deque()

        while True:
            if not program:
                error(f"Expected AND or {end}")
                return True

            token = program.popleft()

            if token.type is end:
                if len(stack) != 1:
                    error(f"Expected exactly one INT")
                    return True

                sizes[variable_name] = stack[0]
                return False

            elif token.type is token_lib.AND:
                if len(stack) != 1:
                    error(f"Expected exactly one INT")
                    return True

                sizes[variable_name] = stack[0]
                break

            elif token.type is token_lib.NAME:
                if token.arg not in names:
                    error_on_token(token, f"'{token.arg}' is undefined")
                    return True

                call_type, *args = names[token.arg]

                if call_type is MACRO:
                    macro, = args

                    extend_macro(program, token, macro, debug_mode)

                else:
                    error_on_token(token, f"Can not call '{token.arg}' here")
                    return True

            elif token.type is token_lib.PUSH8:
                stack.append(token.arg)

            elif token.type is token_lib.ADD:
                if len(stack) < 2:
                    error(f"ADD requires two INTs")
                    return True
                
                stack.append(stack.pop() + stack.pop())

            elif token.type is token_lib.SUB:
                if len(stack) < 2:
                    error(f"SUB requires two INTs")
                    return True

                stack.append(-stack.pop() + stack.pop())

            elif token.type is token_lib.MUL:
                if len(stack) < 2:
                    error(f"MUL requires two INTs")
                    return True
                
                stack.append(stack.pop() * stack.pop())

            else:
                error_on_token(token, f"This operation is not available in compile-time execution")
                return True


def compile_procedure(file, program, data: deque, names: dict, arguments: tuple, returns: tuple, debug_mode: bool = False):
    local_memory = {}
    next_memory = 0
    
    start_level = 0
    levels = deque()

    call_no = 0
    
    stack = deque()
    stack.extend(arguments)

    returned = False
    
    while True:
        if not program:
            error("Found no ENDPROC")
            return True

        token = program.popleft()

        if token.type is token_lib.NAME:
            if returned and token.type is not token_lib.END:
                error_on_token(token, f"This code is impossible to reach")
                return True
                
            if token.arg in local_memory:
                call_type, *args = local_memory[token.arg]

                if call_type is LOCAL_VARIABLE_ADDRESS:
                    address ,= args
                    
                    stack.append(INT_TYPE)

                    file.write(f"    ;; -- PUSH LOCAL VARIABLE ADDRESS '{token.arg}' --\n\n")
                    file.write(f"    push    QWORD [local]\n")

                    if address:
                        file.write(f"    add     QWORD [rsp], {address}\n")

                    file.write(f"\n")

                elif call_type is LET_VARIABLE:
                    address ,= args
                    
                    stack.append(INT_TYPE)

                    file.write(f"    ;; -- PUSH LET VARIABLE '{token.arg}' --\n\n")
                    file.write(f"    mov    rax, QWORD [local]\n")

                    if address:
                        file.write(f"    add    rax, {address}\n")

                    file.write(f"    push   QWORD [rax]\n")

                    file.write(f"\n")
                    
                else:
                    error_on_token(token, f"Unknown local call type; got '{call_type}'")
                    return True

            elif token.arg in names:
                call_type, *args = names[token.arg]

                if call_type is PROCEDURE:
                    arguments_, returns_ = args

                    for i, expected in enumerate(arguments_[::-1]):
                        if not stack or stack.pop() is not expected:
                            error_on_token(token, f"Call arguments are not satisfied")
                            return True

                    stack.extend(returns_)

                    file.write(f"    ;; -- CALL '{token.arg}' --\n\n")
                    file.write(f"    xchg    rsp, [callptr]\n")
                    file.write(f"    push    .R{call_no}\n")
                    file.write(f"    push    QWORD [local]\n")
                    file.write(f"    add     QWORD [local], {next_memory}\n")
                    file.write(f"    xchg    rsp, [callptr]\n")
                    file.write(f"    jmp     PROC_{token.arg}\n")
                    file.write(f"    .R{call_no}:\n\n")

                    call_no += 1

                elif call_type is GLOBAL_VARIABLE_ADDRESS:
                    stack.append(INT_TYPE)

                    file.write(f"    ;; -- PUSH GLOBAL VARIABLE ADDRESS '{token.arg}' --\n\n")
                    file.write(f"    push    global_variable_{token.arg}\n\n")

                elif call_type is MACRO:
                    macro, = args

                    extend_macro(program, token, macro, debug_mode)

                else:
                    error_on_token(token, f"Unknown global call type; got '{call_type}'")
                    return True

            else:
                error_on_token(token, f"'{token.arg}' is not defined as a local or global variable")
                return True

        elif token.type is token_lib.MEMORY:
            sizes = {}

            if get_memory_size(program, sizes, token_lib.IN, names, debug_mode):
                error_on_token(token, f"Could not compile memory size")
                return True

            levels.append((start_level, token_lib.MEMORY, next_memory, tuple(sizes.keys())))

            for name, size in sizes.items():
                if name in local_memory:
                    error_on_token(token, f"Local variable '{name}' was already defined")
                    return True

                local_memory[name] = LOCAL_VARIABLE_ADDRESS, next_memory

                next_memory += size

        elif token.type is token_lib.LET:
            var_names = deque()
            
            if get_names(program, var_names):
                return True

            var_names.reverse()

            file.write(f"    ;; -- LET --\n\n")

            levels.append((start_level, token_lib.MEMORY, next_memory, var_names))
            
            for var_name in var_names:
                if not stack:
                    error_on_token(token, f"There was not enough values in the stack for let to handle")
                    return True

                if var_name in local_memory:
                    error_on_token(token, f"Local variable '{var_name}' was already defined")
                    return True

                stack.pop()
                
                local_memory[var_name] = LET_VARIABLE, next_memory

                file.write(f"    pop     rax\n")
                file.write(f"    mov     rbx, [local]\n")
                file.write(f"    mov     [rbx + {next_memory}], rax\n\n")

                next_memory += 8
            
        elif token.type is token_lib.PUSH8:
            file.write(f"    ;; -- PUSH8 {token.arg} --\n\n")
            file.write(f"    mov    rax, {token.arg}\n")
            file.write(f"    push   rax\n\n")

            stack.append(INT_TYPE)

        elif token.type is token_lib.BAND:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "BAND expects two INTs")
                return True

            file.write(f"    ;; -- BAND --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    and     [rsp], rax\n\n")

        elif token.type is token_lib.BOR:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "BOR expects two INTs")
                return True

            file.write(f"    ;; -- BOR --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    or      [rsp], rax\n\n")

        elif token.type is token_lib.BXOR:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "BXOR expects two INTs")
                return True

            file.write(f"    ;; -- BXOR --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    xor     [rsp], rax\n\n")

        elif token.type is token_lib.BNOT:
            if (
                    len(stack) < 1 or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "BNOT expects an INT")
                return True

            file.write(f"    ;; -- BNOT --\n\n")
            file.write(f"    not     QWORD [rsp]\n\n")

        elif token.type is token_lib.ADD:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "ADD expects two INTs")
                return True

            file.write(f"    ;; -- ADD --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    add     [rsp], rax\n\n")

        elif token.type is token_lib.SUB:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "SUB expects two INTs")
                return True

            file.write(f"    ;; -- SUB --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    sub     QWORD [rsp], rax\n\n")

        elif token.type is token_lib.DIVMOD:
            if (
                    len(stack) < 2 or
                    stack[-1] is not INT_TYPE or
                    stack[-2] is not INT_TYPE
            ):
                error_on_token(token, "DIVMOD expects two INTs")
                return True

            file.write(f"    ;; -- DIVMOD --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    mov     rbx, [rsp]\n")
            file.write(f"    mov     rax, [rsp+8]\n")
            file.write(f"    idiv    rbx\n")
            file.write(f"    mov     [rsp+8], rax\n")
            file.write(f"    mov     [rsp], rdx\n\n")

        elif token.type is token_lib.DIV:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "DIV expects two INTs")
                return True

            file.write(f"    ;; -- DIV --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    idiv    rbx\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.MOD:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "MOD expects two INTs")
                return True

            file.write(f"    ;; -- MOD --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    idiv    rbx\n")
            file.write(f"    mov     [rsp], rdx\n\n")

        elif token.type is token_lib.UDIVMOD:
            if (
                    len(stack) < 2 or
                    stack[-1] is not INT_TYPE or
                    stack[-2] is not INT_TYPE
            ):
                error_on_token(token, "UDIVMOD expects two INTs")
                return True

            file.write(f"    ;; -- UDIVMOD --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    mov     rbx, [rsp]\n")
            file.write(f"    mov     rax, [rsp+8]\n")
            file.write(f"    div     rbx\n")
            file.write(f"    mov     [rsp+8], rax\n")
            file.write(f"    mov     [rsp], rdx\n\n")

        elif token.type is token_lib.UDIV:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "UDIV expects two INTs")
                return True

            file.write(f"    ;; -- UDIV --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    div     rbx\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.UMOD:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "UMOD expects two INTs")
                return True

            file.write(f"    ;; -- UMOD --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    div     rbx\n")
            file.write(f"    mov     [rsp], rdx\n\n")

        elif token.type is token_lib.FULLMUL:
            if (
                    len(stack) < 2 or
                    stack[-1] is not INT_TYPE or
                    stack[-2] is not INT_TYPE
            ):
                error_on_token(token, "FULLMUL expects two INTs")
                return True

            file.write(f"    ;; -- FULLMUL --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    mov     rbx, [rsp]\n")
            file.write(f"    mov     rax, [rsp+8]\n")
            file.write(f"    imul    rbx\n")
            file.write(f"    mov     [rsp], rax\n")
            file.write(f"    mov     [rsp+8], rdx\n\n")

        elif token.type is token_lib.MUL:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "MUL expects two INTs")
                return True

            file.write(f"    ;; -- MUL --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    imul    rbx\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.MUL2:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "MUL2 expects two INTs")
                return True

            file.write(f"    ;; -- MUL2 --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    imul    rbx\n")
            file.write(f"    mov     [rsp], rdx\n\n")
            
        elif token.type is token_lib.UFULLMUL:
            if (
                    len(stack) < 2 or
                    stack[-1] is not INT_TYPE or
                    stack[-2] is not INT_TYPE
            ):
                error_on_token(token, "UFULLMUL expects two INTs")
                return True

            file.write(f"    ;; -- UFULLMUL --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    mov     rbx, [rsp]\n")
            file.write(f"    mov     rax, [rsp+8]\n")
            file.write(f"    mul     rbx\n")
            file.write(f"    mov     [rsp], rax\n")
            file.write(f"    mov     [rsp+8], rdx\n\n")

        elif token.type is token_lib.UMUL:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "UMUL expects two INTs")
                return True

            file.write(f"    ;; -- UMUL --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    mul     rbx\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.UMUL2:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
            ):
                error_on_token(token, "UMUL2 expects two INTs")
                return True

            file.write(f"    ;; -- UMUL2 --\n\n")
            file.write(f"    xor     rdx, rdx\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    mul     rbx\n")
            file.write(f"    mov     [rsp], rdx\n\n")

        elif token.type is token_lib.IF:
            if len(stack) < 1 or stack.pop() is not BOOL_TYPE:
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
                level, start, *args = levels.pop()

                if start in (token_lib.IF, token_lib.ELSE):
                    old_stack ,= args

                    if returned:
                        stack = old_stack
                        returned = False
                        
                    else:
                        if old_stack != stack:
                            error_on_token(token, "Stack changed inside an if-end")
                            return True

                    file.write(f"    ;; -- ENDIF ({level}) --\n\n")
                    file.write(f".L{level}:\n\n")

                elif start is token_lib.DO:
                    old_stack ,= args
                    
                    level2, start2, old_stack2 = levels.pop()

                    if start2 is not token_lib.WHILE:
                        error_on_token(token, "Invalid syntax")
                        return True

                    if returned:
                        error_on_token(token, "Returned between do-end")

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

                elif start is token_lib.MEMORY:
                    old_memory, remove_names = args

                    next_memory = old_memory
                    
                    for name in remove_names:
                        local_memory.pop(name)

                else:
                    error_on_token(token, f"Unknown starter for END; got '{start}'")
                    return True

            else:
                # End of proc
                if returned:
                    error("Returned just before ENDPROC, really?")
                    return True
                    
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
            if len(stack) < 1 or stack.pop() is not BOOL_TYPE:
                error_on_token(token, "DO expects a BOOL")
                return True

            file.write(f"    ;; -- DO ({start_level}) --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    test    rax, rax\n")
            file.write(f"    je      .L{start_level}\n\n")

            levels.append((start_level, token_lib.DO, stack.copy()))
            start_level += 1

        elif token.type is token_lib.INC:
            if len(stack) < 1 or stack[-1] is not INT_TYPE:
                error_on_token(token, "INC expects a INT")
                return True

            file.write(f"    ;; -- INC --\n\n")
            file.write(f"    inc     QWORD [rsp]\n\n")

        elif token.type is token_lib.DEC:
            if len(stack) < 1 or stack[-1] is not INT_TYPE:
                error_on_token(token, "DEC expects a INT")
                return True

            file.write(f"    ;; -- DEC --\n\n")
            file.write(f"    dec     QWORD [rsp]\n\n")

        elif token.type is token_lib.BREAK:
            copy = levels.copy()
            copy.reverse()

            returned = True

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

        elif token.type is token_lib.RETURN:
            returned = True

            if returns != stack:
                error_on_token(token, "Procedure does not obey its returns in pre-return")
                return True

            file.write(f"    ;; -- RETURN --\n\n")
            file.write(f"    jmp     .RETURN\n\n")

        elif token.type is token_lib.EQUAL:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack.pop() is not INT_TYPE
            ):
                error_on_token(token, "= expects two INTs")
                return True

            stack.append(BOOL_TYPE)

            file.write(f"    ;; -- EQUAL --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    sub     rax, rbx\n")
            file.write(f"    pushf\n")
            file.write(f"    and     QWORD [rsp], 0x40\n")

        elif token.type is token_lib.NOT_EQUAL:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack.pop() is not INT_TYPE
            ):
                error_on_token(token, "!= expects two INTs")
                return True

            stack.append(BOOL_TYPE)

            file.write(f"    ;; -- NOT EQUAL --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    sub     [rsp], rax\n\n")

        elif token.type is token_lib.LESS_THAN:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack.pop() is not INT_TYPE
            ):
                error_on_token(token, "< expects two INTs")
                return True

            stack.append(BOOL_TYPE)

            file.write(f"    ;; -- LESS THAN --\n\n")
            file.write(f"    pop    rbx\n")
            file.write(f"    pop    rax\n")
            file.write(f"    sub    rax, rbx\n")
            file.write(f"    pushf\n")
            file.write(f"    and    qword [rsp], 0x80\n\n")

        elif token.type is token_lib.GREATER_THAN:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack.pop() is not INT_TYPE
            ):
                error_on_token(token, "> expects two INTs")
                return True

            stack.append(BOOL_TYPE)

            file.write(f"    ;; -- GREATER THAN --\n\n")
            file.write(f"    pop    rbx\n")
            file.write(f"    pop    rax\n")
            file.write(f"    sub    rbx, rax\n")
            file.write(f"    pushf\n")
            file.write(f"    and    qword [rsp], 0x80\n\n")

        elif token.type is token_lib.LESS_EQUAL:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack.pop() is not INT_TYPE
            ):
                error_on_token(token, "<= expects two INTs")
                return True

            stack.append(BOOL_TYPE)

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
                    stack.pop() is not INT_TYPE or
                    stack.pop() is not INT_TYPE
            ):
                error_on_token(token, ">= expects two INTs")
                return True

            stack.append(BOOL_TYPE)

            file.write(f"    ;; -- GREATER EQUAL --\n\n")
            file.write(f"    pop    rbx\n")
            file.write(f"    pop    rax\n")
            file.write(f"    sub    rax, rbx\n")
            file.write(f"    pushf\n")
            file.write(f"    and    qword [rsp], 0x80\n")
            file.write(f"    xor    qword [rsp], 0x80\n\n")

        elif token.type is token_lib.NOT:
            if len(stack) < 1 or stack.pop() is not BOOL_TYPE:
                error_on_token(token, "NOT expects a BOOL")
                return True

            stack.append(BOOL_TYPE)

            file.write(f"    ;; -- NOT --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    test    rax, rax\n")
            file.write(f"    pushf\n")
            file.write(f"    and     QWORD [rsp], 0x40\n\n")

        elif token.type is token_lib.LOR:
            if (
                    len(stack) < 2 or
                    stack.pop() is not BOOL_TYPE or
                    stack[-1] is not BOOL_TYPE
            ):
                error_on_token(token, "LOR expects two BOOLs")
                return True

            file.write(f"    ;; -- LOR --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    or      [rsp], rax\n\n")

        elif token.type is token_lib.FALSE:
            stack.append(BOOL_TYPE)

            file.write(f"    ;; -- FALSE --\n\n")
            file.write(f"    xor     rax, rax\n")
            file.write(f"    push    rax\n\n") 

        elif token.type is token_lib.TRUE:
            stack.append(BOOL_TYPE)

            file.write(f"    ;; -- TRUE --\n\n")
            file.write(f"    mov     rax, 1\n")
            file.write(f"    push    rax\n\n")

        elif token.type is token_lib.LOAD8:
            if not len(stack) or stack[-1] is not INT_TYPE:
                error_on_token(token, "LOAD8 expects a INT")
                return True

            file.write(f"    ;; -- LOAD8 --\n\n")
            file.write(f"    mov     rax, QWORD [rsp]\n")
            file.write(f"    mov     rax, QWORD [rax]\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.STORE8:
            if len(stack) < 2 or stack.pop() is not INT_TYPE or stack.pop() is not INT_TYPE:
                error_on_token(token, "STORE8 expects two INTs")
                return True

            file.write(f"    ;; -- STORE8 --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     [rax], rbx\n\n")

        elif token.type is token_lib.LOAD:
            if not len(stack) or stack[-1] is not INT_TYPE:
                error_on_token(token, "LOAD expects a INT")
                return True

            file.write(f"    ;; -- LOAD --\n\n")
            file.write(f"    xor     rax, rax\n")
            file.write(f"    mov     rbx, QWORD [rsp]\n")
            file.write(f"    mov     al, BYTE [rbx]\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.STORE:
            if len(stack) < 2 or stack.pop() is not INT_TYPE or stack.pop() is not INT_TYPE:
                error_on_token(token, "STORE expects two INTs")
                return True

            file.write(f"    ;; -- STORE --\n\n")
            file.write(f"    pop     rax\n")
            file.write(f"    pop     rbx\n")
            file.write(f"    mov     [rax], bl\n\n") 

        elif token.type is token_lib.SYSCALL0:
            if len(stack) < 1 or stack[-1] is not INT_TYPE:
                error_on_token(token, "SYSCALL0 expects a INT")
                return True

            file.write(f"    ;; -- SYSCALL0 --\n\n")
            file.write(f"    mov     rax, [rsp]\n")
            file.write(f"    syscall\n")
            file.write(f"    mov     [rsp], rax\n\n")

        elif token.type is token_lib.SYSCALL1:
            if (
                    len(stack) < 2 or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
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
                    stack.pop() is not INT_TYPE or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
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
                    stack.pop() is not INT_TYPE or
                    stack.pop() is not INT_TYPE or
                    stack.pop() is not INT_TYPE or
                    stack[-1] is not INT_TYPE
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

            stack.append(INT_TYPE)
            stack.append(INT_TYPE)
                
            data.append(f"db " + ", ".join(map(str, map(ord, token.arg + "\x00"))))

        elif token.type is token_lib.DEBUG_STACK:
            log_lib.log("DEBUG", f"({token.address}) Reached ?stack")
            print_stack(stack)

        else:
            error_on_token(token, f"Token type {token.type} is unknown.")
            return True
