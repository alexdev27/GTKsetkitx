from os import environ as envs
from dotenv import load_dotenv, dotenv_values
load_dotenv()


WAREINFO_API_URL = envs['WAREINFO_API_URL']

print('env values', dotenv_values())
