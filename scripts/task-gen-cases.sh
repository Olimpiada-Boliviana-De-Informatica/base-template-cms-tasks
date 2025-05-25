gen_cases() {

  cd tasks || exit

  for item in "$@"; do
    echo "Task: $item"

    cd "$item" || exit

    tps gen

    cd ..
  done
  cd ..
}

gen_cases "$@"
