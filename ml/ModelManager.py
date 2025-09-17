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
        self.model = self.modelMaker.createModel(stockData, interval, hyperTune=hyperTune, showStats=showStats)
        

        answer = input('should model be saved?:')        
        if answer.lower() in ['y', 'yes']:
            self.modelRepository.saveModel(self.model, stockName, interval, version, "dev")



    def getFittingModel(self, stockName, interval):

        model = self.modelRepository.loadModel(stockName, interval, "dev", "test")
        if model is None:
            print(f"No saved model found for stock {stockName}.")
            return None
        return model



    def isModelUpdated(self, stockUpdateInfo):
        return self.modelFiler.isModelUpdated(stockUpdateInfo.stockName, stockUpdateInfo.latestUpdateTime)

