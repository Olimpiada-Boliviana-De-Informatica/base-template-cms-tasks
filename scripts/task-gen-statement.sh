gen_statement() {
  bash scripts/task-view-statement.sh $1 "no-browser" &
  cd tasks || exit

  python3 .commons/export_pdf.py "$2" "$1/statement" "$3"
}

get_problem_name_from_json() {
  local JSON_FILE="$1"

  if [ -z "$JSON_FILE" ]; then
    echo "Error: Debes proporcionar la ruta al archivo JSON." >&2
    return 1
  fi

  if [ ! -f "$JSON_FILE" ]; then
    echo "Error: El archivo '$JSON_FILE' no se encontró." >&2
    return 1
  fi

  grep '"name":' "$JSON_FILE" | head -1 | sed -e 's/.*"name": "\(.*\)",/\1/' | xargs

  local LAST_PIPE_STATUS=${PIPESTATUS[0]} # grep
  if [ "${#PIPESTATUS[@]}" -ge 2 ]; then
      LAST_PIPE_STATUS=${PIPESTATUS[4]} # xargs
  fi

  return 0
}

problem_name=$(get_problem_name_from_json "tasks/$1/problem.json")

gen_statement $1 $problem_name $2
