

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
            days = int(request.args.get("days", 1)) # default is one

            packets = self.predictor.predict(ticker,days,"1d")

            jsonReady = [vars(p) for p in packets]

            return jsonify(jsonReady)


        @self.app.route("/historical/<ticker>", methods=["GET"])
        def getHistorical(ticker):
            
            days = int(request.args.get("days", 30))


            data = self.stockManager.getStockData(ticker, "1d").tail(days)

            result = [{"date": index.strftime("%Y-%m-%d"), "close": row["Close"]} 
              for index, row in data.iterrows()]
            
            
            return jsonify(result)

        @self.app.route("/stocknames", methods=["GET"])
        def getStockNames():

            stockNamesList = self.stockManager.getStockNames()

            return jsonify(stockNamesList)



    def start(self):
        self.app.run(debug=True)