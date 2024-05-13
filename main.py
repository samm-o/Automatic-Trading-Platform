# First Gen Front-End that uses Jinja2 HTML Templates
import mysql.connector, config
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date
from ib_insync import IB, util
from datetime import date
from fastapi import BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
current_date = date.today().strftime("%Y-%m-%d")

print(current_date)
@app.get("/")
def index(request: Request):
    stock_filter = request.query_params.get('filter', False)
    
    connection = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
    ) # Replace with your MySQL database credentials
    
    cursor = connection.cursor(dictionary=True)
    
    if stock_filter == 'new_closing_highs':
        cursor.execute(""" 
        select * from(
            select symbol, name, stock_id, max(close), datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            group by stock_id
            order by symbol
        )where datetime = (select max(datetime) from stock_price)
        """)
    elif stock_filter == 'new_closing_lows':
        cursor.execute(""" 
        select * from(
            select symbol, name, stock_id, min(close), datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            group by stock_id
            order by symbol
        )where datetime = (select max(datetime) from stock_price)
        """)
    elif stock_filter == 'rsi_overbought':
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where rsi_14 > 70
            AND datetime = (select max(datetime) from stock_price)
            order by symbol
        """)
    elif stock_filter == 'rsi_oversold':
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where rsi_14 < 30
            AND datetime = (select max(datetime) from stock_price)
            order by symbol
        """)
    elif stock_filter == 'above_sma_20':
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where close > sma_20
            AND datetime = (select max(datetime) from stock_price)
            order by symbol
        """)
    elif stock_filter == 'below_sma_20':
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where close < sma_20
            AND datetime = (select max(datetime) from stock_price)
            order by symbol
        """)
    elif stock_filter == 'above_sma_50':
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where close > sma_50
            AND datetime = (select max(datetime) from stock_price)
            order by symbol
        """)
    elif stock_filter == 'below_sma_50':
        cursor.execute(""" 
            select symbol, name, stock_id, datetime
            from stock_price join stock on stock.id = stock_price.stock_id
            where close < sma_50
            AND datetime = (select max(datetime) from stock_price)
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
    
    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows, "indicator_values": indicator_values})

@app.get("/stock/{symbol}")
def stock_detail(request: Request, symbol):
    connection = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
    ) # Replace with your MySQL database credentials

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
    prices = cursor.fetchall()
    
    return templates.TemplateResponse("stock_detail.html", {"request": request, "stock": row, "bars": prices, "strategies": strategies})

@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    connection = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
    ) # Replace with your MySQL database credentials

    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (%s, %s)
    """, (stock_id, strategy_id))
    
    connection.commit()
    
    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code=303)

@app.get("/strategies")
def strategies(request: Request):
    connection = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
    ) # Replace with your MySQL database credentials
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM strategy
    """)
    strategies = cursor.fetchall()
    return templates.TemplateResponse("strategies.html", {"request": request, "strategies": strategies})

@app.get("/trades")
async def trades(request: Request):
    # Create an instance of the IB class
    ib = IB()

    await ib.connectAsync(config.TWS_HOST, config.TWS_PORT, clientId=config.TWS_CLIENT_ID)

    trades = ib.trades()
        
    ib.disconnect()
    return templates.TemplateResponse("orders.html", {"request": request, "trades": trades})
    
@app.get("/strategy/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
    ) # Replace with your MySQL database credentials

    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, name 
        FROM strategy
        WHERE id = %s
    """, (strategy_id,))
    strategy = cursor.fetchone()
    
    cursor.execute("""
        SELECT symbol, name
        FROM stock JOIN stock_strategy ON stock_strategy.stock_id = stock.id
        WHERE strategy_id = %s
    """, (strategy_id,))
    stocks = cursor.fetchall()
    
    return templates.TemplateResponse("strategy.html", {"request": request, "stocks": stocks, "strategy": strategy})
