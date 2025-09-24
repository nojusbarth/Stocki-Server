from datetime import datetime, timedelta
from time import sleep
from data import StockManager
import threading
import time
import locks
import logging

class StockUpdater:
    


    def __init__(self, interval, updateQueue):
        self.interval = interval
        self.queue = updateQueue
        self.logger = logging.getLogger("stock")


    def run(self):

        stockManager = StockManager.StockManager()

        while True:
            start_time = time.time()
            updateBatch = stockManager.getStockTickers()

            updatedStocks = stockManager.updateStocks(self.interval, updateBatch)

            if updatedStocks:
                self.queue.put(updatedStocks)

                update_duration = time.time() - start_time

                self.logger.info({
                    "event": "stock_update_complete",
                    "interval": self.interval,
                    "update_duration_s": round(update_duration, 2),
                    "sleep_s": self.calculateSleepSeconds(),
                    "thread": threading.current_thread().name
                })

            sleepSeconds = self.calculateSleepSeconds()
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


