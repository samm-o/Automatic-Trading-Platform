import mysql.connector, config
from datetime import datetime
from ib_insync import *
import config
import smtplib, ssl
from  timezone import isDST
from utilities import calc_quantity, buy_order, take_profit_order, stop_order, trailing_stop_order

context = ssl.create_default_context()

connection = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
    ) # Replace with your MySQL database credentials

cursor = connection.cursor(dictionary=True)

cursor.execute("""
    select id from strategy where name = 'opening_range_breakout'
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

    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]
    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low
    
    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]
    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars['close'] > opening_range_high]
        
    if not after_opening_range_breakout.empty:
        if symbol not in existing_order_symbols:
            try:
                limit_price = after_opening_range_breakout.iloc[0]['close']
                quantity = calc_quantity(limit_price)
                
                messages.append(f"placing order for {symbol} at {limit_price}, closed above {opening_range_high}\n\n{after_opening_range_breakout.iloc[0]}\n\n")    
                print(f"placing order for {symbol} at {limit_price}, closed above {opening_range_high} at {after_opening_range_breakout.iloc[0]}")

                # Create a contract
                contract = Stock(symbol, 'SMART', 'USD')

                # Create a market buy order
                buy = buy_order(quantity)
                
                # Create a take profit order
                take_profit_price = limit_price + opening_range
                take_profit = take_profit_order(quantity, take_profit_price)
                
                # Create a stop loss order
                stop_loss_price = limit_price - opening_range
                stop_loss = stop_order(quantity, stop_loss_price)
                
                # Create a trailing stop order (Percentage)
                trailing_stop = trailing_stop_order(quantity, 0.6)
                
                ib.placeOrder(contract, buy)
                ib.placeOrder(contract, take_profit)
                ib.placeOrder(contract, stop_loss)
                
            except Exception as e:
                print(e)
                print(f"Could not place order for {symbol}")
        else:
            print(f"Already an order for {symbol}, skipping")
        
print(messages)

with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
    
    email_message = f"Subject: Trade Notificantions for {datetime.today().date()}\n\n"
    email_message += "\n".join(messages)
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message)
