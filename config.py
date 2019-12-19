from os import path


SETTINGS_FILENAME = 'gtk_scan_settings.json'
SETTINGS_FILE = path.normpath(path.expanduser('~/' + SETTINGS_FILENAME))

PRINT_COMMAND = 'lp -d'
