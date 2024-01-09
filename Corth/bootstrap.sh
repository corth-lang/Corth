ERROR='\x1b[1;31m[ERROR]\x1b[0;97m'
INFO='\x1b[1;97m[INFO]\x1b[0;97m'

echo -e '[build.sh] '$INFO' Creating build directory...'
mkdir ./Corth/build/

echo -e '[build.sh] '$INFO' Copying ./Corth/corth to ./Corth/build/corth'
cp ./Corth/corth ./Corth/build/

echo -e '[build.sh] '$INFO' Starting to compile ./Corth/compiler/corth.corth'

i=0;

while
    cp ./Corth/build/corth ./Corth/build/old
    
    i=$(( $i + 1 ))
    
    ./Corth/build/old compile ./Corth/compiler/corth.corth -i . --output-path ./Corth/build/corth
    compile_exit=$?

    if [[ $compile_exit != 0 ]]; then
        echo -e '[build.sh] '$ERROR' [ #'$i' ] Could not compile.'
        exit $compile_exit
    fi

    echo -e '[build.sh] '$INFO' [ #'$i' ] Compiled ('$(wc -l < ./output.asm)' lines).'

    not diff ./Corth/build/corth ./Corth/build/old
do :; done

echo -e '[build.sh] '$INFO' Reached stability in '$i' tries, starting tests...'

./PythonCompiler/main.py test -eo -p ./Corth/build/corth
tests_exit=$?

if [[ $tests_exit != 0 ]]; then
    echo -e '[build.sh] '$ERROR' Tests failed.'
    exit $tests_exit
fi

echo -e '[build.sh] '$INFO' Tests succeded, moving ./Corth/build/corth to ./Corth/corth.'

mv ./Corth/build/corth ./Corth/corth
rm -rf ./Corth/build/

echo -e '[build.sh] '$INFO' Done.'
