import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from app.helpers import make_error, show_gtk_error_modal


class SettingsScreen(Gtk.Dialog):
    def __init__(self, parent_window):
        Gtk.Dialog.__init__(self, title='Настройки', parent=parent_window)
        self.set_modal(True)
        self.set_size_request(600, 300)
        # self.add_button('Сохранить', Gtk.ResponseType.APPLY)
        # self.add_button('Отменить и Закрыть', Gtk.ResponseType.CANCEL)

        content_area = self.get_content_area()

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=10)

        # поле апи информации о товаре
        _box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label('Адрес API информации о товаре', xalign=Gtk.Justification.LEFT, margin_bottom=5)
        self.wareinfo_api = Gtk.Entry()
        _box.pack_start(label, False, False, 0)
        _box.pack_start(self.wareinfo_api, False, False, 0)
        content_box.pack_start(_box, False, False, 10)

        # поле мягкого чека
        _box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label('Адрес API генерации мягкого чека', xalign=Gtk.Justification.LEFT, margin_bottom=5)
        self.soft_cheque_api = Gtk.Entry()
        _box.pack_start(label, False, False, 0)
        _box.pack_start(self.soft_cheque_api, False, False, 0)
        content_box.pack_start(_box, False, False, 0)

        _box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        __box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.sys_printer_radio = Gtk.RadioButton.new_with_label(None, 'Печать с системного принтера')
        self.sys_printer = Gtk.Entry(placeholder_text='Имя принтера в системе (пробелы заменятся на _ )', margin_left=22)
        __box.pack_start(self.sys_printer_radio, False, False, 5)
        __box.pack_start(self.sys_printer, False, False, 0)
        _box.pack_start(__box, False, False, 0)
        content_box.pack_start(_box, False, False, 5)

        _box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        __box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.socket_printer_radio = Gtk.RadioButton.new_with_label_from_widget(self.sys_printer_radio, 'Печать по протоколу socket в формате zpl')
        self.socket_printer = Gtk.Entry(placeholder_text='Введите IP:PORT принтера в сети', margin_left=22)
        __box.pack_start(self.socket_printer_radio, False, False, 5)
        __box.pack_start(self.socket_printer, False, False, 0)
        _box.pack_start(__box, False, False, 0)
        content_box.pack_start(_box, False, False, 5)


        _box = Gtk.Box(margin_top=20)
        self.save_btn = Gtk.Button(label='Сохранить')
        self.save_btn.connect('clicked', self.on_save_clicked)
        _box.pack_start(self.save_btn, False, False, 0)
        content_box.pack_start(_box, False, False, 0)

        content_area.pack_start(content_box, False, False, 0)

    def show_settings(self):
        self.show_all()

        result = self.run()

        if result == Gtk.ResponseType.APPLY:

            pass
        # elif result == Gtk.ResponseType.CANCEL:
        #     pass

        print('Result -> ', result)
        self.destroy()

    def _validate_incoming_settings(self):
        wareinfo_api = str(self.wareinfo_api.get_text()).strip()
        soft_cheque_api = str(self.soft_cheque_api.get_text()).strip()

        errors = []
        if not wareinfo_api:
            errors.append('Поле "Адрес API информации о товаре" не должно быть пустым')
        if not soft_cheque_api:
            errors.append('Поле "Адрес API генерации мягкого чека" не должно быть пустым')

        sys_radio = self.sys_printer_radio.get_active()
        sock_radio = self.socket_printer_radio.get_active()

        if not (sys_radio or sock_radio):
            errors.append('Только одно из полей выбора способа печати должно быть выбрано')

        if sys_radio:
            sys_print = str(self.sys_printer.get_text()).strip()
            if not sys_print:
                errors.append('Поле ввода "Печать с системного принтера" не должно быть пустым')

        if sock_radio:
            sock_print = str(self.socket_printer.get_text()).strip()
            if not sock_print:
                errors.append('Поле ввода "Печать по протоколу socket в формате zpl" не должно быть пустым')


        # print(self.sys_printer_radio.get_active(), self.socket_printer_radio.get_active())

        if errors:
            err_str = '\n'.join(errors)
            return make_error(err_str)
        else:
            return {}

    def _save_to_json_file(self):
        pass

    def on_save_clicked(self, widget):
        info = self._validate_incoming_settings()
        if info.get('error'):
            show_gtk_error_modal(self, info['message'])
            return
