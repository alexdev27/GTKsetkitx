import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from .functions import process_success_request, check_in_main_list_of_barcodes_and_modify, \
    request_to_wareinfo, on_amount_changed


btn_text = {'add': 'К добавлению', 'rm': 'К удалению'}

# prod_codes = {}
# barcode_and_code = {}


headers = ['Код товара', 'Название', 'Цена', 'Количество', 'Тип']

win_height = 750
win_width = 1300


class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="experiments")

        self.barcodes_and_codes = {}
        self.prod_codes = {}


        self.accumulate_characters = []
        self.connect("key-press-event", self.on_key_pressed)


        self.set_border_width(10)
        self.set_default_size(win_width, win_height)


        scrolled_win = Gtk.ScrolledWindow(min_content_height=win_height)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        # self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self.liststore = Gtk.ListStore(str, str, float, float, str)
        # self.liststore_right = Gtk.ListStore(str, str, float, float, str)

        # for i in prod_codes.values():
        #     tpl = list(i)
        #     tpl.append(5)
        #     self.liststore_left.append(tpl)
        #     self.liststore_right.append(tpl)

        self.tree_view = Gtk.TreeView(model=self.liststore)
        self.tree_view.set_property('can-focus', False)
        # self.tree_view_right = Gtk.TreeView(model=self.liststore_right)

        for i, header in enumerate(headers):
            if header == 'Количество':
                renderer_spin = Gtk.CellRendererSpin(editable=True)
                renderer_spin.connect("edited", self.on_amount_edited, self)
                adjustment = Gtk.Adjustment(0, 0, 9999, 1, 10, 0)
                renderer_spin.set_property("adjustment", adjustment)
                self.tree_view.append_column(Gtk.TreeViewColumn(header, renderer_spin, text=i))
                continue
            self.tree_view.append_column(Gtk.TreeViewColumn(header, Gtk.CellRendererText(), text=i))

        myform = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Поле ввода
        # box = Gtk.Box()
        # self.barcode_entry = Gtk.Entry(placeholder_text='Отсканируйте баркод товара в это поле')
        # box.pack_start(self.barcode_entry, True, True, 0)
        # myform.pack_start(box, True, True, 0)
        # self.barcode_entry.connect('activate', self.on_barcode_submited)

        # Контрол
        box = Gtk.Box()
        self.switch_btn = Gtk.ToggleButton(label=btn_text['add'])
        self.switch_btn.set_property('can-focus', False)
        self.switch_btn.connect('toggled', self.btn_is_toggled)
        box.pack_start(self.switch_btn, True, True, 0)

        myform.pack_start(box, True, True, 0)
        self.grid.attach(myform, 0, 0, 1, 1)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin_top=15)
        box.pack_start(self.tree_view, True, True, 0)
        scrolled_win.add(box)
        self.grid.attach(scrolled_win, 0, 2, 1, 1)

    def btn_is_toggled(self, widget):
        print('button active? ' + str(self.switch_btn.get_active()))

        if widget.get_active():
            widget.set_label(btn_text['rm'])
        else:
            widget.set_label(btn_text['add'])

    def on_barcode_submited(self, entry):
        barcode = entry.get_text().strip()
        entry.set_text('')

        if self.switch_btn.get_active():
            command = 'REMOVE'
        else:
            command = 'ADD'

        # проверяем наличие в штрихкодах
        print('Current Command: ' + command)
        if check_in_main_list_of_barcodes_and_modify(barcode, command, self):
            return

        if command == 'REMOVE':
            return

        # если добрались сюда, то делаем запрос
        info = request_to_wareinfo(barcode)

        if not info:
            return

        print(f'barcode_info: {barcode} - {info["code"]} - {info["measure"]} - {info["quantity"]}')

        # обновляем листстор и мапку баркодов
        process_success_request(info, barcode, command, self)

    def on_amount_edited(self, widget, path, value, window):
        on_amount_changed(path, value, window)


    def on_key_pressed(self, widget, event):
        # print('event ' + str(dir(event)))
        print('event type ' + str(event.get_event_type()))
        print('key code ' + str(event.get_keycode()))
        print('key value ' + str(event.get_keyval()))
        print('readable key value ' + str(Gdk.keyval_name(event.keyval)))
        keyval = Gdk.keyval_name(event.keyval)
        if keyval != 'Return':
            self.accumulate_characters.append(keyval)
            return

        barcode = ''.join(self.accumulate_characters)
        self.accumulate_characters = []
        exec_code(self, barcode)


def exec_code(window, barcode):

    if window.switch_btn.get_active():
        command = 'REMOVE'
    else:
        command = 'ADD'

    # проверяем наличие в штрихкодах
    print('Current Command: ' + command)
    if check_in_main_list_of_barcodes_and_modify(barcode, command, window):
        return

    if command == 'REMOVE':
        return

    # если добрались сюда, то делаем запрос
    info = request_to_wareinfo(barcode)

    if not info:
        return

    print(f'barcode_info: {barcode} - {info["code"]} - {info["measure"]} - {info["quantity"]}')

    # обновляем листстор и мапку баркодов
    process_success_request(info, barcode, command, window)

def launch():
    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
