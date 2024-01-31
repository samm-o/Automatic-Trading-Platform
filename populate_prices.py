import sqlite3, config
import alpaca_trade_api as tradeapi

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

api = tradeapi.REST(config.API_KEY, config.SECRET, base_url=config.API_URL)

chunk_size = 200
for i in range(0, len(symbols), chunk_size):
    symbol_chunk = symbols[i:i+chunk_size]
    for symbol in symbol_chunk:
        bars = api.get_bars(symbol, tradeapi.rest.TimeFrame.Day, '2000-01-01')
        print(f"processing symbol {symbol}")
        for bar in bars:
            stock_id = int(stock_dict[symbol])
            cursor.execute("""
                INSERT INTO stock_price (stock_id, datetime, open, high, low, close, volume) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (stock_id, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v))
            connection.commit()
        
