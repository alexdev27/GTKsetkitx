import code128
import pdfkit
import requests
import base64
import tempfile
import os
from io import BytesIO
from config import PRINT_COMMAND, PREFIX
from app.zpl_printing.functions import send_to_print
from app.helpers import make_error, show_gtk_error_modal


def send_to_setkitx(data, window):
    if not data:
        print('Empty data!')
        return

    res = _post_to_setkitx(data)
    if res.get('error'):
        show_gtk_error_modal(window, res['message'])
        return

    sys_print = bool(int(os.environ['SYS_ENABLE']))
    sock_print = bool(int(os.environ['SOCK_ENABLE']))
    # создание на принтер мягких чеков
    if sys_print:
        print('Выбран системный принтер')
        make_barcode_image(res['result']['guid'])
        pass

    # отправить на зебру по сокету
    if sock_print:
        print('Выбран принтер для отправки по сокету')
        send_to_print('%s%s' % (PREFIX, res['result']['guid']))
        pass


def _post_to_setkitx(data):
    timeouts = 4
    url = os.environ['SOFTCHEQUE_URL']
    try:
        res = requests.post(url=url, json={'wares': data}, timeout=timeouts)

        if res.status_code >= 400:
            msg = url + ' Ошибка. Вернулся код статуса: ' + str(res.status_code)
            print(msg)
            return make_error(msg)

        res = res.json()

        if res.get('error'):
            msg = url + ' Вернулась Ошибка с Setkitx API: ' + str(res['message'])
            print(msg)
            return make_error(msg)

        return res

        # guid = res['result']['guid']
        # print('GUID --> ' + str(guid))
        # make_barcode_image(guid)

    except requests.RequestException as e:
        msg = url + ' При попытке запроса в сервис генерации мягких чеков ' \
              'возникло исключение requests.RequestException: ' + str(e.__class__.__name__)
        print(msg)
        return make_error(msg)


def make_barcode_image(guid):

    pdf_file = tempfile.NamedTemporaryFile()
    pdf_file.name += '.pdf'

    imgTemp = BytesIO()
    img = code128.image('%s%s' % (PREFIX, guid))

    options = {
        'page-width': '120mm',
        'page-height': '120mm',
        'encoding': "UTF-8"
    }

    img.save(imgTemp, format='PNG')

    sourceHtml = """
       <body style="text-align: center;">
           <div>
               <img style="inline" src='data:image/png;base64,{0}' />
           </div>
       </body>
    """.format(base64.b64encode(imgTemp.getvalue()).decode())
    pdfkit.from_string(sourceHtml, 'app/testpdf.pdf', options=options)
    pdfkit.from_string(sourceHtml, pdf_file.name, options=options)
    _send_barcodeimage_to_printer(pdf_file)


def _send_barcodeimage_to_printer(pdf_file):
    printer = os.environ['SYS_PRINTER_NAME']
    printer = '\"{0}\"'.format(printer)
    os.system('{0} {1} {2}'.format(PRINT_COMMAND, printer, pdf_file.name))
