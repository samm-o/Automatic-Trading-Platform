import mysql.connector, config

try:
  connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toor"
  )
except Exception as e:
  print(e)
  exit(1)  # Exit the script if the connection cannot be established

cursor = connection.cursor(dictionary=True)

# Create a new database
cursor.execute("CREATE DATABASE IF NOT EXISTS app2")

# Now we need to connect to the new database
connection.close()  # Close the old connection first
try:
  connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toor",
    database="app2"
  )
except Exception as e:
  print(e)
  exit(1)  # Exit the script if the connection cannot be established

cursor = connection.cursor(dictionary=True)

# cursor.execute("CREATE DATABASE IF NOT EXISTS app2")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(255) NOT NULL UNIQUE,
    name TEXT NOT NULL,
    exchange TEXT NOT NULL
    )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_price (
    id INTEGER AUTO_INCREMENT PRIMARY KEY, 
    stock_id INTEGER,
    datetime TEXT NOT NULL,
    open TEXT NOT NULL, 
    high TEXT NOT NULL,
    low TEXT NOT NULL, 
    close TEXT NOT NULL, 
    volume TEXT NOT NULL,
    sma_20 TEXT,
    sma_50 TEXT,
    rsi_14 TEXT,
    FOREIGN KEY (stock_id) REFERENCES stock (id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS strategy (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name TEXT NOT NULL
)
""")

cursor.execute("""
	CREATE TABLE IF NOT EXISTS stock_strategy (
    stock_id INTEGER NOT NULL,
    strategy_id INTEGER NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES stock (id),
    FOREIGN KEY (strategy_id) REFERENCES strategy (id)
	)
""")

# strategies = ['opening_range_breakout', 'opening_range_breakdown', 'bollinger_bands']

# for strategy in strategies:
#     cursor.execute("""
#         INSERT INTO strategy (name) VALUES (%s)
#     """, (strategy,))
    
cursor.execute("""
  CREATE TABLE IF NOT EXISTS stock_price_minute (
    id INTEGER AUTO_INCREMENT PRIMARY KEY, 
    stock_id INTEGER,
    datetime TEXT NOT NULL,
    open INTEGER NOT NULL, 
    high INTEGER NOT NULL,
    low INTEGER NOT NULL, 
    close INTEGER NOT NULL, 
    volume INTEGER NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES stock (id),
    UNIQUE (stock_id, datetime(20))
)
""")
    
connection.commit()