import code128
import pdfkit
import requests
import base64
import tempfile
import os
from io import BytesIO
from config import SOFTCHEQUE_URL, PRINT_COMMAND, SOFTCHEQUE_PRINTER
from app.zpl_printing.functions import send_to_print
from app.helpers import make_error, show_gtk_error_modal


def send_to_setkitx(data, window):
    if not data:
        print('Empty data!')
        return
    print('data to send ', data)

    # window = kwargs['window']

    res = _post_to_setkitx(data)
    if res.get('error'):
        show_gtk_error_modal(window, res['message'])
        return

    # создание на принтер мягких чеков
    #make_barcode_image(res['result']['guid'])

    # отправить на зебру по сокету
    send_to_print(res['result']['guid'])


def _post_to_setkitx(data):
    timeouts = 4
    try:
        res = requests.post(url=SOFTCHEQUE_URL, json={'wares': data}, timeout=timeouts)

        if res.status_code >= 400:
            msg = str(res.url) + ' вернулся код статуса: ' + str(res.status_code)
            print(msg)
            return make_error(msg)

        res = res.json()

        if res.get('error'):
            msg = str(res.url) + ' Вернулась Ошибка с Setkitx API: ' + str(res['message'])
            print(msg)
            return make_error(msg)

        return res

        # guid = res['result']['guid']
        # print('GUID --> ' + str(guid))
        # make_barcode_image(guid)

    except requests.RequestException as e:
        msg = 'Возникло исключение requests.RequestException: ' + str(e.__class__.__name__)
        print(msg)
        return make_error(msg)


def make_barcode_image(guid):

    pdf_file = tempfile.NamedTemporaryFile()
    pdf_file.name += '.pdf'

    imgTemp = BytesIO()
    img = code128.image(str(guid))

    options = {
        'page-width': '80mm',
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
    os.system('{0} {1} {2}'.format(PRINT_COMMAND, SOFTCHEQUE_PRINTER, pdf_file.name))
