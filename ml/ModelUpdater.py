
from datetime import datetime, timedelta
from time import sleep
from data import StockManager
from data.update import StockUpdater
from ml import ModelManager
import queue


class ModelUpdater:


    def __init__(self, updateQueue, predictionRepository):
        self.queue = updateQueue
        self.predictionRep = predictionRepository
        self.queueTimeOutTime=10 #seconds

    
    def run(self):
        stockManager = StockManager.StockManager()
        modelManager = ModelManager.ModelManager()

        

        while True:

            try:

                stocksInfo = self.queue.get(timeout=self.queueTimeOutTime)

                for stockInfo in stocksInfo:

                    if not modelManager.containsModel(stockInfo.stockName, stockInfo.interval) or not modelManager.isModelUpdated(stockInfo):
                        modelManager.createNewModel(stockInfo.stockName, 
                                                    stockManager.getStockData(stockInfo.stockName, stockInfo.interval), 
                                                    stockInfo.interval, version="test", 
                                                    hyperTune=True, 
                                                    showStats=False)
                        self.predictionRep.updatePrediction(stockInfo.stockName, stockInfo.interval)
                        print(f"{stockInfo.interval}, {stockInfo.stockName} model update complete.")

                self.queue.task_done()


            except queue.Empty:
                continue