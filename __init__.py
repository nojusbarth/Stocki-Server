# https://towardsdatascience.com/a-comprehensive-guide-to-downloading-stock-prices-in-python-2cd93ff821d4

import tkinter as tk
from tkinter import ttk
from api.server import Server
from data.database import StockDB
from data.update import StockUpdater
from ml.prediction import Predictor
from ml.ModelManager import ModelManager
from data import Stock, StockManager
from view import MainFrame
from windowMng import *
from ml import ModelUpdater

import threading
import time


def setupUpdateLoopStocks():
    hourUpdater = StockUpdater.StockUpdater(interval="1h")
    dayUpdater = StockUpdater.StockUpdater(interval="1d")

    hourThread = threading.Thread(target=hourUpdater.run, daemon=True)
    dayThread = threading.Thread(target=dayUpdater.run, daemon=True)

    hourThread.start()
    dayThread.start()


def setupUpdateLoopModels():
    hourModelUpdater = ModelUpdater.ModelUpdater(interval="1h")
    dayModelUpdater = ModelUpdater.ModelUpdater(interval="1d")
    hourModelThread = threading.Thread(target=hourModelUpdater.run, daemon=True)
    dayModelThread = threading.Thread(target=dayModelUpdater.run, daemon=True)
    hourModelThread.start()
    dayModelThread.start()


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

    
    stockManager = StockManager.StockManager()
    modelManager = ModelManager()
    
    predictor = Predictor.Predictor(modelManager=modelManager,stockManager=stockManager)

    #setupUpdateLoopStocks()
    #setupUpdateLoopModels()
    #
    server = Server(predictor=predictor, stockManager=stockManager, modelManager=modelManager)
    #
    server.start()



    #frame = MainFrame.MainFrame(stockManager=stockManager,modelManager=modelManager)
    #frame.run()

    input("Press Enter to exit...")
