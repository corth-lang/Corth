./Corth/build/corth compile-nasm ./Corth/compiler/corth.corth ./Corth/build/corth.asm
echo "[build.sh] [INFO] Compiled to NASM."
nasm ./Corth/build/corth.asm -f elf64 -o ./Corth/build/corth.o
echo "[build.sh] [INFO] Created the object file."
ld ./Corth/build/corth.o -o ./Corth/build/corth
echo "[build.sh] [INFO] Done."
