view_statement() {
  cd tasks/$1/statement || exit
  for port in {8000..8010}; do
    if ! lsof -i :$port > /dev/null; then
      URL="http://127.0.0.1:$port/index.html"

      if command -v xdg-open > /dev/null; then
        xdg-open "$URL"
      elif command -v open > /dev/null; then
        open "$URL"
      elif command -v start > /dev/null; then
        start "$URL"
      else
        echo "❌ No se pudo abrir el navegador. Abre manualmente: $URL"
      fi

      http-server . -p $port
      exit
    fi
  done
}

view_statement $1
