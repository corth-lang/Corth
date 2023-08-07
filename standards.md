# Standards used to write the Corth libraries:

- Since Corth is a very chaotic looking language, to make writing and reading code easier, some standards are used (Even though some libraries may not exactly obey them).
- It is preferred to use 2-space indentaion. But it is okay to use 1 or 4-space indentation as well (but God please, don't use 3 or 5, or 8).
- Even though these are recommended by me, you can obviously use your preferred way of writing. These are just some possible guidelines that can help to write better code.

### Procedures:

- It is not preferred to define a procedure in one line. Instead, it is recommended to split the lines into 'proc' keyword, types, 'in' keyword, behaviour, 'end' keyword.


        proc <name>
          //// Shows the type and names of the parameters and outputs for descriptivity. Nothing else should be here.
          //// If there is no output, '--' can be not used.
          // <type>: <name> <type>: <name> ... -- <type>: <name> <type>: <name>

          //// Shows the types of the arguments and output. Nothing else should be here.
          //// Even if there is no output, '--' must be used (This might change in a future update).
          <type> <type> ... -- <type> <type> ...

          //// A description of the procedure.
          // Does ...

          //// Notes for undefined behaviours, segmentation fault causes, exceptions...
          // NOTE: Can cause ...
        in
          ...
        end


- If parameters are named using 'let', 'let' can be put on the same line as 'in' of procedure definition.


        proc <name>
          ...
        in let <name> <name> in
          ...
        end end
    

- If the procedure is the 'main' procedure, the following pattern is preferred.


        proc main
          //// No argument name description is required.
          int int -- int
          //// No procedure description is required.
          //// No note is required.
        in let argc argv in
          ...
        end 0 end
    

- Even if it does not make a difference, it is recommended to use the right type for descriptions, and not its equivalent.


        proc <name>
          //// Don't use int if it is a pointer, or int if it is an unsigned integer. Use the right names even though ptr or uint expands to a single int.
          // ptr: start int: length
          ptr int --
        ...


- It is recommended to split the lines of behaviour so that no line depends on another (or the dependency is minimalized). This way it is easy to see which command generates values and which one uses that value.


        ...
        //// Don't do:
        address address
        mlength
        malloc address mlength memcpy8
        //// Every line in this example requires another line, which can make it hard to debug or read.

        //// Instead, use:
        address address mlength malloc address mlength memcpy8
        //// This line does not depend on another line to fill or clean the stack.
        ...


- *./libs/core.corth* offers some stack management macros, which can help in many cases. However, if stack operations are complex; it is recommended to use 'let' since that way the program will be more efficient and simpler to understand.


        //// Don't do:
        proc to-dynamic
          // ptr: start int: length -- ptr: x
          ptr int -- ptr
        in
          dup malloc dup isn-null if
            swp memcpy8
          else
            drop drop drop
          end
        end
        //// This code causes many useless memory writes, and is very hard to understand.

        //// Instead, use:
        proc to-dynamic
          // ptr: start int: length -- ptr: x
          ptr int -- ptr
        in let start length in
          length malloc let new in
            new isn-null if
              start new length memcpy8
            end
          end
        end end
        //// This code minimizes useless memory references, and is easy to understand.


- But it is also important to not overuse 'let' since there are already macros that does some of its job.


        //// Dont do:
        let obj in
          obj obj mlength to-dynamic
        end
        //// This code uses 'let', even though there is a macro that does exactly that and shortens the code.

        //// Instead, use:
        dup mlength to-dynamic
        //// This code uses 'dup', which makes the code shorter.


### Macros:

- If the macro defines a behaviour and is as simple as several tokens and does not contain any name definitions, it can be defined in one line. In this case, the input and outputs should be commented in the same line and after the macro definition.


        //// A description of the macro.
        // Does ...

        //// Notes of the macro.
        // NOTE: Can cause ...
        macro <name> ... endmacro // <type>: <name> <type>: <name> ... -- <type>: <name> <type>: <name> ...


- If the macro defines 'let' variables, their name should start and end with underscores (_). This helps to make sure that they are not reused in the code that uses them.


        //// From ./libs/core/stack.corth
        macro dup let _a_ in _a_ _a_ end endmacro  


- If macros with similar patterns are defined together, the tokens can be aligned to keep the code easier to read.


        //// From ./libs/core/stack.corth
        macro dup let _a_     in _a_ _a_ end endmacro
        macro swp let _a_ _b_ in _b_ _a_ end endmacro


- If the macro is used to define a constant, no input or output description is required.


        //// From ./libs/math/constants.corth
        macro PI          0x03243F6A89 endmacro
        macro E           0x02B7E15162 endmacro
        macro rad-per-deg 0x000477D1A8 endmacro
        macro deg-per-rad 0x394BB834BE endmacro


### 'for' loops:

- If a 'for' loop is required, it can be created using a standard pattern.


        //// This defines a 'for' loop that starts from <start>, and increases until <end>.
        //// If <end> is less than <start>, 'inc' and '<' should be replaced with 'dec' and '>'.
        //// Equality can also be used if <end> should be in the range (like <= or >=).
        <start> while dup <end> < do
          ...
        inc end drop
    

- The variable can be named with a 'let' statement. But instead of using a new line, 'let' statement can be kept in the 'while-do' line.


        //// Loop from <start> to <end>, and names that as <var>.
        <start> while dup <end> < do let <var> in
          ...
        <var> end inc end drop
        //// "<var> inc end end drop" whould also work.


### 'do-while' loops:

- A 'while' loop can also be used as a 'do-while' loop using a standard pattern.


        //// This defines a 'while' loop that runs a code and after, checks whether a condition is true.
        //// Because of the syntax of Corth language, any command can be written between 'while-do' or between 'do-end'.
        while
          <code>
        <condition> do end
        //// <code> will run at least once.


### A better general understanding of 'while':

- 'while' loop does not work the exact same way it usually does in other languages.


        //// In Corth, 'while' keyword is used only as a jump tag. When an 'end' of 'while' is reached, it jumps directly back to 'while' which allows loops. 'do' is the actual code that checks the condition.
        while //// This is where 'end' jumps to.
        
          //// This part is run BEFORE condition is checked. This is why it can be used for 'do-while' loops.


          //// This is the condition. Note that this is just a part of the code above, that returns a bool for 'do'. Because of that, condition could definitily be returned before any other code is run.
          <condition> ...
          
        do    //// Check if the value is true and if not; jump to the location AFTER 'end', breaking the loop.
        
          //// This code will run AFTER condition is checked. This part can also contain 'break', which (just like 'do') jumps to the location after 'end'.
          <code> ...
          
        end   //// Jump back to 'while'.
        
        //// This is the location 'do' and 'break' jumps.


- It should be noted that after 'end' is reached, program will jump to 'while'. This is why stack must be the same, since otherwise the stack would grow or shrink at every iteration which would cause very big problems.


### Standardization:

- It is recommended to use is-zero, isn-zero, is-pos... (or is-null and isn-null for pointers) from *./libs/core.corth* instead of their exact meanings, even though they mean the exact same thing. This is important, because in the case of an update to the language the way '=' works might change and '0 =' may not work as efficient as possible anymore (or not even work). In that case, 'is-zero' would also be updated to compare in the most efficient way possible.
