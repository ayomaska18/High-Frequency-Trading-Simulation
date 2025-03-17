from .setting import *
import time

def enforce_tick_size(price):
    price_int = int(price * PRICE_MULTIPLIER)
    rounded_price = round(price_int / TICK_MULTIPLIER) * TICK_MULTIPLIER
    return rounded_price

def convert_to_price(price_int):
    return price_int / PRICE_MULTIPLIER