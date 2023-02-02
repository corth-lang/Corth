# Corth
A programming language made with inspiration of Porth, which is a programming language made with inspiration of Forth.

parser_lib.py contains the parser, which returns a list of tokens.

compiler_lib.py contains the compiler, which creates the NASM program.

main.py allows the usage of command-line for easy access.

For now, the language is made in Python. Later, it will be rewritten in itself.
Because of that, you will need Python in your machine. (>=Python3.7 because of the f-strings)


## How to use the compiler?

To compile a Corth program to an executable, type this in a command-line in the Corth folder.

    python3 main.py compile <source>

For more information about the commands, type:

    python3 main.py -h


## Quick start to the Corth language

- Corth is a concatinative (stack based) language.
- Programs are compiled into NASM first, then into an executable.
- Everything can be inlined. The return character is used only to end inline comments and to add the newline character to the strings.
- Indentation and spaces mean nothing to the parser.

- EVERYTHING IN THIS LANGUAGE CAN BE CHANGED AT ANY TIME. USE WITH CAUTION.

### First program:

    include libs/io.corth
    
    proc main 
      returns int
    in
      "Hello, World!\n" puts
      
      0
    end
    
- This is a simple program that prints "Hello, World!" when run.
- 'include' is used to include the library io.corth, which contains some I/O operations like writing to files and the standard output.
- 'proc' is used to define a procedure. 'main' is where the program starts.
- 'puts' is used to print a string to the standard output.
- For more examples, you can check the ./examples/ directory.
- For more information about these concepts, keep scrolling.

### Numbers:

    34 0b101001 0o205126 0x5729da
    'a' '\n'

- Numbers push an integer type to the stack.
- Putting a character between '' causes it to be interpreted as an integer, its ASCII value.
- Escapes are supported in characters.

### Strings:

    "This is a string"

    "This also is a string.
     In Corth, multi-line strings are supported."

- Strings push two numbers, the address and the length of the string.
- THIS BEHAVIOUR WILL BE CHANGED IN A FUTURE UPDATE! USE WITH CAUTION.

### Arithmetic operators:

    34 35 +
    
    69 27 -
    
    68 inc
    
    43 dec

- '+' adds the last two items and pushes the result back, '-' subtracts.
- 'inc' increases the last item in the stack once, 'dec' decreases.

### Including modules:

    include libs/str.corth

- 'include' allows to use external code.

### I/O:

    "Hello, world!\n" puts
    34 35 + putu " is a nice number.\n" puts

- libs/io.corth contains useful procedures for I/O operations.

### Procedures:

    proc sum
        int int returns
    in
        "Sum of these numbers are: " puts + putu "\n" puts
    end

    proc main
        returns int
    in
        17 52 sum
    end

- 'proc' defines a procedure, which can be called anywhere in the code.
- Program starts from the 'main' procedure; if it is not defined, the compiler will return an error.

### Macros:

    macro sayHi
        // Takes a string, the name

        "Hi, " puts puts "!\n" puts
    endmacro

    proc main
        returns int
    in
        "Josh" sayHi
	
	0
    end

- 'macro' keyword is used to define macros and 'endmacro' is used to end the definition.

### Comments:

    // This is a line comment, it can also come after code
    34 35 + putu  // Just like that

    /*
      This is a block comment, also known as multi-line comment.
      This is still in comment.
      And it still is.
      This can also come after code, but I am too lazy to write an example for that.
      Code can come after that comment, too.
    */

### Control flow:

    2 2 + 5 = if
      "Well, math is broken. Nice.\n" puts
    end

    3 4 > if
      "Your computer has virus\n" puts
    else
      "Your computer is alright, unlike you\n" puts
    end

    "First 10 numbers from 0 are,\n" puts
    0
    while
      dup 10 <
    do
      dup putu
      "\n" puts

      dup 100 = if
        "How!?\n" puts
	break
      end

      inc
    end

    drop

- 'if' is used for conditions.
- 'if' can be used with 'else' for more functionality.
- 'while' is used for loops, and 'break' can be used to quit the loop early.

### Memory management:

    memory count 8
    
    proc increase
        returns
    in
        count dup load8 inc store8
    end

    proc main
        returns int
    in
        count 0 store8

        increase

        count load8 putu

        0
    end

- 'memory' is used for allocating global memory.
- 'load8' loads 8 bytes of data from the address.
- 'store8' stores 8 bytes of data to the address. (First argument is address and the second is the value to be stored)
- SYNTAX FOR MEMORY IS A PLACEHOLDER. IT WILL BE CHANGED IN A FUTURE UPDATE. USE WITH CAUTION.
