import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
from pathlib import Path
from ml.pipeline import DataPreparer

from ml.pipeline import ModelMaker
from ml.repository import ModelRepository


class ModelManager:

    def __init__(self):
        self.modelRepository = ModelRepository.ModelRepository()
        self.modelMaker = ModelMaker.ModelMaker()



    def createNewModel(self, stockName, stockData, interval, version, hyperTune=False, showStats=False):
        
        #model pipeline
        modelDev, modelProd = self.modelMaker.createModel(stockData, interval, hyperTune=hyperTune, showStats=showStats)
        

        self.modelRepository.saveModel(modelDev, stockName, interval, version, "dev")
        self.modelRepository.saveModel(modelProd, stockName, interval, version, "production")



    def getFittingModel(self, stockName, interval):

        model = self.modelRepository.loadModel(stockName, interval, "production", "test")
        if model is None:
            print(f"No saved model found for stock {stockName}.")
            return None
        return model


    def containsModel(self, stockName, interval):

        return self.modelRepository.containsModel(stockName, interval, "dev", "test")


    def isModelUpdated(self, stockUpdateInfo):

        modelUpdateStr = self.modelRepository.getModelUpdateTime(
            stockUpdateInfo.stockName, 
            stockUpdateInfo.interval, 
            stage="dev", 
            version="test"
        )
        stockUpdateStr = stockUpdateInfo.latestUpdateTime

        if stockUpdateInfo.interval == "1d":
            dt_format = "%Y-%m-%d"
            modelUpdateTime = datetime.strptime(modelUpdateStr, dt_format).date()
            stockUpdateTime = datetime.strptime(stockUpdateStr, dt_format).date()
        elif stockUpdateInfo.interval == "1h":
            dt_format = "%Y-%m-%d %H"
            modelUpdateTime = datetime.strptime(modelUpdateStr, dt_format).replace(minute=0, second=0, microsecond=0)
            stockUpdateTime = datetime.strptime(stockUpdateStr, dt_format).replace(minute=0, second=0, microsecond=0)
        else:
            raise ValueError(f"Unbekanntes Interval: {stockUpdateInfo.interval}")

        return modelUpdateTime >= stockUpdateTime

