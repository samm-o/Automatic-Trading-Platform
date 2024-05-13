import config
from ib_insync import *

ib = IB()
ib.connect(config.TWS_HOST, config.TWS_PORT, clientId=config.TWS_CLIENT_ID)

openOrders = ib.reqPositions()

for order in openOrders:
    ib.placeOrder(order.contract, MarketOrder('SELL', abs(order.position)))
