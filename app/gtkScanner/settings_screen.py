from os import environ as envs
import json
from app.helpers import make_error, show_gtk_error_modal
from config import SETTINGS_FILENAME

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


YES = 1
NO = 0


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

        # Поле физического принтера
        _box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        __box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.sys_printer_radio = Gtk.RadioButton.new_with_label(None, 'Печать с системного принтера')
        self.sys_printer_radio.connect('toggled', self.on_checked_radio, 'sys')
        self.sys_printer = Gtk.Entry(placeholder_text='Имя принтера в системе', margin_left=22)
        __box.pack_start(self.sys_printer_radio, False, False, 5)
        __box.pack_start(self.sys_printer, False, False, 0)
        _box.pack_start(__box, False, False, 0)
        content_box.pack_start(_box, False, False, 5)

        # Поле принтера по сокету
        _box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        __box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.socket_printer_radio = Gtk.RadioButton.new_with_label_from_widget(self.sys_printer_radio, 'Печать по протоколу socket в формате zpl')
        self.socket_printer_radio.connect('toggled', self.on_checked_radio, 'sock')
        self.socket_printer = Gtk.Entry(placeholder_text='Введите IP:PORT принтера в сети', margin_left=22)
        __box.pack_start(self.socket_printer_radio, False, False, 5)
        __box.pack_start(self.socket_printer, False, False, 0)
        _box.pack_start(__box, False, False, 0)
        content_box.pack_start(_box, False, False, 5)

        # Кнопка сохранения
        _box = Gtk.Box(margin_top=20)
        self.save_btn = Gtk.Button(label='Сохранить')
        self.save_btn.connect('clicked', self.on_save_clicked)
        _box.pack_start(self.save_btn, False, False, 0)
        content_box.pack_start(_box, False, False, 0)

        content_area.pack_start(content_box, False, False, 0)

    def on_checked_radio(self, widget, param):
        print(widget.get_label(), widget.get_active(), param)
        if param == 'sys' and widget.get_active():
            self.toggle_printer(self.sys_printer, True)
            self.toggle_printer(self.socket_printer, False)
        elif param == 'sock' and widget.get_active():
            self.toggle_printer(self.sys_printer, False)
            self.toggle_printer(self.socket_printer, True)

    def toggle_printer(self, entry_field, active):
        opacity = 1.0 if active else 0.5
        entry_field.set_property('opacity', opacity)
        entry_field.set_property('can-focus', active)
        entry_field.set_property('editable', active)

    def show_settings(self):
        self.show_all()
        self._fill_interface()
        result = self.run()

        if result == Gtk.ResponseType.CLOSE:
            print('Close the dialog!')
            pass

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
            else:
                sock_print = str(self.socket_printer.get_text()).strip()
                addr = sock_print.split(':', maxsplit=1)
                ip = addr[0]
                port = None
                try:
                    port = addr[1]
                except IndexError as exc:
                    errors.append(
                        'В поле ввода "Печать по протоколу socket в формате zpl"'
                        ' PORT должен присутствовать')

                if (not ip) or (not port):
                    errors.append(
                        'Поле ввода "Печать по протоколу socket в формате zpl"'
                        ' должно содержать информацию в виде IP:PORT')
                if port:
                    try:
                        int(port)
                    except ValueError as exc:
                        errors.append('В поле ввода "Печать по протоколу socket в формате zpl" '
                                      'PORT должен быть числом')

        if errors:
            err_str = '\n'.join(errors)
            return make_error(err_str)
        else:
            return {}

    def _prepare_to_save(self):
        settings = {
            'WAREINFO_API_URL': '',
            'SOFTCHEQUE_URL': '',
            'SYS_ENABLE': '',
            'SYS_PRINTER_NAME': '',
            'SOCK_ENABLE': '',
            'SOCK_PRINTER_IP': '',
            'SOCK_PRINTER_PORT': ''
        }

        ip = envs['SOCK_PRINTER_IP']
        port = envs['SOCK_PRINTER_PORT']

        if self.socket_printer_radio.get_active():
            settings['SOCK_ENABLE'] = YES
            settings['SYS_ENABLE'] = NO
            addr = str(self.socket_printer.get_text()).split(':', maxsplit=1)
            ip = addr[0]
            port = addr[1]

        elif self.sys_printer_radio.get_active():
            settings['SYS_ENABLE'] = YES
            settings['SOCK_ENABLE'] = NO

        settings['SYS_PRINTER_NAME'] = self.sys_printer.get_text()
        settings['SOCK_PRINTER_IP'] = ip
        settings['SOCK_PRINTER_PORT'] = port
        settings['WAREINFO_API_URL'] = self.wareinfo_api.get_text()
        settings['SOFTCHEQUE_URL'] = self.soft_cheque_api.get_text()

        from pprint import pprint as pp
        pp(settings)

        return settings

    def _push_to_env_variables(self, _dict):
        for k, v in _dict.items():
            if type(v) == int:
                v = str(v)
            envs[k] = v

    def _save_to_json_file(self, _dict):
        with open(SETTINGS_FILENAME, 'w') as fp:
            json.dump(_dict, fp)

    def _fill_interface(self):
        self.sys_printer.set_text(envs['SYS_PRINTER_NAME'])
        self.socket_printer.set_text(str(envs['SOCK_PRINTER_IP'] + ':' + envs['SOCK_PRINTER_PORT']))
        self.soft_cheque_api.set_text(envs['SOFTCHEQUE_URL'])
        self.wareinfo_api.set_text(envs['WAREINFO_API_URL'])

        if bool(int(envs['SOCK_ENABLE'])):
            self.socket_printer_radio.toggled()
        elif bool(int(envs['SYS_ENABLE'])):
            self.sys_printer_radio.toggled()
        # self.socket_printer_radio.set_active(bool(int(envs['SOCK_ENABLE'])))
        # self.sys_printer_radio.set_active(bool(int(envs['SYS_ENABLE'])))

    def on_save_clicked(self, widget):
        info = self._validate_incoming_settings()

        if info.get('error'):
            show_gtk_error_modal(self, info['message'])
            return

        settings = self._prepare_to_save()

        try:
            self._save_to_json_file(settings)
        except Exception as exc:
            msg = 'Возникло исключение при сохранении файла настроек: \n'
            msg += str(exc)
            show_gtk_error_modal(self, msg)
            return
        self._push_to_env_variables(settings)
        self.response(Gtk.ResponseType.CLOSE)

