import sqlite3, config
from ib_insync import *
from datetime import datetime
import tulipy, numpy
from multiprocessing import Pool
import os
import threading
import mysql.connector

lock = threading.Lock()

def split_list(lst, n):
    """Split a list into n chunks"""
    k, m = divmod(len(lst), n)
    return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

def process_symbol(symbol_chunk):
    
    connection = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
    ) # Replace with your MySQL database credentials

    cursor = connection.cursor(dictionary=True, buffered=True)
    ib = IB()
    ib.connect(config.TWS_HOST, config.TWS_PORT, clientId=config.TWS_CLIENT_ID + os.getpid())

    for symbol in symbol_chunk:
        cursor.execute("""
            SELECT id FROM stock WHERE symbol = %s
        """, (symbol,))

        row = cursor.fetchone()
        stock_id = row['id']

        # Get the current date
        current_date = datetime.today()

        contract = Stock(symbol, 'SMART', 'USD')  # replace 'SMART' with the actual exchange if necessary

        cursor.execute("""
            SELECT * FROM stock_price
            WHERE stock_id = %s
        """, (stock_id,))

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
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (stock_id, bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume, sma_20, sma_50, rsi_14))
                
                connection.commit()
                

        # Check if there is a price associated with the current day for the stock
        cursor.execute("""
            SELECT datetime FROM stock_price
            WHERE stock_id = %s AND datetime = %s
        """, (stock_id, current_date.date()))

        existing_price = cursor.fetchone()

        if existing_price is None and existing_prices is not None:
            print(f"processing symbol {symbol}")
            try:
                bars = ib.reqHistoricalData(
                    contract,
                    endDateTime=current_date.strftime('%Y%m%d %H:%M:%S'),
                    durationStr='51 D',
                    barSizeSetting='1 day',
                    whatToShow='TRADES',
                    useRTH=True,
                    formatDate=1
                )
            except Exception as e:
                print(e)    
            recent_closes = [bar.close for bar in bars]
            if bars:
                latest_bar = bars[-1]
                for bar in bars:
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
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (stock_id, latest_bar.date, latest_bar.open, latest_bar.high, latest_bar.low, latest_bar.close, latest_bar.volume, sma_20, sma_50, rsi_14))
                
                connection.commit()
            else:
                print(f"No bars data for symbol: {symbol}")

if __name__ == '__main__':
    connection = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
    ) # Replace with your MySQL database credentials

    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT symbol FROM stock
    """)

    symbols = [row['symbol'] for row in cursor.fetchall()]
    symbols = symbols[symbols.index('ZZZ'):]
    symbol_chunks = list(split_list(symbols, 10))
    
    with Pool(10) as p:
        p.map(process_symbol, symbol_chunks)
