
import logging
import time
import queue
from multiprocessing import Manager, Pool
from shared.data import StockManager
from shared.ml import ModelManager
from shared.logger import setup_logging
import sys
from datetime import datetime

class ModelUpdater:
    @staticmethod
    def process_stock(stockInfo, predictionQueue):
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)        
        setup_logging()
        stock_name = stockInfo.stockName
        interval = stockInfo.interval

        print(f"Processing {stock_name} ({interval})", flush=True)
        
        
        start_time = datetime.utcnow()
        stockManager = StockManager.StockManager()
        modelManager = ModelManager.ModelManager()

        if not modelManager.containsModel(stock_name, interval) or \
           not modelManager.isModelUpdated(stockInfo):
            
            modelManager.createNewModel(
                stock_name,
                stockManager.getStockData(stock_name, interval),
                interval,
                version="test",
                hyperTune=True,
                showStats=False
            )


        end_time = datetime.utcnow()
        duration = end_time - start_time

        predictionQueue.put(stockInfo)
        print(f"Processed {stock_name} ({interval}) in {duration}")