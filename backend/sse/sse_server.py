from flask import Flask, Response
import json
import time
import yfinance as yf

app = Flask(__name__)

def fetch_stock_price(stock_symbol):
    """Fetch the latest stock price for the given symbol using yfinance."""
    stock = yf.Ticker(stock_symbol)
    data = stock.history(period="1d")
    # Get the latest close price
    price = data['Close'].iloc[-1]
    return round(price, 2)

def generate_data(stock_symbol="AAPL"):
    """Stream real-time stock price data using Server-Sent Events (SSE)."""
    while True:
        # Fetch real stock data using yfinance
        price = fetch_stock_price(stock_symbol)
        data = json.dumps({"stock": stock_symbol, "price": price})
        
        # Yield the data in SSE format
        yield f"data: {data}\n\n"
        time.sleep(3)  # Set interval for pushing updates (adjust as needed)

@app.route('/events/<symbol>')
def stream(symbol="AAPL"):
    """SSE endpoint for streaming data."""
    return Response(generate_data(symbol), mimetype='text/event-stream')

if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
