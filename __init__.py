# https://towardsdatascience.com/a-comprehensive-guide-to-downloading-stock-prices-in-python-2cd93ff821d4

import tkinter as tk
from tkinter import ttk
from api.server import Server
from ml import Predictor
from ml.ModelManager import ModelManager
from ml.model_core import ModelEvaluator
from data import Stock, StockManager
from view import MainFrame
from windowMng import *


def updateLoop(stockManager, modelManager, interval):
    #update loop

    stockManager.updateStocks(interval)
    updateInfos = stockManager.getLatestUpdateInfo()
    for updateInfo in updateInfos[interval]:
        if not modelManager.isModelUpdated(updateInfo):
            #create new model with up to date data

            stockData = stockManager.getStockData(updateInfo.stockName, interval)
            if stockData is not None:
                print(f"Creating new model for stock {updateInfo.stockName}")
                modelManager.createNewModel(updateInfo.stockName, stockData, hyperTune=False, showStats=True)
            else:
                print(f"Stock {updateInfo.stockName} not found in stock manager")


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

    updateLoop(stockManager=stockManager, modelManager=modelManager, interval="1d");
    

    server = Server(predictor=predictor, stockManager=stockManager)


    server.start()


    #frame = MainFrame.MainFrame(stockManager=stockManager,modelManager=modelManager)
    #frame.run()

    input("Press Enter to exit...")
