import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from .functions import process_barcode


btn_text = {'add': 'К добавлению', 'rm': 'К удалению'}
headers = ['Код товара', 'Название', 'Цена', 'Количество', 'Тип']

win_height = 600
win_width = 1200


class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="experiments")

        self.accumulated_characters = []
        self.connect("key-press-event", self.on_key_pressed)

        self.set_border_width(10)
        self.set_default_size(win_width, win_height)

        scrolled_win = Gtk.ScrolledWindow(min_content_height=win_height)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        # self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self.liststore = Gtk.ListStore(str, str, float, float, str)

        self.tree_view = Gtk.TreeView(model=self.liststore)
        self.tree_view.set_property('can-focus', False)

        for i, header in enumerate(headers):
            if header == 'Количество':
                renderer_spin = Gtk.CellRendererSpin(editable=True)
                self.tree_view.append_column(Gtk.TreeViewColumn(header, renderer_spin, text=i))
                continue
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

    def on_key_pressed(self, widget, event):
        keyval = Gdk.keyval_name(event.keyval)
        if keyval != 'Return':
            self.accumulated_characters.append(keyval)
            return

        barcode = ''.join(self.accumulated_characters)
        self.accumulated_characters = []
        process_barcode(self.liststore, barcode, self.switch_btn.get_active())


def launch():
    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
