# TODO LIST:

## New ideas:

#### Important: 

- Add 'break' stacking. Stacking 'break' n times will cause the program to break the nth loop.
- Implement 'promise' keyword, which allows to 'promise' to create procedures or global variables for cyclic procedure dependencies.
- Add types for let variables.
- Implement directory including.

#### Less important:

- Implement an optimization model.
- Single quotes can contain more than one character, this will put more integers to the stack.
- Implement local labels. (label here)
- Implement label type. (label <type>* end)
- Implement 'goto'. (goto here)
- Add promise for local labels.
- Implement local macros.
- Add calling standard C functions. (this would make life so damn simple)
- Add 'addrof' and 'proc' types. (addrof p) will be usable to get the address of a procedure, (proc <type>* -- <type>* end) will be usable to define the type of a procedure and (call p) will be usable to call a procedure address. That way, the types will be kept static.
- Add 'expect' which checks if the stack contains the right types. (expect type1 type2 ... end)
- Add 'switch' and 'case'. (<value> switch (case <case1> in <code1>)* end)
- Add compiler symbols.

## Libraries:

- Remake core library macros to take advantage of precompilation.
- Remove malloc.sew and remake malloc.mfree.
- Add mmap and remake malloc and mfree using mmap.
- I/O macro and procedures should be rewritten for performance reasons.
- Implement a new I/O library that allows buffered writes.
- Most of ./libs/core/memory.corth macro and procedures would be more efficient if they worked with pointers and not indexes.
- Add the information about the time complexity to collection libraries.
- deque64 library requires an insert and pop procedure.
- Add a string mapping library that uses hash instead of strings.

## New compiler symbols:

- #warn <message>: Causes the compiler to show a warning.
- #err <code> <message>: Causes the compiler to show an error and exit with an exit code.
- #isdef <name>: Checks if a name is defined and returns a bool.
- #isinc <path>: Checks if a library is included and returns a bool.

## New syntax ideas:

    let
      (<modifier>* <type> <name>)*
    in
      <any>
    end

## Modifier ideas:

- var (for 'let'): Create a variable that when called, returns the ADDRESS rather than the VALUE. This allows 'let' variables to be over-writable.

    69
    let var int x in
      [code]
    end

Will act similar to

    69
    memory x sizeof(int) in
      x !64
      [code]
    end

- local (for 'let'): Create the variable in the local scope. Placement of the variable will be calculated relative to the local stack pointer. Will be needed for recursion in functions if generalized memory approach is implemented.

- out (for 'let'): Output in the end of the 'let' statement. Not exactly super useful, but would help make the code more readable.

    69
    let out int x in
      [code]
    end

Will act similar to

    69
    let int x in
      [code]
      x
    end

## Notes:

- It is actually possible to remove the output definition from the procedure definition. Altough, not sure if that would be a good idea.
