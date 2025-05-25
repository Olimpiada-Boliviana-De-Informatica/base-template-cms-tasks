#/usr/bin/env python

from pyppeteer import launch
import asyncio, sys, os
import http.server, socketserver
import functools, threading
import subprocess
import socket

PYPPETEER_PDF_OPTIONS = {
    'margin': {
        'left': '0.75in',
        'right': '0.75in',
        'top': '0.62in',
        'bottom': '1in',
    },
    'format': 'A4',
    'printBackground': True,
}


def write_exception_messages(exc, stream=sys.stderr):
    while exc is not None:
        stream.write("{}\n".format(str(exc)))
        exc = exc.__cause__


PORT = 8000

def kill_process_on_port(port):
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        lines = result.stdout.strip().split("\n")
        for line in lines[1:]:  # saltamos el encabezado
            parts = line.split()
            pid = parts[1]
            os.system(f"kill -9 {pid}")
    except Exception as e:
        print(f"Error al intentar liberar el puerto {port}: {e}")

def find_free_port(start_port=8000, max_port=9000):
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free ports available")

async def convert_to_pdf(statement_path, pdf_file, task_name):
    httpd = None
    PORT = find_free_port()
    try:
        kill_process_on_port(PORT)
        Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=statement_path)
        httpd = socketserver.TCPServer(("", PORT), Handler)
        sys.stderr.write(f"serving at port {PORT}\n")
        thread = threading.Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()

        browser = await launch(options={'args': ['--no-sandbox']})
        page = await browser.newPage()
        await page.goto(f'http://localhost:{PORT}/index.html', {
            'waitUntil': 'networkidle2',
        })
        await page.emulateMedia('print')
        await page.pdf({
            'path': pdf_file,
            **PYPPETEER_PDF_OPTIONS,
            'displayHeaderFooter': True,
            'footerTemplate': f'''
                </style>
                <div style="font-size: 16px; width: 100%; text-align: right; color: #666666; padding: 0 72px 10px 0; font-family: Arial;">
                    {task_name} (<span class="pageNumber"></span> de <span class="totalPages"></span>)
                </div>
            ''',
            'headerTemplate': '<div></div>',
        })
        await browser.close()
        httpd.shutdown()
        httpd.server_close()
    except Exception as e:
        sys.stderr.write("Exception in converting to pdf\n")
        write_exception_messages(e)
    finally:
        PORT = PORT + 1
        if httpd:
            httpd.shutdown()
            httpd.server_close()
            sys.stderr.write("Servidor cerrado correctamente.\n")



def add_page_numbers_to_pdf(pdf_file_path, task_name):
    color =  '-color "0.4 0.4 0.4" '
    cmd = ('cpdf -add-text "{0} (%Page of %EndPage)   " -font "Arial" ' + color + \
          '-font-size 10 -bottomright .62in {1} -o {1}').format(task_name, pdf_file_path)
    os.system(cmd)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} task_name statement_path output_file")
        exit(1)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(convert_to_pdf(sys.argv[2], sys.argv[3], sys.argv[1]))
#     add_page_numbers_to_pdf(sys.argv[3], sys.argv[1])
