#Second Gen Front-End that uses React
import mysql.connector, config
from fastapi import FastAPI, Request, Form
from datetime import date
from ib_insync import IB
from datetime import date
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.mount("/static", StaticFiles(directory=r"C:\Users\Samuil Georgiev\Projects\FullstackTradingApp\build", html=True), name="fullstacktradingapp")

origins = [
    "http://localhost:3000",  # React app
    "http://127.0.0.1:8000", # FastAPI server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_date = date.today().strftime("%Y-%m-%d")
print(current_date)

@app.get("/")
def index(request: Request):
    full_path = str(request.url)
    
    print(full_path)
    
    connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toor",
    database="app2"
    )
    cursor = connection.cursor(dictionary=True)
    
    if 'new_closing_highs' in full_path:
        cursor.execute(""" 
        SELECT * FROM (
            SELECT symbol, name, stock_id, max(close) AS max_close, datetime
            FROM stock_price 
            JOIN stock ON stock.id = stock_price.stock_id
            where datetime = (select max(datetime) from stock_price)
            GROUP BY stock_id, datetime
            ORDER BY symbol
        ) AS derived_table
        """)
    elif 'new_closing_lows' in full_path:
        cursor.execute(""" 
        SELECT * FROM (
            SELECT symbol, name, stock_id, min(close) AS min_close, datetime
            FROM stock_price 
            JOIN stock ON stock.id = stock_price.stock_id
            where datetime = (select max(datetime) from stock_price)
            GROUP BY stock_id, datetime
            ORDER BY symbol
        ) AS derived_table
        """)
    elif 'rsi_overbought' in full_path:
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where rsi_14 > 70
            AND datetime = '2024-3-18'
            order by symbol
        """)
    elif 'rsi_oversold' in full_path:
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where rsi_14 < 30
            AND datetime = '2024-3-18'
            order by symbol
        """)
    elif 'above_sma_20' in full_path:
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where close > sma_20
            AND datetime = '2024-3-18'
            order by symbol
        """)
    elif 'below_sma_20' in full_path:
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where close < sma_20
            AND datetime = '2024-3-18'
            order by symbol
        """)
    elif 'above_sma_50' in full_path:
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where close > sma_50
            AND datetime = '2024-3-18'
            order by symbol
        """)
    elif 'below_sma_50' in full_path:
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where close < sma_50
            AND datetime = '2024-3-18'
            order by symbol
        """)
    else:
        cursor.execute("""
    SELECT id, symbol, name FROM stock ORDER BY symbol
    """)
    rows = cursor.fetchall()
    
    
    cursor.execute(f"""
    SELECT symbol, rsi_14, sma_20, sma_50, close
    FROM stock JOIN stock_price ON stock_price.stock_id = stock.id
    WHERE datetime = '2024-3-18'
    """)
    
    indicator_rows = cursor.fetchall()
    indicator_values = {}
    
    for row in indicator_rows:
        indicator_values[row['symbol']] = row

    return {"stocks": rows, "indicator_values": indicator_values}

@app.get("/stock/{symbol}")
def stock_detail(request: Request, symbol):
    connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toor",
    database="app2"
    )
    
    full_path = str(request.url)
    print(full_path)

    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM strategy
    """)
    strategies = cursor.fetchall()
    
    cursor.execute("""
        SELECT * FROM stock WHERE symbol = %s
    """, (symbol,))
    
    row = cursor.fetchone()
    
    cursor.execute("""
    SELECT * FROM stock_price 
    WHERE stock_id = %s 
    ORDER BY STR_TO_DATE(datetime, '%Y-%m-%d') DESC
    """, (row['id'],))

    bars = cursor.fetchall()

    return {"stock": row, "bars": bars, "stock_id": row['id']}

@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    print(f"Received strategy_id: {strategy_id}, stock_id: {stock_id}")
    connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toor",
    database="app2"
    )

    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (%s, %s)
    """, (stock_id, strategy_id))
    
    connection.commit()

@app.get("/strategies")
def strategies(request: Request):
    connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toor",
    database="app2"
    )
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, name 
        FROM strategy
    """)
    strategies = cursor.fetchall()

    for strategy in strategies:
        cursor.execute("""
            SELECT symbol, name
            FROM stock JOIN stock_strategy ON stock_strategy.stock_id = stock.id
            WHERE strategy_id = %s
        """, (strategy['id'],))
        stocks = cursor.fetchall()
        strategy['stocks'] = stocks
    
    return {"strategies": strategies}

@app.delete("/strategies/{strategy_id}/stocks/{symbol}")
async def remove_stock(strategy_id: int, symbol: str):
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="toor",
        database="app2"
    )
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        DELETE FROM stock_strategy 
        WHERE strategy_id = %s AND stock_id = (SELECT id FROM stock WHERE symbol = %s)
    """, (strategy_id, symbol))
    
    connection.commit()

@app.get("/trades")
async def trades(request: Request):
    # Create an instance of the IB class
    ib = IB()

    await ib.connectAsync(config.TWS_HOST, config.TWS_PORT, clientId=config.TWS_CLIENT_ID)

    trades = ib.trades()
        
    ib.disconnect()
    return {"trades": trades}

@app.post("/login")
async def login(data: dict):
    username = data.get('username')
    password = data.get('password')

    # Replace 'admin' and 'secret' with your hardcoded username and password
    if username == 'sammo' and password == 'trading':
        return {"success": True}
    else:
        return {"success": False}


