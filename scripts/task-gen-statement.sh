gen_statement() {
  cd tasks || exit

  python3 .commons/export_pdf.py "$2" "$1/statement" "$1/statement/$3.pdf"
}

gen_statement $1 $2 $3
