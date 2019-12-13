import code128
import pdfkit
import requests
import base64
import tempfile
import os
from io import BytesIO
from config import SOFTCHEQUE_URL, PRINT_COMMAND, SOFTCHEQUE_PRINTER


def send_to_setkitx(data):
    if not data:
        print('Empty data!')
        return
    print('data to send ', data)
    _post_to_setkitx(data)


def _post_to_setkitx(data):
    timeouts = 4
    try:
        res = requests.post(url=SOFTCHEQUE_URL, json={'wares': data}, timeout=timeouts)

        if res.status_code >= 400:
            print('С API вернулся код статуса ' + str(res.status_code))

        res = res.json()

        if res.get('error'):
            print('Вернулась Ошибка с Setkitx API: ' + str(res['message']))
            return

        guid = res['result']['guid']
        print('GUID --> ' + str(guid))
        make_barcode_image(guid)

    except requests.RequestException as exc:
        print('SetkitX API Request exception! ' + str(exc))


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
           <hr/>
       </body>
    """.format(base64.b64encode(imgTemp.getvalue()).decode())
    pdfkit.from_string(sourceHtml, pdf_file.name, options=options)
    _send_barcodeimage_to_printer(pdf_file)


def _send_barcodeimage_to_printer(pdf_file):
    os.system('{0} {1} {2}'.format(PRINT_COMMAND, SOFTCHEQUE_PRINTER, pdf_file.name))
