#!/bin/bash

sync_folders() {
  rm -rf tasks/.commons/statement-viewer/resources
  ln -s "$(realpath tasks/$1/statement)" tasks/.commons/statement-viewer/resources
  ln -s "$(realpath tasks/$1/problem.json)" tasks/.commons/statement-viewer/data/problem.json
}

sync_folders $1

cd tasks/.commons
lsof -ti :1234 | xargs kill -9
serve -p 1234 statement-viewer &

URL="http://localhost:1234"

if command -v xdg-open > /dev/null; then
  xdg-open "$URL"
elif command -v open > /dev/null; then
  open "$URL"
elif command -v start > /dev/null; then
  start "$URL"
else
  echo "❌ No se pudo abrir el navegador. Abre manualmente: $URL"
fi
