import sqlite3, config
from ib_insync import *
from datetime import datetime
import tulipy, numpy

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id, symbol, name FROM stock
""")

rows = cursor.fetchall()
symbols = []
stock_dict = {}

for row in rows:
    symbol = row['symbol']
    symbols.append(symbol) 
    stock_dict[symbol] = row['id']

# Connect to TWS
ib = IB()
ib.connect(config.TWS_HOST, config.TWS_PORT, clientId=config.TWS_CLIENT_ID) # replace with your connection details

# Get the current date
current_date = datetime.today()
# symbols = symbols[symbols.index(''):]  # Start from 'XLE' symbol

for symbol in symbols:
    contract = Stock(symbol, 'SMART', 'USD')  # replace 'SMART' with the actual exchange if necessary

    cursor.execute("""
        SELECT * FROM stock_price
        WHERE stock_id = ?
    """, (stock_dict[symbol],))

    existing_prices = cursor.fetchall()
   
    if not existing_prices:
        print(f"processing symbol {symbol}")
        bars = ib.reqHistoricalData(
            contract,
            endDateTime=current_date.strftime('%Y%m%d %H:%M:%S'),
            durationStr='1 Y',
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )
        recent_closes = [bar.close for bar in bars]
        for bar in bars:
            stock_id = int(stock_dict[symbol])

            if len(recent_closes) >= 50 and (current_date.date().isoformat() == bar.date.isoformat()):
                sma_20 = tulipy.sma(numpy.array(recent_closes), period=20) [-1]
                sma_50 = tulipy.sma(numpy.array(recent_closes), period=50) [-1]
                rsi_14 = tulipy.rsi(numpy.array(recent_closes), period=14) [-1]
            else:
                sma_20 = None
                sma_50 = None
                rsi_14 = None
                
            cursor.execute("""
                INSERT INTO stock_price (stock_id, datetime, open, high, low, close, volume, sma_20, sma_50, rsi_14) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (stock_id, bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume, sma_20, sma_50, rsi_14))
            connection.commit()

    # Check if there is a price associated with the current day for the stock
    cursor.execute("""
        SELECT datetime FROM stock_price
        WHERE stock_id = ? AND datetime = ?
    """, (stock_dict[symbol], current_date.date()))

    existing_price = cursor.fetchone()

    if existing_price is None:
        print(f"processing symbol {symbol}")
        bars = ib.reqHistoricalData(
            contract,
            endDateTime=current_date.strftime('%Y%m%d %H:%M:%S'),
            durationStr='51 D',
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )
        recent_closes = [bar.close for bar in bars]
        for bar in bars:
            stock_id = int(stock_dict[symbol])
            latest_bar = bars[-1]
            if len(recent_closes) >= 50 and (current_date.date().isoformat() == latest_bar.date.isoformat()):
                sma_20 = tulipy.sma(numpy.array(recent_closes), period=20)[-1]
                sma_50 = tulipy.sma(numpy.array(recent_closes), period=50)[-1]
                rsi_14 = tulipy.rsi(numpy.array(recent_closes), period=14)[-1]
            else:
                sma_20 = None
                sma_50 = None
                rsi_14 = None
            
            
            cursor.execute("""
                INSERT INTO stock_price (stock_id, datetime, open, high, low, close, volume, sma_20, sma_50, rsi_14) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (stock_id, latest_bar.date, latest_bar.open, latest_bar.high, latest_bar.low, latest_bar.close, latest_bar.volume, sma_20, sma_50, rsi_14))
            
            connection.commit()

ib.disconnect()