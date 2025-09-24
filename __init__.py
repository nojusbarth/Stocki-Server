# https://towardsdatascience.com/a-comprehensive-guide-to-downloading-stock-prices-in-python-2cd93ff821d4

import tkinter as tk
from tkinter import ttk
from api.server import Server
from data.database import StockDB
from data.update import StockUpdater
from ml.prediction import Predictor
from ml.ModelManager import ModelManager
from data import Stock, StockManager
from ml.prediction.repository import PredictionRepository
from view import MainFrame
from windowMng import *
from ml import ModelUpdater
import queue
import threading
import time


def setupUpdateLoops(predictionRepository):
    updateQueue = queue.Queue()
    
    hourStockUpdater = StockUpdater.StockUpdater(interval="1h", updateQueue=updateQueue)
    dayStockUpdater = StockUpdater.StockUpdater(interval="1d", updateQueue=updateQueue)

    modelUpdater = ModelUpdater.ModelUpdater(updateQueue=updateQueue, predictionRepository=predictionRepository)

    threading.Thread(target=hourStockUpdater.run, daemon=True, name="StockUpdater-1h").start()
    threading.Thread(target=dayStockUpdater.run, daemon=True, name="StockUpdater-1d").start()
    threading.Thread(target=modelUpdater.run, daemon=True, name="ModelUpdater").start()

#TODO: Minuten aggregierungstrick testen: bei yf update 1m wenn 1h gegeben und dann pd aggregieren

#
if __name__ == "__main__":
    
    # root
    #root = tk.Tk()
    #root.configure(bg='light steel blue')
    #root.state('zoomed')
    #root.geometry(STOCKI_LAYOUT_frameGeometry)
    #root.title(STOCKI_LAYOUT_AppTitle)
    
    #wm = WindowMng(root)
        
    #root.mainloop()

    #Alles Datetime machen in UTC
    
    stockManager = StockManager.StockManager()
    modelManager = ModelManager()
    
    predictor = Predictor.Predictor(modelManager=modelManager,stockManager=stockManager)

    predictionRepository = PredictionRepository.PredictionRepository(predictor=predictor)

    #setupUpdateLoops(predictionRepository)
    
    server = Server(predictionRepository, stockManager=stockManager, modelManager=modelManager)
    
    server.start()

    #frame = MainFrame.MainFrame(stockManager=stockManager,modelManager=modelManager)
    #frame.run()

    input("Press Enter to exit...")
