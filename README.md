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
      -- int
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

    34
    0b101001
    0o205126
    0x5729da
    'a'
    '\n'

- Numbers push an integer type to the stack.
- Different bases are possible: binary, octal, decimal and hexadecimal. These can be used with 0b, 0o and 0x.
- Putting a character between '' causes it to be interpreted as its ASCII value.
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
    3 23 *
    60 5 /

- '+' adds the last two items and pushes the result back, '-' subtracts, '*' multiplies and '/' divides.
- 'inc' increases the last item in the stack once, 'dec' decreases.

### Including modules:

    include libs/str.corth

- 'include' allows to use external code.
- ./libs/ directory contains some useful libraries like core.corth or str.corth.

### Stack operations:
  
    1 2 3 drop // stack is now  1  2
    34 35 dup  // stack is now 34 35 35
    45 23 swp  // stack is now 23 45
    1 2 3 rot  // stack is now  2  3  1
    1 2 3 arot // stack is now  3  1  2

- ./libs/core.corth contains some basic stack operations.
- 'drop' removes the last item from the stack.
- 'dup' duplicates the last item in the stack.
- 'swp' swaps the places of the last two items.
- 'rot' rotates the places of the last 3 items, by moving the first added to the last position.
- 'arot' does the exact opposite of what 'rot' does.
- If possible, it is recommended to use 'let' instead of those since these are already 'let' macros.
- There are some others, but it is recommended to check ./libs/core.corth for more information since they are a bit more complex.

### I/O:

    "Hello, world!\n" puts
    34 35 + putu " is a nice number.\n" puts

- ./libs/io.corth contains useful procedures for I/O operations like reading and writing to streams.

### Procedures:

    proc sum
        int int --
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
- If the procedure does not require recursion or macro, it is probably a better idea to use a macro.

### Macros:

    macro sayHi
        // Takes a string, the name

        "Hi, " puts puts "!\n" puts
    endmacro

    proc main
        -- int
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

    include libs/io.corth

    proc main
      -- int
    in
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
    end

- 'if' is used for conditions, it runs the code after it only if the last item on the stack is true.
- 'if' can be used with 'else' for more functionality, which runs only if the bool is false.
- If 'if' is used without an 'else', the stack must not change between 'if' and 'end' since otherwise it will create an ambiguity of what the stack will be.
- If 'if' is used with an 'else', the stack change between 'if' and 'else' must be the same for the code between 'else' and 'end'.
- Because of the way this language works, the 'if-else' statement can be used as ternary operator.
- 'while' is used for loops, and 'break' can be used to quit the loop early.

### Memory management:

    include libs/core.corth

    memory count sizeof(int) end
    
    proc increase
        --
    in
        count dup load8 inc store8
    end

    proc main
        returns int
    in
        count 0 store8

        increase

        count load8 putu

        memory x sizeof(int) and
	       y sizeof(int) in
	       
	  x 0 store8
	  x load8 puti " is before saving x\n" puts
	  x 420 store8
	  x load8 puti " is after saving x\n" puts
	  y 0 store8
	  y load8 puti " is before saving y\n" puts
	  y 69 store8
	  y load8 puti " is after saving y\n" puts
	end

        0
    end

- 'memory' is used for allocating global or local memory.
- When called a variable name; the address is returned, NOT the value.
- When used globally, 'memory' allocates memory that can be used from everywhere, even before the definition.
- But when used locally, 'in' should be added. 'end' will where the memory reserved will be allocated, and the names will be deleted.
- 'and' can be used to allocate more data without dealing with a huge chain of 'end's.
- 'load8' loads 8 bytes of data from the address.
- 'store8' stores 8 bytes of data to the address. (First argument is address and the second is the value to be stored)
- The memory keyword can only be used in the global space, and the size is calculated on the compile time.

### Let:

   3 4
   let x y in
     x y * x + y -
   end
   
   puti

- 'let' is used to make the stack management easier.
- When 'let' is reached, the variables are stored with the stack data. These names will be removed from the namescope when end is reached.
- When any 'let' variable is called, it directly returns its value, unlike a 'memory' variable.