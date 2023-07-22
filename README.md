# Corth
A stack based programming language I designed based on Forth. 

The idea to make such a programming language came from the [Porth programming language](https://gitlab.com/tsoding/porth) series of [Tsoding Daily channel](https://www.youtube.com/@TsodingDaily).

- *./parser_lib.py* contains the parser, which returns a list of tokens.
- *./compiler_lib.py* contains the compiler, which creates the NASM program.
- *./main.py* allows the usage of command-line for easy access.
- *./quick_test.py* allows to quickly test compiling every example from *./examples/*.
- *./todo.md* is a TODO list for future plans on the project.
- *./libs/* directory contains some libraries written in Corth.
- *./examples/* directory contains some examples written in Corth.

For now, the language and tools are made in Python. As the project evolves, these tools will be rewritten in Corth.

## Requirements

- To use the Python compiler, Python is required (at least >=3.7 because of the f-strings).
- Programs are compiled to NASM, which requires the NASM compiler.
- You will need Linux environment, since syscalls won't work for Windows.

## How to use the compiler?

To compile a Corth program to an executable, type this in a command-line in the Corth folder.

    python3 main.py compile <source>

If there are no compile errors, this command will create an executable named *./output*. To change the output path, use '-o'.

For more information about the commands, type:

    python3 main.py -h


## Quick start to the Corth language

- Corth is a concatinative (stack based) language.
- Programs are compiled into NASM first, then into an executable.
- Everything can be inlined. The return character is used only to end inline comments and to add the newline character to the strings.
- Indentation and spaces are removed during parsing so they can be used.
- Names can contain any character except whitespace (space, tab or newline); but can not start with a decimal digit, a dollar sign, single or double quote.
- EVERYTHING IN THIS LANGUAGE CAN BE CHANGED AT ANY TIME. USE WITH CAUTION.

### First program:

    include libs/linux_86/stdio.corth
    
    proc main 
      int int -- int
    in let argc argv in
      "Hello, World!\n" puts
    end 0 end
    
- This is a simple program that prints "Hello, World!" when run.
- '[include](#include)' is used to include the library stdio, which contains some I/O operations like writing to files and the standard output.
- '[let](#let)' is used to 'name' values. In this example, it is used to name the parameter values.
- '[procedures](#procedures)' is used to define a procedure. 'main' is where the program starts.
- 'puts' is used to print a string to the standard output.
- For more examples, you can check the *./examples/* directory.
- For more information about these concepts, keep scrolling.

### Numbers:

    34
    0b101001
    0o205126
    0x5729da
    'a'
    '\n'

- Numbers push an integer type to the stack.
- Binary, octal and hexadecimal numbers are allowed. These can be used with 0b, 0o and 0x.
- Putting a character between single quotes ('') causes it to be interpreted as a *character*, which returns its ASCII value.
- Escapes such as *\n* are supported in characters.

### Strings:

    "This is a string"

    "This also is a string.
     In Corth, multi-line strings are supported."

- Strings push two numbers, the address and the length of the string.
- Strings are defined in the *data* part in the NASM compiler, so they can be modified at run-time (even though that is not recommended).

### Arithmetic operators:

    34 35 + // stack is now 69
    69 27 - // stack is now 42
    68 inc  // stack is now 69
    43 dec  // stack is now 42
    3 23 *  // stack is now 69
    85 2 /  // stack is now 42

- '+' adds the last two items and pushes the result back, '-' subtracts, '*' multiplies and '/' divides.
- 'inc' and 'dec' are macros defined as '1 +' and '1 -' in *./libs/core/arithmetic.corth*. They can be used to increase or decrease a number once.

### Include:

    include libs/str.corth

- 'include' allows to use external code.
- *./libs/* directory contains some useful libraries like *./libs/core/* or *./libs/str.corth*.
- Path can be both a file or a directory which will cause the compiler to include every file under that directory.

### Stack operations:
  
    1 2 3 drop // stack is now  1  2
    34 35 dup  // stack is now 34 35 35
    45 23 swp  // stack is now 23 45
    1 2 3 rot  // stack is now  2  3  1
    1 2 3 arot // stack is now  3  1  2

- *./libs/core/stack.corth* contains some basic stack operations.
- 'drop' removes the last item from the stack.
- 'dup' duplicates the last item in the stack.
- 'swp' swaps the places of the last two items.
- 'rot' rotates the places of the last 3 items, by moving the first added to the last position.
- 'arot' does the exact opposite of what 'rot' does.
- These operations are macros defined using [let](#let), with names starting with underscore (_). For hard to manage stack operations, it is recommended to use 'let' instead of these macros.
- There are some others, but it is recommended to check *./libs/core/stack.corth* for more information since they are a bit more complex.

### I/O:

    "Hello, world!\n" puts
    34 35 + putu " is a nice number.\n" puts

- *./libs/linux/stdio.corth* contains useful procedures for I/O operations like reading from and writing to streams.

### Procedures:

    proc sum
      int int --
    in
      "Sum of these numbers are: " puts + putu "\n" puts
    end

    proc main
      int int -- int
    in let argc argv in
      17 52 sum
    end 0 end

- 'proc' defines a procedure, which can be called anywhere in the code.
- 'return' can be used to early return from a procedure, but the stack must match with the procedure's output layout.
- Program starts from the 'main' procedure; if it is not defined, the compiler will return an error.
- If the code does not require recursion and is simple, it might be better to use a macro depending on the exact requirements.

### Macros:

    macro sayHi
      // Takes a string, the name

      "Hi, " puts puts "!\n" puts
    endmacro

    proc main
      int int -- int
    in let argc argv in
      "Josh" sayHi
    end 0 end

- 'macro' keyword is used to define macros and 'endmacro' is used to end the definition.
- Macros expand at compile time, allowing simplifying and compressing code.
- Macros are only compiled after expanding, so any comppile time error that would be caused by a macro is not detected before expansion.
- Using 'let' inside a macro is usually a bad idea, although some library macros are designed that way (like *dup*, *swp* or *rot*). If the code requires let; either change that macro to a procedure, or name the let variable with names that starts and ends with underscores (_).

### Name scopes:

- If a name is defined globally (for example with 'memory'), it can be reached from anywhere meaning any procedure in and out of the same file.
- If a name is defined locally in a procedure, it can only be reached within that procedure. 
- Two global or two local variables can not have the same name, but if a local and a global variable have the same name, the local one will be reachable until it is removed from the scope.

### Comments:

    // This is a line comment, it can also come after code
    34 35 + putu  // Just like that

    /*
      This is a block comment, aka a multi-line comment.
      Block comments can span several lines.
    */

### Control flow:

    include libs/linux_x86/stdio.corth

    proc main
      int int -- int
    in let argc argv in
      2 2 + 5 = if
        "Well, math is broken. Nice.\n" puts // Hopefully wont be printed
      end

      3 4 > if
        "Your computer has virus\n" puts     // Hopefully wont be printed
      else
        "Your computer is alright\n" puts    // Hopefully will be printed
      end

      // Count 0-9
      "First 10 numbers from 0 are,\n" puts
      0 while dup 10 < do                    // Duplicate the number, and check if it is less then 10
        dup putu "\n" puts                   // Print the number
      inc end drop                           // Increase the number
    end 0 end

- 'if' is used for conditions, it runs the code after it only if the last item on the stack is true.
- 'if' can be used with 'else' for more functionality, which runs only if the bool is false.
- Because of the way this language works, the 'if-else' statement can be used as ternary operator.
- 'while' is used for loops, and 'break' can be used to quit the loop early.
- If 'if' is used without an 'else', the stack must not change between 'if' and 'end' since otherwise it will create an ambiguity of what the stack will be after that part.
- If 'if' is used with an 'else', the stack change between 'if' and 'else' must be the same for the code between 'else' and 'end'.
- Stack must not change between 'while' and 'end'.
- Even though parser does not care for indentation, it is still a good idea to indent since in Corth these operations can get very hard to understand very quickly.

### Let:

     3 4 let x y in
       x y * x + y -
     end puti

- 'let' is used to make the stack management easier.
- When 'let' is reached, the variables are stored with the stack data. These names will be removed from the namescope when end is reached.
- When any 'let' variable is called, it directly returns its value, unlike a 'memory' variable which returns its address. Because of that, let variables are read-only, since they can only be written only once at the declaration.

### Static memory management:

    include libs/core/

    memory count sizeof(int) end
    
    proc increase
      --
    in
      count @64 inc count !64
    end

    proc main
      int int -- int
    in let argc argv in
      0 count !64

      increase

      count @64 putu

      memory x sizeof(int) and
             y sizeof(int) in
	       
        0 x !64
        x @64 puti " is before saving x\n" puts
        420 x !64
        x @64 puti " is after saving x\n" puts
        0 y !64
        y @64 puti " is before saving y\n" puts
        69 y !64
        y @64 puti " is after saving y\n" puts
      end
    end 0 end

- 'memory' is used for allocating global or local memory.
- When a variable name is called; the address is returned, NOT the value.
- When used globally, 'memory' allocates memory that can be used from everywhere after definition.
- But when used locally, 'in' should be added. 'end' shows the location where the memory reserved will be deallocated, and the names will be deleted.
- 'and' can be used to allocate more data without dealing with a huge chain of 'end's.
- '@64' loads 8 bytes of data from the address.
- '!64' stores 8 bytes of data to the address. (First argument is the value to be stored and the second is the address)
- 'memory' keyword allocates the memory at compile-time; because of that, a dynamic memory manager is required.

### Dynamic memory management:

    include libs/dynamic/malloc.corth

    100 malloc let buffer in
      buffer while dup buffer 100 + < do let addr in
        0x67 addr !8
      addr end inc end drop

      buffer mfree
    end

- *libs/dynamic/* directory contains some dynamic memory management utilities, like malloc or djoin.

### Collections:

- *libs/collections/* directory contains different kinds of data structures.