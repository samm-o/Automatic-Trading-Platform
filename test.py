from ib_insync import *
import config
util.logToConsole('DEBUG')
ib = IB()
ib.connect(config.TWS_HOST, config.TWS_PORT, clientId=config.TWS_CLIENT_ID)