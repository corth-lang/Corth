BUILD_ITERATION=3

ERROR='\x1b[1;31m[ERROR]\x1b[0;97m'
INFO='\x1b[1;97m[INFO]\x1b[0;97m'

echo -e '[build.sh] '$INFO' Creating build directory...'
mkdir ./Corth/build/

echo -e '[build.sh] '$INFO' Copying ./Corth/corth to ./Corth/build/corth'
cp ./Corth/corth ./Corth/build/

echo -e '[build.sh] '$INFO' Starting to compile ./Corth/compiler/corth.corth'
echo -e '[build.sh] '$INFO' Iteration depth is '$BUILD_ITERATION.

for i in $(seq 1 $BUILD_ITERATION); do
  ./Corth/build/corth compile-nasm ./Corth/compiler/corth.corth ./Corth/build/corth.asm
  compile_exit=$?

  if [[ $compile_exit != 0 ]]; then
     echo -e '[build.sh] '$ERROR' ['$i/$BUILD_ITERATION'] Could not compile to NASM.'
     rm -rf ./Corth/build/
     exit $compile_exit
  fi

  echo -e '[build.sh] '$INFO' ['$i/$BUILD_ITERATION'] Compiled to NASM.'

  nasm ./Corth/build/corth.asm -f elf64 -o ./Corth/build/corth.o
  nasm_exit=$?

  if [[ $nasm_exit != 0 ]]; then
     echo -e '[build.sh] '$ERROR' ['$i/$BUILD_ITERATION'] Could not compile NASM program.'
     rm -rf ./Corth/build/
     exit $nasm_exit
  fi

  echo -e '[build.sh] '$INFO' ['$i/$BUILD_ITERATION'] Created the object file.'

  ld ./Corth/build/corth.o -o ./Corth/build/corth
  linker_exit=$?

  if [[ $linker_exit != 0 ]]; then
     echo -e '[build.sh] '$ERROR' ['$i/$BUILD_ITERATION'] Could not link program.'
     rm -rf ./Corth/build/
     exit $linker_exit
  fi

  echo -e '[build.sh] '$INFO' ['$i/$BUILD_ITERATION'] Created executable.'
done

echo -e '[build.sh] '$INFO' Starting tests...'

./PythonCompiler/main.py test -ce -p ./Corth/build/corth
tests_exit=$?

if [[ $tests_exit != 0 ]]; then
    echo -e '[build.sh] '$ERROR' Tests failed.'
    rm -rf ./Corth/build/
    exit $tests_exit
fi

echo -e '[build.sh] '$INFO' Tests succeded, moving ./Corth/build/corth to ./Corth/corth.'

mv ./Corth/build/corth ./Corth/corth
rm -rf ./Corth/build/

echo -e '[build.sh] '$INFO' Done.'
