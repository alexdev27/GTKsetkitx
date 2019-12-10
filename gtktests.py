import gi
import requests
from config import WAREINFO_API_URL

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# from pprint import pprint as pp

btn_text = {'add': 'К добавлению', 'rm': 'К удалению'}
prod_codes = {
    # '2227302': ['2227302', 'Каша овсяная 300г',  45, 1, 'кг\шт\etc']
}

# {'barcode': ['code', 'qty']}
barcode_and_code = {}

headers = ['Код товара', 'Название', 'Цена', 'Количество', 'Тип']

win_height = 350
win_width = 1000


class TreeViewFilterWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="experiments")
        self.set_border_width(10)
        self.set_default_size(win_width, win_height)

        scrolled_win = Gtk.ScrolledWindow(min_content_height=win_height)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        # self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self.liststore_left = Gtk.ListStore(str, str, float, float, str)
        self.liststore_right = Gtk.ListStore(str, str, float, float, str)

        # for i in prod_codes.values():
        #     tpl = list(i)
        #     tpl.append(5)
        #     self.liststore_left.append(tpl)
        #     self.liststore_right.append(tpl)

        self.tree_view_left = Gtk.TreeView(model=self.liststore_left)
        self.tree_view_right = Gtk.TreeView(model=self.liststore_right)

        for i, header in enumerate(headers):
            if header == 'Количество':
                renderer_spin = Gtk.CellRendererSpin(editable=True)
                renderer_spin.connect("edited", self.on_amount_edited, self.liststore_left)
                adjustment = Gtk.Adjustment(0, 0, 9999, 1, 10, 0)
                renderer_spin.set_property("adjustment", adjustment)
                self.tree_view_left.append_column(Gtk.TreeViewColumn(header, renderer_spin, text=i))
                renderer_spin = Gtk.CellRendererSpin(editable=True)
                renderer_spin.connect("edited", self.on_amount_edited, self.liststore_right)
                # adjustment = Gtk.Adjustment(0, 0, 9999, 1, 10, 0)
                renderer_spin.set_property("adjustment", adjustment)
                self.tree_view_right.append_column(Gtk.TreeViewColumn(header, renderer_spin, text=i))
                continue
            self.tree_view_left.append_column(Gtk.TreeViewColumn(header, Gtk.CellRendererText(), text=i))
            self.tree_view_right.append_column(Gtk.TreeViewColumn(header, Gtk.CellRendererText(), text=i))

        myform = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Поле ввода
        box = Gtk.Box()
        self.barcode_entry = Gtk.Entry(placeholder_text='Отсканируйте баркод товара в это поле')
        box.pack_start(self.barcode_entry, True, True, 0)
        myform.pack_start(box, True, True, 0)
        self.barcode_entry.connect('activate', self.on_barcode_submited)

        # Контрол
        box = Gtk.Box()
        self.switch_btn = Gtk.ToggleButton(label=btn_text['add'])
        self.switch_btn.connect('toggled', self.btn_is_toggled)
        box.pack_start(self.switch_btn, True, True, 0)

        myform.pack_start(box, True, True, 0)
        self.grid.attach(myform, 0, 0, 1, 1)

        # left list
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin_top=15)
        box.pack_start(self.tree_view_left, True, True, 0)
        box.pack_start(self.tree_view_right, True, True, 0)
        scrolled_win.add(box)
        self.grid.attach(scrolled_win, 0, 2, 1, 1)

    def btn_is_toggled(self, widget):
        print('toggled ', widget.get_active())
        if widget.get_active():
            widget.set_label(btn_text['rm'])
        else:
            widget.set_label(btn_text['add'])

    def on_barcode_submited(self, entry):
        barcode = entry.get_text().strip()
        entry.set_text('')


        if self.switch_btn.get_active():
            liststore = self.liststore_right
        else:
            liststore = self.liststore_left


        # проверяем наличие в штрихкодах
        if check_in_main_list_of_barcodes_and_modify(barcode, liststore):
            return

        # если дошли до сюда, то проверяем в кодах товара
        # так как это мог быть введён код товара
        if check_in_product_codes_list_and_modify(barcode, liststore):
            return

        info = request_to_wareinfo(barcode)

        if not info:
            return

        print(f'barcode_info: {info["code"]} - {info["measure"]} - {info["quantity"]}')

        process_success_request(info, barcode, liststore)

    def on_amount_edited(self, widget, path, value, liststore):
        p = prod_codes[liststore[path][0]]
        p_price = p[2]
        p_measure = p[4]
        val = float(value)
        if p_measure != 'кг':
            val = int(float(value))

        new_price = val * p_price

        liststore[path][3] = val
        liststore[path][2] = new_price


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


def check_in_main_list_of_barcodes_and_modify(barcode, liststore):
    if barcode in barcode_and_code.keys():
        if barcode_and_code[barcode][0] in prod_codes.keys():
            ratio = barcode_and_code[barcode][1]
            code = barcode_and_code[barcode][0]
            price = prod_codes[code][2]
            qty = prod_codes[code][3]
            for row in liststore:
                if row[0] == code:
                    row[3] += (ratio * qty)
                    row[2] += (price * ratio * qty)
                    return True
    return False


def check_in_product_codes_list_and_modify(barcode, liststore):
    if barcode in prod_codes.keys():
        for row in liststore:
            if row[0] == barcode:
                row[3] += prod_codes[barcode][3]
                row[2] += prod_codes[barcode][2]
                return True
        liststore.append(prod_codes[barcode])
        return True
    return False


def process_success_request(info, barcode, liststore):
    code = info['code']
    name = info['name']
    ratio = info['ratio']
    price = info['price']
    qty = info['quantity']
    measure = info['measure']
    actual_price = float(ratio * price * qty)
    actual_qty = float(ratio * qty)

    # если код есть в мапке кодов продукта
    if code in prod_codes.keys():
        for row in liststore:
            if row[0] == code:
                row[2] += actual_price
                row[3] += actual_qty
                return  # Done

    _list_to_cache = [code, name, price, qty, measure]
    _list_to_view = [code, name, actual_price, actual_qty, measure]

    prod_codes[code] = _list_to_cache
    liststore.append(_list_to_view)
    # сохраняю инфу о таком баркоде
    barcode_and_code[barcode] = [code, ratio]


win = TreeViewFilterWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()