gen_zip() {
  cd tasks || exit

  for task_name in "$@"; do
    echo "Task: $task_name"
    cd "$task_name" || exit
#    tps export CMS 1 --statement-pdf statement/es.pdf
    tps export CMS 1
    # adding statements
    file_zip="$(ls -1t *.zip | head -n 1)"
    rm -rf "./$file_zip-tmp"
    unzip "$file_zip" -d "./$file_zip-tmp"

    first_subfolder=$(find "./$file_zip-tmp" -mindepth 1 -maxdepth 1 -type d | sort | head -n 1)
    task_code=$(basename "$first_subfolder")

    mkdir -p "./$file_zip-tmp/$task_code/statements"
    cp statement/*.pdf "./$file_zip-tmp/$task_code/statements"
    rm -rf "./$file_zip"
    cd "./$file_zip-tmp"
    zip -r "../$file_zip" "./$task_code/"
    cd ..
    rm -rf "./$file_zip-tmp"
  done
}

gen_zip $1
