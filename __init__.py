# https://towardsdatascience.com/a-comprehensive-guide-to-downloading-stock-prices-in-python-2cd93ff821d4

import tkinter as tk
from tkinter import ttk
from control import Predictor
from control.ModelManager import ModelManager
from control.model_core import ModelEvaluator
from model import Stock, StockManager
from view import MainFrame
from windowMng import *


def updateLoop(stockManager, modelManager):
    #update loop

    stockManager.updateStocks()
    updateInfos = stockManager.getLatestUpdateInfo()
    for updateInfo in updateInfos:
        if modelManager.isModelUpdated(updateInfo):
            print(f"Model for stock {updateInfo.stockName} is up to date")
        else:
            #create new model with up to date data

            stock = stockManager.getStock(updateInfo.stockName)
            if stock is not None:
                print(f"Creating new model for stock {updateInfo.stockName}")
                modelManager.createNewModel(updateInfo.stockName, stock.getData(), hyperTune=False, showStats=True)
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


    updateLoop(stockManager=stockManager, modelManager=modelManager);
    

    frame = MainFrame.MainFrame(stockManager=stockManager,modelManager=modelManager)
    frame.run()

    input("Press Enter to exit...")
