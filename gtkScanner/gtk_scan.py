import requests
from os import environ as envs

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Grid Example")
        self.entry = Gtk.Entry()
        self.entry.set_text("")
        self.entry.connect('activate', self.on_activate)

        self.add(self.entry)

    def on_activate(self, item):
        print('info ->  ', item.get_text())
        text = item.get_text()
        item.set_text('')
        request_to_wareinfo(text)


def launch():
    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


def request_to_wareinfo(barcode):
    timeouts = (6, 6)

    try:
        res = requests.get(envs['WAREINFO_API_URL'] + barcode, timeout=timeouts)
        print(res.json())
    except requests.RequestException as e:
        print('Request Exception: ' + str(e))

