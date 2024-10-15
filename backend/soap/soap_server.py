from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import yfinance as yf

app = Flask(__name__)

class StockService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def getStockPrice(ctx, symbol):
        try:
            stock = yf.Ticker(symbol)
            price = stock.history(period="1d")['Close'].iloc[0]
            return f"The stock price of {symbol} is {price}"
        except Exception as e:
            return f"Error fetching stock price for {symbol}: {str(e)}"

soap_app = Application([StockService], 'stock.soap.api',
                       in_protocol=Soap11(validator='lxml'),
                       out_protocol=Soap11())
wsgi_app = WsgiApplication(soap_app)

# Attach the SOAP app to Flask
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/soap': wsgi_app})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5004)
