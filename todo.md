# TODO LIST:

## New compiler:

- Implement global variables.
- Implement macros.
- Add types for let variables.
- Implement more complex patterns of scopes.
- Implement an optimization model.

## New ideas:

- Implement types.
- Implement local labels.
- Implement goto.
- Implement local macros.

## Libraries:

- Rewrite string library.
- Remake core library macros to take advantage of precompilation.
- Remove malloc.sew and remake malloc.free.
- Remake queue64.sort and implement quick sort.
- Add mmap and remake malloc and mfree using mmap.
- I/O macro and procedures should be rewritten for performance reasons.
- Implement a new I/O library that allows buffered writes.
- Create an OS or path library that allows path operations like merging or splitting.
- Create a vector library.
- Most of ./libs/memory.corth macro and procedures would be more efficient if they worked with pointers and not indexes.
- Add the information about the time complexity to collection libraries.
- deque64 library requires an insert and pop procedure.
- Add a string mapping library that uses hash instead of strings.

## Other:

- Make a test library.