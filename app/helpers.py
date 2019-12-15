import math
from functools import wraps
import requests

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier


def round_half_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n*multiplier - 0.5) / multiplier


def handle_request():
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except requests.RequestException as exc:
                print('Request Exception: ' + str(exc))
                return
        return decorator
    return wrapper


def show_gtk_error_modal(parent_window, message):
    dialog = Gtk.MessageDialog(
        parent_window, 0, Gtk.MessageType.ERROR,
        Gtk.ButtonsType.OK, "Возникла ошибка!"
    )
    dialog.format_secondary_text(message)
    dialog.run()

    dialog.destroy()

def show_popover_spinner():
    pass


def make_error(msg):
    return {'error': True, 'message': msg}
