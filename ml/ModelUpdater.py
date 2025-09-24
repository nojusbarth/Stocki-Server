
from datetime import datetime, timedelta
from time import sleep
from data import StockManager
from data.update import StockUpdater
from ml import ModelManager
import queue
import time
import threading
import logging

class ModelUpdater:


    def __init__(self, updateQueue, predictionRepository):
        self.queue = updateQueue
        self.predictionRep = predictionRepository
        self.queueTimeOutTime=10 #seconds
        self.logger = logging.getLogger("model")

    
    def run(self):
        stockManager = StockManager.StockManager()
        modelManager = ModelManager.ModelManager()

        while True:

            try:

                stocksInfo = self.queue.get(timeout=self.queueTimeOutTime)
                start_time = time.time()
                updated_count = 0
                print("STARTED MODEL TRAINING, DONT CLOSE APP")
                for stockInfo in stocksInfo:

                    if not modelManager.containsModel(stockInfo.stockName, stockInfo.interval) or not modelManager.isModelUpdated(stockInfo):
                        modelManager.createNewModel(stockInfo.stockName, 
                                                    stockManager.getStockData(stockInfo.stockName, stockInfo.interval), 
                                                    stockInfo.interval, version="test", 
                                                    hyperTune=True, 
                                                    showStats=False)
                        self.predictionRep.updatePrediction(stockInfo.stockName, stockInfo.interval)
                        updated_count += 1

                self.queue.task_done()
                duration = time.time() - start_time

                self.logger.info({
                    "event": "model_update_batch_complete",
                    "processed_stocks": len(stocksInfo),
                    "updated_models": updated_count,
                    "duration_s": round(duration, 2),
                    "thread": threading.current_thread().name
                })
                print("ENDED MODEL TRAINING")

            except queue.Empty:
                continue