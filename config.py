from os import environ as envs
import json
# from dotenv import load_dotenv, dotenv_values
# load_dotenv()

SETTINGS_FILENAME = 'settings.json'


# загоняем настройки в систему, если они вообще есть
with open(SETTINGS_FILENAME, mode='r') as _file:
    _vars = json.load(_file)
    for k, v in _vars.items():
        if type(v) == int:
            v = str(v)
        envs[k] = v


# WAREINFO_API_URL = envs['WAREINFO_API_URL']
# SHOP_NUMBER = envs['SHOP_NUMBER']
# SOFTCHEQUE_URL = envs['SOFTCHEQUE_URL']

# SOFTCHEQUE_PRINTER = 'TSC_TDP-225'

PRINT_COMMAND = 'lp -d'

# print('env values', dotenv_values())
