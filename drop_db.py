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

# cursor.execute("""
#     DROP TABLE IF EXISTS stock_price
# """)

# cursor.execute("""
#     DROP TABLE IF EXISTS stock_strategy
# """)

# cursor.execute("""
#     DROP TABLE IF EXISTS stock
# """)

# cursor.execute("""
#     DROP TABLE IF EXISTS strategy
# """)

cursor.execute("""
    DROP TABLE IF EXISTS stock_price_minute
""")

connection.commit()