import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from time import sleep

from .functions import process_barcode
from .constants import ALLOWED_KEYS
from .models import AppliedBarcodes

from app.setkitX.functions import send_to_setkitx

from pprint import pprint as pp

btn_text = {'add': 'Добавление', 'rm': 'Удаление'}
headers = ['Штрихкод товара', 'Код товара', 'Название', 'Цена', 'Количество', 'Тип']

win_height = 600
win_width = 1200


class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="experiments")

        self.accumulated_characters = []
        self.connect("key-press-event", self.on_key_pressed)

        self.applied_barcodes = AppliedBarcodes()

        self.set_border_width(10)
        self.set_default_size(win_width, win_height)

        scrolled_win = Gtk.ScrolledWindow(min_content_height=win_height)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        # self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self.liststore = Gtk.ListStore(str, str, str, float, float, str)

        self.tree_view = Gtk.TreeView(model=self.liststore)
        self.tree_view.set_property('can-focus', False)

        self.popover = Gtk.Popover.new(self.tree_view)
        self.popover.set_modal(True)
        self.popover.set_position(Gtk.PositionType.BOTTOM)
        self.spinner = Gtk.Spinner()
        self.popover.add(self.spinner)



        for i, header in enumerate(headers):
            # if header == 'Количество':
            #     renderer_spin = Gtk.CellRendererSpin()
            #     # renderer_spin.connect('edited', )
            #     self.tree_view.append_column(Gtk.TreeViewColumn(header, renderer_spin, text=i))
            #     continue
            self.tree_view.append_column(Gtk.TreeViewColumn(header, Gtk.CellRendererText(), text=i))

        myform = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)


        # Контрол
        box = Gtk.Box()
        self.switch_btn = Gtk.ToggleButton(label=btn_text['add'])
        self.switch_btn.set_property('can-focus', False)
        self.switch_btn.connect('toggled', self.btn_is_toggled)
        box.pack_start(self.switch_btn, True, True, 0)

        myform.pack_start(box, True, True, 0)
        self.grid.attach(myform, 0, 0, 1, 1)

        self.total_label = Gtk.Label('Всего: ', xalign=Gtk.Justification.LEFT)
        self.total_value = Gtk.Label('0', xalign=Gtk.Justification.LEFT)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=15)
        box.pack_start(self.tree_view, True, True, 0)
        scrolled_win.add(box)
        self.grid.attach(scrolled_win, 0, 2, 1, 1)

        self.print_btn = Gtk.Button(label='Распечатать')
        self.print_btn.set_property('can-focus', False)
        self.print_btn.connect('clicked', self.on_print_btn_clicked)

        #  нижняя панель
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin_top=15, margin_bottom=5)
        box.pack_start(self.total_label, False, False, 0)
        box.pack_start(self.total_value, False, False, 0)
        box.pack_end(self.print_btn, False, False, 0)
        self.grid.attach(box, 0, 3, 1, 1)

    def btn_is_toggled(self, widget):
        print('button active? ' + str(self.switch_btn.get_active()))

        if widget.get_active():
            widget.set_label(btn_text['rm'])
        else:
            widget.set_label(btn_text['add'])

    def on_key_pressed(self, widget, event):
        key_code = event.keyval
        key_value = ALLOWED_KEYS.get(key_code)
        keyval = Gdk.keyval_name(event.keyval)

        if keyval != 'Return' and key_value:
            self.accumulated_characters.append(keyval)
            return

        barcode = ''.join(self.accumulated_characters)
        self.accumulated_characters = []
        if not barcode:
            return
        self.show_spinner()
        process_barcode(self, barcode, self.switch_btn.get_active())
        self.hide_spinner()

    def show_spinner(self):
        self.popover.popup()
        self.spinner.show()
        self.spinner.start()

    def hide_spinner(self):
        self.popover.popdown()
        self.spinner.stop()

    def on_print_btn_clicked(self, widget):

        return
        pp('Applied barcodes !')
        data = self.applied_barcodes.get_ready_for_setkitx()
        send_to_setkitx(data)
        # pass


def launch():
    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
