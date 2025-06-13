#!/bin/bash

# wget, zip and jq required

gen_zip() {
  cd tasks || exit

  for task_name in "$@"; do
    echo "Task: $task_name"
    cd "$task_name" || exit
    wget https://github.com/Pantnkrator/boca-problem-base/archive/refs/heads/master.zip
    unzip master.zip
    rm master.zip
    rm ./boca-problem-base-master/README.md

    mkdir -p "./boca-problem-base-master/input"
    mkdir -p "./boca-problem-base-master/output"

    inputs=($(ls "./tests"/*.in 2>/dev/null | sort))
    count=1

    for infile in "${inputs[@]}"; do
      base=$(basename "$infile" .in)
      outfile="./tests/${base}.out"

      cp "$infile" "./boca-problem-base-master/input/file${count}"

      if [ -f "$outfile" ]; then
        cp "$outfile" "./boca-problem-base-master/output/file${count}"
      fi

      ((count++))
    done

    cp ./statement/*.pdf "./boca-problem-base-master/description/"
    archivo_pdf=$(find "./statement/" -maxdepth 1 -name '*.pdf' | head -n 1)
    nombre_pdf=$(basename "$archivo_pdf")
    title=$(jq -r '.title' ./problem.json)
    time_limit=$(jq -r '.time_limit' ./problem.json)
    memory_limit=$(jq -r '.memory_limit' ./problem.json)
    max_size=$(du -k ./boca-problem-base-master/output/* | sort -nr | head -n 1 | cut -f1)
    size_limit=$((max_size + 10))


    echo "basename=Main
fullname=${title}
descfile=${nombre_pdf}" > "./boca-problem-base-master/description/problem.info"

    echo "echo $(printf "%.0f" "$time_limit")
echo 1
echo ${memory_limit}
echo ${size_limit}
exit 0" > ./boca-problem-base-master/limits/c

    echo "echo $(printf "%.0f" "$time_limit")
echo 1
echo ${memory_limit}
echo ${size_limit}
exit 0" > ./boca-problem-base-master/limits/cc

    time_limit_java=$(( time_limit * 2 ))
    echo "echo $(printf "%.0f" "$time_limit_java")
echo 1
echo ${memory_limit}
echo ${size_limit}
exit 0" > ./boca-problem-base-master/limits/java

    echo "echo $(printf "%.0f" "$time_limit_java")
echo 1
echo ${memory_limit}
echo ${size_limit}
exit 0" > ./boca-problem-base-master/limits/py2

    echo "echo $(printf "%.0f" "$time_limit_java")
echo 1
echo ${memory_limit}
echo ${size_limit}
exit 0" > ./boca-problem-base-master/limits/py3

    cd ./boca-problem-base-master/
    zip -r ./${task_name}.zip .
    mv ./${task_name}.zip ../${task_name}.zip
    cd ..
    rm -rf ./boca-problem-base-master/

  done
}

gen_zip $1
