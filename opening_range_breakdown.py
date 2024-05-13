import sqlite3, config
from datetime import datetime
from ib_insync import *
import config
import smtplib, ssl
from  timezone import isDST
import mysql.connector

context = ssl.create_default_context()

connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toor",
    database="app2"
    )

cursor = connection.cursor(dictionary=True)

cursor.execute("""
    select id from strategy where name = 'opening_range_breakdown'
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
    end_minute_bar = f"{today} 9:45:00-05:00"
else:
    start_minute_bar = f"{today} 9:30:00-04:00"
    end_minute_bar = f"{today} 9:45:00-04:00"



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

    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]
    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low
    
    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]
    after_opening_range_breakdown = after_opening_range_bars[after_opening_range_bars['close'] < opening_range_low]
        
    if not after_opening_range_breakdown.empty:
        if symbol not in existing_order_symbols:
            limit_price = after_opening_range_breakdown.iloc[0]['close']
            
            message = (f"selling short {symbol} at {limit_price}, closed below {opening_range_high}\n\n{after_opening_range_breakdown.iloc[0]}\n\n")    
            messages.append(message)
            
            print(message)
            
            try:
                order = LimitOrder('BUY', 1, limit_price)
                take_profit = LimitOrder('SELL', 1, limit_price - opening_range)
                stop_loss = StopOrder('SELL', 1, limit_price + opening_range)
                
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
                print(f"Error placing order for {symbol}")
        else:
            print(f"Already an order for {symbol}, skipping")

with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
    
    email_message = f"Subject: Trade Notificantions for {datetime.today().date()}\n\n"
    email_message += "\n".join(messages)
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message)