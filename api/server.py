

from api import TickerMapper
from flask import Flask, request, jsonify



class Server:

    def __init__(self, predictor, stockManager, modelManager):
        self.predictor = predictor
        self.stockManager = stockManager
        self.modelManager = modelManager
        self.tickerMap = TickerMapper.TickerMapper(self.stockManager.getStockTickers())

        self.app = Flask(__name__)
        self.setupRoutes()



    def setupRoutes(self):
        @self.app.route("/predictions/<name>", methods=["GET"])
        def getPrediction(name):
            period = int(request.args.get("period", 1))
            interval = str(request.args.get("interval", "1d"))

            ticker = self.tickerMap.getTicker(name)

            packets = self.predictor.predict(ticker,period,interval)

            jsonReady = [vars(p) for p in packets]

            return jsonify(jsonReady)


        @self.app.route("/historical/<name>", methods=["GET"])
        def getHistorical(name):
            
            period = int(request.args.get("period", 30))
            interval = str(request.args.get("interval", "1d"))

            ticker = self.tickerMap.getTicker(name)

            data = self.stockManager.getStockData(ticker, interval).tail(period)

            dateFormat = "%Y-%m-%d" if interval == "1d" else "%Y-%m-%d %H:%M"

            result = [{"date": index.strftime(dateFormat), "close": row["Close"]} 
              for index, row in data.iterrows()]
            
            
            return jsonify(result)

        @self.app.route("/stocknames", methods=["GET"])
        def getStockNames():

            tickerList = self.stockManager.getStockTickers()

            stockNamesList = []

            for t in tickerList:
                name = self.tickerMap.getName(t)
                if name is not None:
                    stockNamesList.append(name)

            return jsonify(stockNamesList)

        @self.app.route("/modelinfo/<name>", methods=["GET"])
        def getModelInfo(name):
            interval = str(request.args.get("interval", "1d"))

            ticker = self.tickerMap.getTicker(name)

            info = self.modelManager.getModelInfo(ticker, interval)

            return jsonify(vars(info))

    def start(self):
        self.app.run(debug=False)