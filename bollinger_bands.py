import mysql.connector, config
from datetime import datetime
from ib_insync import *
import config
from  timezone import isDST
import tulipy

connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toor",
    database="app2"
    )

cursor = connection.cursor(dictionary=True)

cursor.execute("""
    select id from strategy where name = 'bollinger_bands'
""")

strategy_id = cursor.fetchone()['id']

cursor.execute("""
    select symbol, name from stock
    join stock_strategy on stock_strategy.stock_id = stock.id
    where stock_strategy.strategy_id = %s
""", (strategy_id,))

stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks]
today = datetime.today().isoformat()

if isDST():
    start_minute_bar = f"{today} 9:30:00-05:00"
    end_minute_bar = f"{today} 15:07:00-05:00"
else:
    start_minute_bar = f"{today} 9:30:00-04:00"
    end_minute_bar = f"{today} 16:00:00-04:00"

util.startLoop()

# Connect to TWS API
ib = IB()
api = ib.connect(config.TWS_HOST, config.TWS_PORT, clientId=config.TWS_CLIENT_ID)

trades = ib.trades()
existing_order_symbols = [trade.contract.symbol for trade in trades]

messages = []

for symbol in symbols:

    # Request historical data
    contract = Stock(symbol, 'SMART', 'USD')
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='1 D',
        barSizeSetting='1 min',
        whatToShow='TRADES',
        useRTH=True,
        formatDate=1
    )

    # Convert historical data to pandas DataFrame
    df = util.df(bars)

    # Set the index to the timestamp column
    df.set_index('date', inplace=True)

    # Rename columns to match the existing code
    df.rename(columns={'low': 'low', 'high': 'high', 'close': 'close'}, inplace=True)

    minute_bars = df
    if len(minute_bars) >= 20:
        closes = minute_bars.close.values
        lower, middle, upper = tulipy.bbands(closes, period=20, stddev=2)
        
        current_candle = minute_bars.iloc[-1]   
        previous_candle = minute_bars.iloc[-2]
        
        if current_candle.close > lower[-1] and previous_candle.close < lower[-2]:
            print(f"{symbol} has closed above the lower band")
            print(current_candle)
            
            if symbol not in existing_order_symbols:
                try:
                    limit_price = current_candle.close
                    range = current_candle.high - current_candle.low
                    
                    print(f"placing order for {symbol} at {limit_price}")
                    
                    order = LimitOrder('BUY', 1, limit_price)
                    take_profit = LimitOrder('SELL', 1, limit_price + (range * 3))
                    stop_loss = StopOrder('SELL', 1, previous_candle.low)

                    trade = ib.placeOrder(contract, order)
                    take_profit_order = ib.placeOrder(contract, take_profit)
                    stop_loss_order = ib.placeOrder(contract, stop_loss)

                    # Assign order IDs to the take profit and stop loss orders
                    trade.transmit = False
                    take_profit_order.transmit = False
                    stop_loss_order.transmit = True

                    trade_id = trade.order.orderId
                    take_profit_order.parentId = trade_id
                    stop_loss_order.parentId = trade_id

                    ib.placeOrder(contract, take_profit_order)
                    ib.placeOrder(contract, stop_loss_order)

                    ib.transmitOrders()
                except Exception as e:
                    print(e)
                    print(f"Could not place order for {symbol}")
                else:
                    print(f"Already an order for {symbol}, skipping")