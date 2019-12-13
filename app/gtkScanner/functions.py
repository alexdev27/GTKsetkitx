from functools import reduce

import requests
from config import WAREINFO_API_URL
from .models import prod_codes, barcodes
from .constants import RM, ADD
from app.helpers import round_half_down


def request_to_wareinfo(barcode):
    timeouts = 4

    try:
        res = requests.get(WAREINFO_API_URL + barcode, timeout=timeouts)
        if res.status_code >= 400:
            print(' ---> Ошибка запроса. Код ошибки: ' + str(res.status_code))
            return None

        res = res.json()
        if res.get('error'):
            print(' ---> Ошибка с сервиса API: ' + str(res['message']))
            return None

        return res
    except requests.RequestException as e:
        print(' ---> Request Exception: ' + str(e))
        return None


def check_in_main_list_of_barcodes_and_modify(barcode, command, window):
    kwargs = {'barcode': barcode, 'command': command, 'liststore': window.liststore, 'window': window}

    if barcode not in barcodes.keys():
        if command == ADD:
            info = request_to_wareinfo(barcode)
            print('barcode  > ', barcode)
            if not info:
                return

            print('barcode_info: {0} - {1} - {2} - {3}'
                  .format(barcode, info['code'], info['measure'], info['quantity']))

            # обновляем листстор и кэш баркодов
            process_success_request(info, **kwargs)
    else:
        _add_or_remove(info=None, from_request=False, **kwargs)


def modify_liststore_row(barcode, liststore, command, actual_qty, actual_price, **kwargs):
    for indx, row in enumerate(liststore):
        if row[0] == barcode:
            modify_row(indx, liststore, command, row, actual_qty, actual_price, barcode=barcode, **kwargs)
            break


def process_success_request(info, **kwargs):
    # kwargs = {'barcode': barcode, 'command': command, 'liststore': liststore}
    _add_or_remove(info, from_request=True, **kwargs)


def _add_or_remove(info, from_request, **kwargs):
    barcode = kwargs['barcode']
    liststore = kwargs['liststore']
    command = kwargs['command']
    window = kwargs['window']
    if from_request:
        code = info['code']
        name = info['name']
        ratio = info['ratio']
        price = info['price']
        qty = info['quantity']
        measure = info['measure']
    else:
        ratio = barcodes[barcode][1]
        code = barcodes[barcode][0]
        qty = barcodes[barcode][2]
        price = prod_codes[code][2]
        name = prod_codes[code][1]
        measure = prod_codes[code][3]

    actual_price = float(ratio * price * qty)
    actual_qty = float(ratio * qty)

    # кэшируем записи, если это пришло с запроса
    if from_request:
        _list_to_cache = [code, name, price, measure]
        prod_codes[code] = _list_to_cache
        barcodes[barcode] = [code, ratio, qty]

    # если в листсторе есть такой продукт, то обновляем его
    # и возвращаем флаг модификации (true, false)
    if check_row_exist(liststore, barcode):
        modify_liststore_row(barcode, liststore, command, actual_qty, actual_price, window=kwargs['window'])
    # если в листсторе записи не оказалось и это операция добавления, то добавляем
    elif command == ADD:
        args = [barcode, code, name, actual_price, actual_qty, measure]
        liststore.append(args)
        window.applied_barcodes.add_barcode(barcode, actual_qty)
    else:
        print('Nothing to remove')


def check_row_exist(liststore, code):
    return any(map(lambda x: x[0] == code, liststore))


def modify_row(iter_path, liststore, command, row, qty, price, **kwargs):
    if command == ADD:
        row[4] += qty
        row[3] += price
        kwargs['window'].applied_barcodes.add_barcode(kwargs['barcode'], qty)
    elif command == RM:
        if (row[4] - qty <= 0) or (row[3] - price <= 0):
            _iter = liststore.get_iter(iter_path)
            liststore.remove(_iter)
        else:
            row[4] -= qty
            row[3] -= price
        kwargs['window'].applied_barcodes.remove_barcode(kwargs['barcode'], qty)


def process_barcode(window, barcode, btn_active):
    if btn_active:
        command = RM
    else:
        command = ADD

    # проверяем наличие баркода в кэше
    check_in_main_list_of_barcodes_and_modify(barcode, command, window)
    recalc_total(window)


def recalc_total(window):
    liststore = window.liststore
    total_value_widget = window.total_value
    total = 0
    for row in liststore:
        total += row[3]

    total = round_half_down(total, 4)
    total_value_widget.set_label(str(total))
