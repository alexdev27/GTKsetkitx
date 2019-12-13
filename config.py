from os import environ as envs
from dotenv import load_dotenv, dotenv_values
load_dotenv()


WAREINFO_API_URL = envs['WAREINFO_API_URL']
# SHOP_NUMBER = envs['SHOP_NUMBER']
SOFTCHEQUE_URL = envs['SOFTCHEQUE_URL']

SOFTCHEQUE_PRINTER = 'TSC_TDP-225'

PRINT_COMMAND = 'lp -d'

print('env values', dotenv_values())
