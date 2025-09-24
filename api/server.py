

from api import AccuracyPackager, TickerMapper
from flask import Flask, request, jsonify, g
import time
import threading
import logging

class Server:

    def __init__(self, predictonRep, stockManager, modelManager):
        self.logger = logging.getLogger("api")
        
        self.predictonRep = predictonRep
        self.stockManager = stockManager
        self.modelManager = modelManager
        self.tickerMap = TickerMapper.TickerMapper(self.stockManager.getStockTickers())
        self.accuracyPackager = AccuracyPackager.AccuracyPackager(stockManager, predictonRep)

        self.app = Flask(__name__)
        self.setupLoggingHooks() 
        self.setupRoutes()




    def setupLoggingHooks(self):
        @self.app.before_request
        def start_timer():
            g.start_time = time.time()

        @self.app.after_request
        def log_request(response):
            duration = time.time() - g.start_time
            self.logger.info({
                "event": "request_completed",
                "path": request.path,
                "method": request.method,
                "status": response.status_code,
                "duration_s": round(duration, 4),
                "thread": threading.current_thread().name
            })
            return response

        @self.app.errorhandler(Exception)
        def handle_exception(e):
            duration = time.time() - g.start_time if hasattr(g, "start_time") else None
            self.logger.exception({
                "event": "exception",
                "path": request.path if request else None,
                "method": request.method if request else None,
                "duration_s": round(duration, 4) if duration else None,
                "thread": threading.current_thread().name,
                "exception": str(e)
            })
            return {"error": str(e)}, 500


    def setupRoutes(self):
        @self.app.route("/predictions/<name>", methods=["GET"])
        def getPrediction(name):
            interval = str(request.args.get("interval", "1d"))

            ticker = self.tickerMap.getTicker(name)
            packets = self.predictonRep.getLatestPrediction(ticker,interval)

            jsonReady = [p.toDict() for p in packets]

            return jsonify(jsonReady)


        @self.app.route("/historical/<name>", methods=["GET"])
        def getHistorical(name):
            
            period = int(request.args.get("period", 30))
            interval = str(request.args.get("interval", "1d"))

            ticker = self.tickerMap.getTicker(name)

            data = self.stockManager.getStockData(ticker, interval).tail(period)

            result = [{"date": index.isoformat(), "close": row["Close"]} 
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

            return jsonify(info.toDict())

        @self.app.route("/predictionsall/", methods=["GET"])
        def getAllPredictions():
            interval = str(request.args.get("interval", "1d"))

            allPreds = self.predictonRep.getAllLatestPredictions(self.stockManager.getStockTickers(), interval)

            jsonReady = {self.tickerMap.getName(ticker): packet.toDict()
                         for ticker, packet in allPreds.items() if self.tickerMap.getName(ticker) is not None}
            return jsonify(jsonReady)


        @self.app.route("/accuracy/<name>", methods=["GET"])
        def getLastPredictions(name):
            interval = str(request.args.get("interval", "1d"))
            period = int(request.args.get("period", 5))

            ticker = self.tickerMap.getTicker(name)
            historicals = self.accuracyPackager.buildPackets(ticker, interval, period)

            jsonReady = {key: [pkt if pkt is not None else None for pkt in pkts] 
                         for key, pkts in historicals.items()}

            return jsonify(jsonReady)

    def start(self):
        self.app.run(host="0.0.0.0", port=5000, debug=False)

    def shutdown(self):
        if Server._instances == 0 and Server.app_logger_instance:
            Server.app_logger_instance.stop_listener()