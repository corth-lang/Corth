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
- Everything in this language can be changed at any time. Use with caution.

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
- THIS BEHAVIOUR WILL BE CHANGED IN A FUTURE UPDATE! BE CAREFUL.

### Arithmetic operators:

    34 35 +
    
    69 27 -

- '+' adds the last two items and pushes the result back, '-' subtracts.

    70 dec
    
    41 inc

- 'inc' increases the last item in the stack once, 'dec' decreases.

### dump:

    34 35 + dump

- 'dump' prints the last item on the stack.
- THIS WILL BE REMOVED IN A FUTURE UPDATE! BE CAREFUL.

### Including modules:

    include libs/str.corth

- 'include' allows to use external code.

### Procedures:

    proc sum
        int int returns int int int
    in
        dup rot dup rot +

        0
    end

    proc main
        returns int
    in
        17 52 sum dump dump dump
	// This should print 69, 52 and 17
    end

- 'proc' defines a procedure, which can be called anywhere in the code.
- Program starts from the 'main' procedure; if it is not defined, the compiler will return an error.

### Comments:

    // This is a line comment, it can also come after code
    34 35 + dump  // Just like that

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
      "Your computer is broken." puts
    else
      "Your computer is alright, unlike you." puts
    end

    "First 10 numbers from 0 are,\n" puts
    0
    while
      dup 10 <
    do
      dup dump
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
