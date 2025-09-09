import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
from pathlib import Path
from ml import DataPreparer
from ml import ModelFiles

from ml.model_core import ModelMaker


class ModelManager:

    def __init__(self):
        self.modelFiler = ModelFiles.ModelFiles(Path(r"C:\Users\nojob\Programmieren\Visual Studio\python\Stocki\project\predictionModels"))
        self.modelMaker = ModelMaker.ModelMaker()

    def createNewModel(self, stockName, stockData, hyperTune=False, showStats=False):

        data = stockData.copy()

        self.model = self.modelMaker.createModel(data, hyperTune=hyperTune, showStats=showStats)
        
        #save model
        answer = input('should model be saved?:')
        
        if answer.lower() in ['y', 'yes']:
            self.modelFiler.saveModel(self.model, stockName)



    def getFittingModel(self, stockName):

        model = self.modelFiler.loadModel(stockName)
        if model is None:
            print(f"No saved model found for stock {stockName}.")
            return None
        return model



    def isModelUpdated(self, stockUpdateInfo):
        return self.modelFiler.isModelUpdated(stockUpdateInfo.stockName, stockUpdateInfo.latestUpdateTime)

