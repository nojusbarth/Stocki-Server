from stockupdates import StockUpdater
from shared.logger import setup_logging
import threading
import time
import logging
import sys

def runStockUpdater(updateQueue, stopEvent):
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    setup_logging()


    print("stock up", flush=True)

    hourStockUpdater = StockUpdater.StockUpdater(interval="1h", updateQueue=updateQueue)
    dayStockUpdater = StockUpdater.StockUpdater(interval="1d", updateQueue=updateQueue)

    threading.Thread(target=hourStockUpdater.run, daemon=True, name="StockUpdater-1h").start()
    threading.Thread(target=dayStockUpdater.run, daemon=True, name="StockUpdater-1d").start()

    try:
        while not stopEvent.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        stopEvent.set()