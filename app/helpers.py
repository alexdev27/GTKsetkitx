import math
from functools import wraps
import requests


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


# def handle_request():
