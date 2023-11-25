mkdir ./Corth/build/

./Corth/corth compile-nasm ./Corth/compiler/corth.corth ./Corth/build/corth.asm
compile_exit=$?

if [[ $compile_exit != 0 ]]; then
   echo '[build.sh] [ERROR] Could not compile to NASM.'
   rm -rf ./Corth/build/
   exit $compile_exit
fi

echo '[build.sh] [INFO] Compiled to NASM.'

nasm ./Corth/build/corth.asm -f elf64 -o ./Corth/build/corth.o
nasm_exit=$?

if [[ $nasm_exit != 0 ]]; then
   echo '[build.sh] [ERROR] Could not compile NASM program.'
   rm -rf ./Corth/build/
   exit $nasm_exit
fi

echo '[build.sh] [INFO] Created the object file.'

ld ./Corth/build/corth.o -o ./Corth/build/corth
linker_exit=$?

if [[ $linker_exit != 0 ]]; then
   echo '[build.sh] [ERROR] Could not link program.'
   rm -rf ./Corth/build/
   exit $linker_exit
fi

echo '[build.sh] [INFO] Starting tests...'

./PythonCompiler/main.py test -ceo
tests_exit=$?

if [[ $tests_exit != 0 ]]; then
    echo '[build.sh] [ERROR] Tests failed.'
    rm -rf ./Corth/build/
    exit $tests_exit
fi

echo '[build.sh] [INFO] Tests succeded, moving ./Corth/build/corth to ./Corth/corth.'

mv ./Corth/build/corth ./Corth/corth
rm -rf ./Corth/build/

echo '[build.sh] [INFO] Done.'
