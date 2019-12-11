import requests
from config import WAREINFO_API_URL
from .models import prod_codes, barcode_and_code



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
    # barcodes_and_codes = window.barcodes_and_codes
    # prod_codes = window.prod_codes
    liststore = window.liststore
    if barcode in barcode_and_code.keys():
        if barcode_and_code[barcode][0] in prod_codes.keys():
            ratio = barcode_and_code[barcode][1]
            code = barcode_and_code[barcode][0]
            qty = barcode_and_code[barcode][2]
            price = prod_codes[code][2]

            actual_qty = ratio * qty
            actual_price = ratio * qty * price

            print(f'add right price and quantity:  {actual_qty} - {actual_price}')

            if check_row_exist(liststore, code):
                return modify_liststore_row(code, liststore, command, actual_qty, actual_price)
            else:
                if command == 'REMOVE':
                    return True
                print(' ---> Append without request')
                name = prod_codes[code][1]
                measure = prod_codes[code][3]
                print(prod_codes[code])
                args = [code, name, actual_price, actual_qty, measure]
                print(args)
                append_to_liststore(liststore, *args)
                return True

            # return modify_liststore_row(code, liststore, command, actual_qty, actual_price)
    return False


# def check_in_product_codes_list_and_modify(barcode, liststore):
#     if barcode in prod_codes.keys():
#         for row in liststore:
#             if row[0] == barcode:
#                 row[3] += prod_codes[barcode][3]
#                 row[2] += prod_codes[barcode][2]
#                 return True
#         liststore.append(prod_codes[barcode])
#         return True
#     return False


def modify_liststore_row(prod_code, liststore, command, actual_qty, actual_price):
    for indx, row in enumerate(liststore):
        if row[0] == prod_code:
            exec_command(indx, liststore, command, row, actual_qty, actual_price)
            return True
    return False


def process_success_request(info, barcode, command, window):
    # barcode_and_code = window.barcodes_and_codes
    # prod_codes = window.prod_codes
    liststore = window.liststore
    code = info['code']
    name = info['name']
    ratio = info['ratio']
    price = info['price']
    qty = info['quantity']
    measure = info['measure']
    actual_price = float(ratio * price * qty)
    actual_qty = float(ratio * qty)

    _list_to_cache = [code, name, price, measure]
    _list_to_view = [code, name, actual_price, actual_qty, measure]

    # если код есть в мапке кодов продукта
    if code in prod_codes.keys() and check_row_exist(liststore, code):
        print(' --> modify row')
        modify_liststore_row(code, liststore, command, actual_qty, actual_price)
    else:
        print(' --> Append list_to_view')
        append_to_liststore(liststore, *_list_to_view)

    prod_codes[code] = _list_to_cache
    # сохраняю инфу о таком баркоде
    barcode_and_code[barcode] = [code, ratio, qty]


def check_row_exist(liststore, code):
    return any(map(lambda x: x[0] == code, liststore))


def append_to_liststore(liststore, *args):
    liststore.append([*args])


def exec_command(iter_path, liststore, command, row, qty, price):
    if command == 'ADD':
        row[3] += qty
        row[2] += price
    elif command == 'REMOVE':
        if (row[3] - qty <= 0) or (row[2] - price <= 0):
            print('its less than Zero! Delete Row! Now!')
            _iter = liststore.get_iter(iter_path)
            liststore.remove(_iter)
        else:
            row[3] -= qty
            row[2] -= price


def on_amount_changed(path, value, window):
    liststore = window.liststore
    prod_codes = window.prod_codes
    p = prod_codes[liststore[path][0]]
    p_price = p[2]
    p_measure = p[4]
    val = float(value)
    if p_measure != 'кг':
        val = int(float(value))

    new_price = val * p_price

    liststore[path][3] = val
    liststore[path][2] = new_price
