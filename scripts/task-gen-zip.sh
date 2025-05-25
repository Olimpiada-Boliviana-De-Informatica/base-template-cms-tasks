gen_zip() {
  cd tasks || exit

  for task_name in "$@"; do
    echo "Task: $task_name"
    cd "$task_name" || exit
    tps export CMS 1 --statement-pdf statement/es.pdf
  done
}

gen_zip $1
