
from datetime import datetime, timedelta
from time import sleep
from data import StockManager
from ml import ModelManager


class ModelUpdater:


    def __init__(self, interval):
        self.interval = interval

    
    def run(self):
        stockManager = StockManager.StockManager()
        modelManager = ModelManager.ModelManager()

        

        while True:

            stocksInfo = stockManager.getLatestUpdateInfo(interval=self.interval)

            for stockInfo in stocksInfo:

                if not modelManager.containsModel(stockInfo.stockName, stockInfo.interval) or not modelManager.isModelUpdated(stockInfo):
                    modelManager.createNewModel(stockInfo.stockName, 
                                                stockManager.getStockData(stockInfo.stockName, stockInfo.interval), 
                                                stockInfo.interval, version="test", 
                                                hyperTune=True, 
                                                showStats=False)

            sleepTime = self.calculateSleepSeconds()
            print(f"{self.interval} model update complete. Sleeping for {sleepTime/60:.2f} minutes.")
            sleep(sleepTime)
            
            
    #private
    def calculateSleepSeconds(self):

        now = datetime.now()
        if self.interval == "1h":
            nextRun = now + timedelta(minutes=10)
        elif self.interval == "1d":
            nextRun = now.replace(hour=23, minute=30, second=0, microsecond=0)
            if now >= nextRun:
                nextRun += timedelta(days=1)
        return (nextRun - now).total_seconds()