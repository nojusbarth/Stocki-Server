

from flask import Flask, request, jsonify



class Server:

    def __init__(self, predictor, stockManager):
        self.predictor = predictor
        self.stockManager = stockManager

        self.app = Flask(__name__)
        self.setupRoutes()



    def setupRoutes(self):
        @self.app.route("/predictions/<ticker>", methods=["GET"])
        def getPrediction(ticker):
            period = int(request.args.get("period", 1))
            interval = str(request.args.get("interval", "1d"))

            packets = self.predictor.predict(ticker,period,interval)

            jsonReady = [vars(p) for p in packets]

            return jsonify(jsonReady)


        @self.app.route("/historical/<ticker>", methods=["GET"])
        def getHistorical(ticker):
            
            period = int(request.args.get("period", 30))
            interval = str(request.args.get("interval", "1d"))


            data = self.stockManager.getStockData(ticker, interval).tail(period)

            dateFormat = "%Y-%m-%d" if interval == "1d" else "%Y-%m-%d %H:%M"

            result = [{"date": index.strftime(dateFormat), "close": row["Close"]} 
              for index, row in data.iterrows()]
            
            
            return jsonify(result)

        @self.app.route("/stocknames", methods=["GET"])
        def getStockNames():

            stockNamesList = self.stockManager.getStockNames()

            return jsonify(stockNamesList)



    def start(self):
        self.app.run(debug=False)