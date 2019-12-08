import gi
import requests

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


btn_text = {'add': 'К добавлению', 'rm': 'К удалению'}
barcodes = {
    '2227302': ['2227302', 'Каша овсяная 300г',  45, 1]
}

headers = ['Баркод', 'Название', 'Цена', 'Количество']

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

        self.liststore_left = Gtk.ListStore(str, str, float, int)
        self.liststore_right = Gtk.ListStore(str, str, float, int)

        # for i in barcodes.values():
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
                break
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
        # liststore = []

        if self.switch_btn.get_active():
            liststore = self.liststore_right
        else:
            liststore = self.liststore_left

        if barcode in barcodes.keys():

            for row in liststore:
                if row[0] == barcode:
                    print('matched ', row[0], barcode)
                    row[3] += barcodes[barcode][3]
                    return
            liststore.append(barcodes[barcode])
            return


        info = request_to_wareinfo(barcode)
        print('Heres ', info)

        if info:
            _list = [info['code'], info['name'], info['price'], info['quantity']]
            barcodes[info['code']] = _list
            liststore.append(_list)

    def on_amount_edited(self, widget, path, value, liststore):
        liststore[path][3] = int(value)


    def on_liststore_row_changed(self, *args, **kwargs):
        pass

def get_submited_barcode_info(barcode):
    # запрос по сети - ответ
    info = barcodes.get(str(barcode))

    return info

from config import WAREINFO_API_URL

def request_to_wareinfo(barcode):
    timeouts = 2

    try:
        res = requests.get(WAREINFO_API_URL + barcode, timeout=timeouts)
        if res.status_code >= 400:
            print('Ошибка запроса. Код ошибки: ', res.status_code)
            return None
        return res.json()
    except requests.RequestException as e:
        print(f'Request Exception: {e}')
        return None


win = TreeViewFilterWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()