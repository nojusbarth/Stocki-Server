from datetime import datetime, timedelta
from time import sleep
from data import StockManager
import threading

import locks


class StockUpdater:
    


    def __init__(self, interval, updateQueue):
        self.interval = interval
        self.queue = updateQueue


    def run(self):

        stockManager = StockManager.StockManager()

        while True:

            updateBatch = stockManager.getStockTickers()
            print(f"Running update for {self.interval} at {datetime.now()}")

            with locks.yfLock:
                updatedStocks = stockManager.updateStocks(self.interval, updateBatch)

                if updatedStocks:
                    self.queue.put(updatedStocks)

       

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


