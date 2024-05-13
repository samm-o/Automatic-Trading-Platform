import mysql.connector, config
import alpaca_trade_api as tradeapi

connection = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
    ) # Replace with your MySQL database credentials

cursor = connection.cursor(dictionary=True)

cursor.execute("""
    SELECT symbol, name FROM stock
""")

rows = cursor.fetchall()
symbols = [row['symbol'] for row in rows]

api = tradeapi.REST(config.API_KEY, config.SECRET, base_url=config.API_URL)
assets = api.list_assets()

for asset in assets:   
    try:
        if asset.symbol not in symbols and asset.status == 'active' and asset.tradable:
            print(f"Added a new stock: {asset.symbol} {asset.name}")
            cursor.execute("INSERT INTO stock (symbol, name, exchange) VALUES (%s, %s, %s)", (asset.symbol, asset.name, asset.exchange))
    except Exception as e:
        print(asset.symbol)
        print(e)

connection.commit()
