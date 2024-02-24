# Corth
A stack based programming language I designed based on Forth and Porth from the [Porth programming language](https://gitlab.com/tsoding/porth) series of [Tsoding Daily channel](https://www.youtube.com/@TsodingDaily).
The language is quite similar to Porth, however there are several differences.
The compiler was written in Python first, but then rewrote it using Corth language itself. It is now a self hosted language.

The repo consists of the compiler source code in Corth, an already compiled and assembled compiler, standard library and examples.

## Requirements

- Right now, the compiler can only compile in ELF64 format.
- Compiler uses NASM which can be downloaded using a package manager or from its repo.

## How to use the compiler?

To compile a Corth program to an ELF64 executable, cd to the directory that contains the corth executable and run:


    ./corth compile <file-name> -i ./std/
    
    
This will create an executable called *output* which can be directly run.

The compiler can be bootstrapped using the `bootstrap` subcommand:


    ./corth bootstrap ./compiler/ --std ./std/
    
    
This will compile the compiler source code and place it at *./corth*.


## Quick start to the Corth language

- Corth is a concatinative (stack based) language. Every operation pops its arguments from the end of the stack and pushes its return values to the end of the stack.
- Programs are compiled into NASM format first, then into object and executable files.
- Indentation, spaces, newline characters are ignored by the compiler unless they are inside of a string.
- Names can contain any character except whitespace (space, tab or newline); but can not start with a decimal digit, a dollar sign, single or double quote.
- Language is made up of WORDS, instead of statements. Because of this, the lexer does not create a AST and instead only produces a sequence of tokens. These tokens are then run in order.
- EVERYTHING IN THIS LANGUAGE CAN BE CHANGED AT ANY TIME. USE WITH CAUTION.

### First program:

    // From ./examples/hello_world.corth
    
    include "linux_86x/stdio.corth"
    
    proc main
      int int -> int
    in let argc argv in
      "Hello, World!\n" puts
    end 0 end 
    
- This is a simple program that prints 'Hello, World!' when run.
- Compile and run this program with `./corth compile ./examples/hello_world.corth -i ./std.corth && ./output`
- [`include`](#include) keyword is used to include the library *stdio*, which contains some basic I/O procedures and macros for writing to/from files and the standard streams.
- [`let`](#let) keyword is used to 'name' values. In this example, it is used to name the parameter values.
- [`proc`](#procedures) keyword is used to define a procedure. `main` is where the program starts.
- Writing anything in double quotes causes it to be interpreted as a string. A string is just a pointer to a character array and an integer that represents its length.
- `puts` is defined in the *stdio* library, which prints the string that is passed to it in the standard output.
- For more examples, you can check the *./examples/* directory.
- For more information about these concepts, keep scrolling.

### Numbers:

    // Push and pop direction of the stack is kept on the right side in this document.
    // This will hopefully help understand the concept of stack and 'let' keyword.
    34        // Stack = { 34 }
    0b101001  // Stack = { 34, 41 }
    0o205126  // Stack = { 34, 41, 68182 }
    0x5729da  // Stack = { 34, 41, 68182, 5712346 }
    'a'       // Stack = { 34, 41, 68182, 5712346, 97 }
    '\n'      // Stack = { 34, 41, 68182, 5712346, 97, 10 }

- Numbers push an integer type to the stack. An integer type of stack item stores an 8 byte value.
- Lexer allows binary, octal and hexadecimal integers as well. The prefixes are `0b`, `0o` and `0x` respectively.
- Putting a character between single quotes ('') causes it to be interpreted as an integer, which appends its ASCII value to the stack.
- Escape statements such as `\n` are supported in characters.

### Strings:

    "This is a string"   // Stack = { 0x648a15, 16 }

    "This also is a string.
     In Corth, multi-line strings are supported."  // Stack = { 0x648a15, 16, 0x648a26, 71 }

- Strings push two items, a pointer to the address and an integer length of the string.
- Escape statements are also supported in strings.
- It is not recommended to modify the contents of strings in program, although it is possible.

### Arithmetic operators:

    34 35 + // Stack = { 69 }
    69 27 - // Stack = { 69, 42 }
    68 inc  // Stack = { 69, 42, 69 }
    43 dec  // Stack = { 69, 42, 69, 42 }
    3 23 *  // Stack = { 69, 42, 69, 42, 69 }
    85 2 /  // Stack = { 69, 42, 69, 42, 69, 42 }

- `+` sums the last two items and pushes the result back, `-` subtracts signed or unsigned integers.
- `*` multiplies and `/` divides signed integers. Right now, the compiler does not keep track of the integer 'signeded-ness', so every signed and unsigned operation can be used on any integer type. The unsigned versions of `\*` and `/` are `u\*` and `u/`.
- `inc` and `dec` are macros defined as `1 +` and `1 -` in *core/arithmetic.corth*. They can be used to increment or decrement a number once.

### Include:

    include "str.corth"

- When compiler sees an `include` keyword, it starts to compile the file whose path is given after the `include` keyword.
- Right now, the compiler does not allow including directories. A todo error will be given if tried.
- *./std/* directory contains some useful libraries like *core/stack.corth* or *str.corth*.

### Stack operations:
  
    1 2 3 // Stack = { 1, 2, 3 }
    swp   // Stack = { 1, 3, 2 }
    drop  // Stack = { 1, 3 }
    dup   // Stack = { 1, 3, 3 }
    rot   // Stack = { 3, 3, 1 }
    arot  // Stack = { 1, 3, 3 }

- *./std/core/stack.corth* contains several macros for stack manipulation.
- `drop` removes the last item from the stack.
- `dup` duplicates the last item in the stack.
- `swp` swaps the places of the last two items.
- `rot` rotates the places of the last 3 items, by moving the first added to the last position.
- `arot` does the exact opposite of what `rot` does.
- These operations are macros defined using [let](#let), with names starting with underscore (_). For hard to manage stack operations, it is recommended to use `let` instead of these macros.
- There are some others, but it is recommended to check *./std/core/stack.corth* for more information since they are a bit more complex.

### I/O:

    "Hello, world!\n" puts                      // Prints 'Hello, world!' to the standard output.
    34 35 + eputu " is a nice number.\n" eputs  // Prints '69 is a nice number.' to the standard error.

- *./std/linux_x86/stdio.corth* contains useful procedures for I/O operations like reading from and writing to streams.

### Procedures:

    proc arithmetic-average  // The name of the procedure is 'arithmetic-average'.
      // Procedure takes two integers as arguments, and returns a single integer.
      // The leftmost type is the oldest item in the stack.
      int int -> int
    in
      // This is where the code is located.
      + 2 /
    end

    // This procedure will be run.
    proc main
      // Right now, only 'int int -> int' argument layout is allowed for the main procedure.
      int int -> int
    in let argc argv in
      "The arithmetic average of 53 and 31 is " puts 53 31 arithmetic-average putu ".\n" puts
    end 0 end  // Program exits with exit code 0.

- `proc` defines a procedure, which can be called anywhere in the code.
- `return` can be used to early return from a procedure, but the stack must match with the procedure's output layout.
- Because of the way the stack works, procedures can return more than one value unlike most other languages.
- Program starts from the `main` procedure; if it is not defined, the compiler will return an error.
- If the code does not require recursion and is simple, it might be better to use a macro depending on the exact requirements.

### Macros:

    macro sayHi 
      // Name of the macro is 'sayHi'. This means when the compiler sees 'sayHi' anywhere in the code, it will convert it to these.
      // Takes a string, the name and prints a welcome message.

      "Hi, " puts puts "!\n" puts
    endmacro

    proc main
      int int -> int
    in let argc argv in
      "Josh" 
      sayHi  // This will be converted to this:
      // "Hi, " puts puts "!\n" puts
    end 0 end

- `macro` keyword is used to define macros and `endmacro` is used to end the definition.
- Macros expand at compile time, allowing simplifying and compressing code without losing functionality.
- Macros are only compiled after expanding, so any compile time error that would be caused by a macro is not detected before expansion.
- Using `let` inside a macro is usually a bad idea, although some library macros are designed that way (like `dup`, `swp` or `rot`). If the code requires `let`; either change that macro to a procedure, or name the let variable with names that starts and ends with underscores (_).

### Name scopes:

- Two global or two local variables can not have the same name, but if a local and a global variable have the same name, the local one will be reachable until it is removed from the scope.
- If a name is defined globally (for example with `memory`), it can be reached from anywhere meaning any procedure in and out of the same file.
- If a name is defined locally in a procedure, it can only be reached within the scope that the statement it is in. For example:


        // 'x' is undefined here.
        69 let x in 
          // 'x' is defined here.
        end
        // 'x' is undefined here.


### Comments:

    // This is a line comment, it can also come after code
    34 35 + putu  // Just like that

    /*
      This is a block comment, aka a multi-line comment.
      Block comments can span several lines.
    */
    
- Comments do not have any affect on the compiled program.

### Control flow:

    include "linux_x86/stdio.corth"

    proc main
      int int -> int
    in let argc argv in
      2 2 + 5 = if
        "Well, math is broken. Nice.\n" puts // Hopefully won't be printed.
      end

      3 4 > if
        "Your computer has virus\n" puts     // Hopefully won't be printed.
      else
        "Your computer is alright\n" puts    // Hopefully will be printed.
      end

      // Count from 0 to 9.
      "First 10 numbers from 0 are,\n" puts
      0 while dup 10 < do                    // Duplicate the number, and check if it is less then 10.
        dup putu "\n" puts                   // Print the number.
      inc end drop                           // Increase the number.
    end 0 end

- `if` is used for conditions, it runs the code after it only if the last item on the stack is true.
- `if` can be used with `else` for more functionality, which runs only if the bool is false.
- Because of the way Corth works, the `if-else` statement can be used like a ternary operator in other languages.
- `while` is used for loops, and `break` can be used to quit the loop early.
- If `if` is used without an `else`, the stack must not change between `if` and `end` since otherwise it will create an ambiguity of what the stack will be after that part.
- If `if` is used with an `else`, the stack change between `if` and `else` must be the same for the code between `else` and `end`.
- Stack must not change between `while` and `end`.
- Even though parser does not care for indentation, it is still a good idea to indent since in Corth these operations can get very hard to understand very quickly.
- Sadly, Corth does not have `else if/elif` statements at the moment.

### Let:

     // The rightmost variable collects the newest item in the stack. So x = 3 and y = 4.
     // From now on, x will be replaced with 3 and y will be replaced with 4.
     // If 'let' variables are compile-time constants, the variables will be directly replaced for optimization reasons.
     // Otherwise, the stack values will be stored in local memory and loaded inside the structure.
     3 4 let x y in
       x y * x + y -
     end
     // Stack = { 10 }

- `let` keyword stores stack items in local memory. The stored values can not be modified but can be read later.
- When any `let` variable is called, it directly returns its value; unlike a `memory` variable which returns its address.

### Peek:

     // The rightmost variable collects the newest item in the stack. So x = 3 and y = 4.
     // From now on, x will be replaced with 3 and y will be replaced with 4.
     3 4 peek x y in
       x y * x + y -
     end
     // Stack = { 3, 4, 10 }

- `peek` works very similar to `let`, except it does not pop the items from the stack. This allows it to directly load them from the stack instead of using the local memory.
- When any `peek` variable is called, it directly returns its value; just like `let`.

### Static memory management:

    include "core/memory.corth"

    // This is a global variable.
    // The size must be a compile-time constant as memory is allocated in compile-time.
    memory count sizeof(int) end
    
    proc increase -> in
      // Reads the value of 'count', adds one and writes back.
      count @64 inc count !64
    end

    proc main
      int int -> int
    in let argc argv in
      // Set the value of 'count' to 0.
      0 count !64

      // Increase the value of 'count'.
      increase

      // Print the value stored at 'count'. Should print '1'.
      count @64 putu putnl
      
      memory x sizeof(int) in
      memory y sizeof(int) in // Size of the variable 'x' is equal to the size of an integer (8 bytes). Same with variable 'y'.
	       
        0 x !64
        x @64 puti " is before saving 'x'\n" puts
        420 x !64
        x @64 puti " is after saving 'x'\n" puts
        
        0 y !64
        y @64 puti " is before saving 'y'\n" puts
        69 y !64
        y @64 puti " is after saving 'y'\n" puts
        
      end end
    end 0 end

- `memory` is used for allocating global or local memory in compile-time.
- When a variable name declared by `memory` keyword is called; the address of the variable is returned.
- When used globally, `memory` allocates memory that can be used from everywhere after definition.
- When used locally, `memory` allocates memory that can be used only in between `in` and `end`.
- `@64` loads 8 bytes of data from the address. (`@8`, `@16` and `@32` are also allowed)
- `!64` stores 8 bytes of data to the address.

### Dynamic memory management:

    include "dynamic/malloc.corth"

    // Assume this is inside a procedure.
    100 malloc let buffer in  // Allocate 100 bytes of memory and save the object pointer as a constant named `buffer`.
      // Loop through every byte in `buffer`.
      buffer while dup buffer 100 + < do peek address in
        0x67 address !8  // Set the byte to 0x67.
      end inc end drop

      buffer mfree drop // Deallocate the space.
    end

- *std/dynamic/* directory contains some dynamic memory management utilities, like `malloc` or `djoin`. Please check the library to learn more.

### Collections:

- *std/collections/* directory contains different kinds of data structures. Most of these are terribly implemented though :(.
