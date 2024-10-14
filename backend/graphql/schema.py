import graphene
import yfinance as yf

def fetch_stock_price(stock_symbol):
    """Fetch the latest stock price for the given symbol using yfinance."""
    stock = yf.Ticker(stock_symbol)
    data = stock.history(period="1d")
    # Get the latest close price
    price = data['Close'].iloc[-1]
    return round(price, 2)

class Stock(graphene.ObjectType):
    symbol = graphene.String()
    price = graphene.Float()

class Query(graphene.ObjectType):
    stock = graphene.Field(Stock, symbol=graphene.String(required=True))

    def resolve_stock(self, info, symbol):
        price = fetch_stock_price(symbol)
        return Stock(symbol=symbol, price=price)

schema = graphene.Schema(query=Query)
