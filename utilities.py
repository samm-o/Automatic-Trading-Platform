import math
from ib_insync import *

def calc_quantity(price):
    quantity = math.floor(1000 / price)
    
    return quantity

def buy_order(quantity):
    order = Order()
    order.action = 'BUY'
    order.totalQuantity = quantity
    order.orderType = 'MKT'
    return order

def take_profit_order(quantity, profit_price):
    order = Order()
    order.action = 'SELL'
    order.totalQuantity = quantity
    order.orderType = 'LMT'
    order.lmtPrice = profit_price
    return order

def stop_order(quantity, stop_price):
    order = Order()
    order.action = 'SELL'
    order.totalQuantity = quantity
    order.orderType = 'STP'
    order.auxPrice = stop_price
    return order

def trailing_stop_order(quantity, trail):
    order = Order()
    order.action = 'SELL'
    order.totalQuantity = quantity
    order.orderType = 'TRAIL'
    order.trailingPercent = trail
    return order