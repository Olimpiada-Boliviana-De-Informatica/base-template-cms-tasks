#/usr/bin/env python

from pyppeteer import launch
import asyncio, sys, os
import http.server, socketserver
import functools, threading
import subprocess
import socket

PYPPETEER_PDF_OPTIONS = {
    'margin': {
        'left': '0.6in',
        'right': '0.6in',
        'top': '0.8in',
        'bottom': '0.8in',
    },
    'format': 'A4',
    'printBackground': True,
}


def write_exception_messages(exc, stream=sys.stderr):
    while exc is not None:
        stream.write("{}\n".format(str(exc)))
        exc = exc.__cause__


async def convert_to_pdf(statement_path, lang, task_name):
    httpd = None
    browser = None
    try:
        browser = await launch(options={'args': ['--no-sandbox']})
        page = await browser.newPage()
        await page.goto(f'http://localhost:1234/' + lang, {
            'waitUntil': 'networkidle2',
        })
        await page.emulateMedia('print')
        await page.pdf({
            'path': statement_path + '/' + lang + '.pdf',
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
    except Exception as e:
        sys.stderr.write("Exception in converting to pdf\n")
        write_exception_messages(e)
    finally:
        if browser:
            await browser.close()


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
    