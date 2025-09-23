

from api import AccuracyPackager, TickerMapper
from flask import Flask, request, jsonify



class Server:

    def __init__(self, predictonRep, stockManager, modelManager):
        self.predictonRep = predictonRep
        self.stockManager = stockManager
        self.modelManager = modelManager
        self.tickerMap = TickerMapper.TickerMapper(self.stockManager.getStockTickers())
        self.accuracyPackager = AccuracyPackager.AccuracyPackager(stockManager, predictonRep)

        self.app = Flask(__name__)
        self.setupRoutes()



    def setupRoutes(self):
        @self.app.route("/predictions/<name>", methods=["GET"])
        def getPrediction(name):
            interval = str(request.args.get("interval", "1d"))

            ticker = self.tickerMap.getTicker(name)

            packets = self.predictonRep.getLatestPrediction(ticker,interval)

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

        @self.app.route("/predictionsall/", methods=["GET"])
        def getAllPredictions():
            interval = str(request.args.get("interval", "1d"))

            allPreds = self.predictonRep.getAllLatestPredictions(self.stockManager.getStockTickers(), interval)

            jsonReady = {self.tickerMap.getName(ticker): vars(packet) 
                         for ticker, packet in allPreds.items() if self.tickerMap.getName(ticker) is not None}
            return jsonify(jsonReady)

        @self.app.route("/accuracy/<name>", methods=["GET"])
        def getLastPredictions(name):
            interval = str(request.args.get("interval", "1d"))
            period = int(request.args.get("period", 5))

            ticker = self.tickerMap.getTicker(name)
            historicals = self.accuracyPackager.buildPackets(ticker, interval, period)

            jsonReady = {key: [vars(pkt) if pkt is not None else None for pkt in pkts] 
                         for key, pkts in historicals.items()}

            return jsonify(jsonReady)

    def start(self):
        self.app.run(host="0.0.0.0", port=5000, debug=False)