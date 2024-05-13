import config
from ib_insync import *
from datetime import datetime, timedelta
import csv
from multiprocessing import Pool
import os
import pandas as pd
import mysql.connector

current_date = datetime.today()

connection = mysql.connector.connect(
host="127.0.0.1",
user="root",
password="toor",
database="app2"
)

symbols = []
stock_ids = {}

cursor = connection.cursor(dictionary=True)
cursor.execute("""
    SELECT * FROM stock
""")
stocks = cursor.fetchall()

# Create a dictionary with symbol as key and id as value
for stock in stocks:
    symbol = stock['symbol']
    stock_ids[symbol] = stock['id']

with open('qqq.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        symbols.append(line[1])

def split_list(lst, n):
    """Split a list into n chunks"""
    k, m = divmod(len(lst), n)
    return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

def process_symbol(symbol_chunk):
    
    connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toor",
    database="app2"
    )

    cursor = connection.cursor(dictionary=True, buffered=True)
    ib = IB()
    ib.connect(config.TWS_HOST, config.TWS_PORT, clientId=config.TWS_CLIENT_ID + os.getpid())

    for symbol in symbol_chunk:
        start_date = datetime(2023, 3, 18).date()
        end_date = datetime(2024, 3, 18).date()
        
        while start_date <= end_date:

            cursor.execute("""
                SELECT id FROM stock WHERE symbol = %s
            """, (symbol,))

            contract = Stock(symbol, 'SMART', 'USD')  # replace 'SMART' with the actual exchange if necessary
            
            try:
                bars = ib.reqHistoricalData(
                    contract,
                    endDateTime=end_date.strftime('%Y%m%d %H:%M:%S'),
                    durationStr='1 D',
                    barSizeSetting='1 min',
                    whatToShow='TRADES',
                    useRTH=True,
                    formatDate=1
                )
            except Exception as e:
                print(f"Error requesting data for symbol {symbol}: {e}")
                continue
            
            if bars:
                minutes = util.df(bars)
                minutes.set_index('date', inplace=True)
                minutes.index = pd.to_datetime(minutes.index)
                minutes = minutes.resample('1min').ffill()
                
                data = []
                for index, row in minutes.iterrows():
                    data.append((stock_ids[symbol], index.tz_localize(None).isoformat(), row['open'], row['high'], row['low'], row['close'], row['volume']))

                print(f"processing symbol {symbol} at ({start_date} - {end_date})")
                cursor.executemany("""
                    INSERT IGNORE INTO stock_price_minute (stock_id, datetime, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, data)
                connection.commit()

                end_date -= timedelta(days=1)
                
            else:
                print(f"No data returned for symbol {symbol}")
                break   

if __name__ == '__main__':
    symbol_chunks = list(split_list(symbols, 20))
    
    with Pool(20) as p:
        p.map(process_symbol, symbol_chunks)