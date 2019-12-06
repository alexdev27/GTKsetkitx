from dotenv import load_dotenv, dotenv_values
load_dotenv()


print('env values', dotenv_values())
