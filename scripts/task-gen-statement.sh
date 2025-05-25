gen_statement() {
  cd tasks || exit

  python3 .commons/export_pdf.py "$1" "$1/statement" "$1/statement/es.pdf"
}

gen_statement $1
