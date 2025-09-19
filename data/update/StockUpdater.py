from datetime import datetime, timedelta
from time import sleep
from data import StockManager
import threading


class StockUpdater:
    
    #allow only one yf call at a time
    yfLock = threading.Lock()


    def __init__(self, interval):
        self.interval = interval


    def run(self):

        stockManager = StockManager.StockManager()

        while True:

            updateBatch = stockManager.getStockNames()
            print(f"Running update for {self.interval} at {datetime.now()}")

            with StockUpdater.yfLock:
                stockManager.updateStocks(self.interval, updateBatch)

            sleepSeconds = self.calculateSleepSeconds()

            print(f"Update complete. Sleeping for {sleepSeconds/60:.2f} minutes.")

            sleep(sleepSeconds)



    #private
    def calculateSleepSeconds(self):

        now = datetime.now()
        if self.interval == "1h":
            nextRun = now + timedelta(minutes=15)
        elif self.interval == "1d":
            nextRun = now.replace(hour=23, minute=0, second=0, microsecond=0)
            if now >= nextRun:
                nextRun += timedelta(days=1)
        return (nextRun - now).total_seconds()


