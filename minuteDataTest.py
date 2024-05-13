import config
import mysql.connector
import pandas
import csv
from datetime import datetime, timedelta
from ib_insync import *

connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toor",
    database="app2"
    )

cursor = connection.cursor(dictionary=True, buffered=True)

ib = IB()
ib.connect(config.TWS_HOST, config.TWS_PORT, clientId=123)

symbols = []
stock_ids = {}

with open('qqq.csv') as f:
    reader = csv.reader(f)

    for line in reader:
        symbols.append(line[1])

cursor.execute("""
    SELECT * FROM stock
""")

stocks = cursor.fetchall()

for stock in stocks:
    symbol = stock['symbol']
    stock_ids[symbol] = stock['id']
    
for symbol in symbols:
    start_date = datetime(2020, 1, 6).date()
    end_date_range = datetime(2020, 11, 20).date()

    while start_date < end_date_range:
        end_date = start_date + timedelta(days=4)
        contract = Stock(symbol, 'SMART', 'USD')

        print(f"== Fetching minute bars for {symbol} {start_date} - {end_date} ==")
        try:
            minutes = ib.reqHistoricalData(
                    contract,
                    endDateTime=end_date.strftime('%Y%m%d %H:%M:%S'),
                    durationStr='2 D',
                    barSizeSetting='1 min',
                    whatToShow='TRADES',
                    useRTH=True,
                    formatDate=1
                ).df
        except Exception as e:
            print(e)
        minutes = minutes.resample('1min').ffill()

        for index, row in minutes.iterrows():
            cursor.execute("""
                INSERT INTO stock_price_minute (stock_id, datetime, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (stock_ids[symbol], index.tz_localize(None).isoformat(), row['open'], row['high'], row['low'], row['close'], row['volume']))

        start_date = start_date + timedelta(days=7)

ib.disconnect()
connection.commit()