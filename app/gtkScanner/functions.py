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


def check_in_main_list_of_barcodes_and_modify(barcode, command, liststore):
    if barcode not in barcodes.keys():
        return False
    else:
        kwargs = {'barcode': barcode, 'command': command, 'liststore': liststore}
        return _add_or_remove(info=None, from_request=False, **kwargs)


def modify_liststore_row(prod_code, liststore, command, actual_qty, actual_price):
    for indx, row in enumerate(liststore):
        if row[0] == prod_code:
            return exec_command(indx, liststore, command, row, actual_qty, actual_price)
    return False


def process_success_request(info, barcode, command, liststore):
    kwargs = {'barcode': barcode, 'command': command, 'liststore': liststore}
    _add_or_remove(info, from_request=True, **kwargs)


def _add_or_remove(info, from_request, **kwargs):
    barcode = kwargs['barcode']
    liststore = kwargs['liststore']
    command = kwargs['command']
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
    if check_row_exist(liststore, code):
        return modify_liststore_row(code, liststore, command, actual_qty, actual_price)
    # если в листсторе записи не оказалось и это операция добавления, то добавляем
    # и возвращаем флаг модификации
    elif command == ADD:
        args = [code, name, actual_price, actual_qty, measure]
        liststore.append(args)
        return True

    print('Nothing to remove')

    return False


def check_row_exist(liststore, code):
    return any(map(lambda x: x[0] == code, liststore))


def exec_command(iter_path, liststore, command, row, qty, price):
    if command == ADD:
        row[3] += qty
        row[2] += price
    elif command == RM:
        if (row[3] - qty <= 0) or (row[2] - price <= 0):
            _iter = liststore.get_iter(iter_path)
            liststore.remove(_iter)
        else:
            row[3] -= qty
            row[2] -= price
    return True


def process_barcode(window, barcode, btn_active):
    if btn_active:
        command = RM
    else:
        command = ADD

    # проверяем наличие баркода в кэше
    if check_in_main_list_of_barcodes_and_modify(barcode, command, window.liststore):
        recalc_total(window)
        return

    # не нужно никаких запросов при удалении из списка
    if command == RM:
        return

    # если добрались сюда, то делаем запрос
    info = request_to_wareinfo(barcode)

    if not info:
        return

    print(f'barcode_info: {barcode} - {info["code"]} - {info["measure"]} - {info["quantity"]}')

    # обновляем листстор и кэш баркодов
    process_success_request(info, barcode, command, window.liststore)
    recalc_total(window)


def key_pressed(window, event):
    pass


def recalc_total(window):
    liststore = window.liststore
    total_value_widget = window.total_value
    total = 0
    for row in liststore:
        total += row[2]

    total = round_half_down(total, 4)
    total_value_widget.set_label(str(total))
