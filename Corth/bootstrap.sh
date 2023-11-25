./Corth/build/corth compile-nasm ./Corth/compiler/corth.corth ./Corth/build/corth.asm
compile_exit=$?

if [[ $compile_exit != 0 ]]; then
   echo "[build.sh] [ERROR] Could not compile to NASM."
   rm ./Corth/build/corth.asm
   exit $compile_exit
fi

echo "[build.sh] [INFO] Compiled to NASM."

nasm ./Corth/build/corth.asm -f elf64 -o ./Corth/build/corth.o
nasm_exit=$?
rm ./Corth/build/corth.asm

if [[ $nasm_exit != 0 ]]; then
   echo "[build.sh] [ERROR] Could not compile NASM program."
   rm ./Corth/build/corth.o
   exit $nasm_exit
fi

echo "[build.sh] [INFO] Created the object file."

ld ./Corth/build/corth.o -o ./Corth/build/corth
linker_exit=$?
rm ./Corth/build/corth.o

if [[ $linker_exit != 0 ]]; then
   echo "[build.sh] [ERROR] Could not link program."
   rm ./Corth/build/corth
   exit $linker_exit
fi

echo "[build.sh] [INFO] Done."
