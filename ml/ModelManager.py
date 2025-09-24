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
import logging
import threading

class ModelManager:

    def __init__(self):
        self.modelRepository = ModelRepository.ModelRepository()
        self.modelMaker = ModelMaker.ModelMaker()
        self.logger = logging.getLogger("model")



    def createNewModel(self, stockName, stockData, interval, version, hyperTune=False, showStats=False):
        
        #model pipeline
        modelDev, modelProd = self.modelMaker.createModel(stockData, interval, hyperTune=hyperTune, showStats=showStats)
        
        self.logger.info({
            "event": "model_creation_finished",
            "message": f"Creation of Model {stockName} finished",
            "model_name": stockName,
            "interval": interval,
            "metrics": modelDev.getInfo().metrics,
            "hyperparameters": modelDev.getInfo().hyperParameters,
            "thread": threading.current_thread().name
        })

        self.modelRepository.saveModel(modelDev, stockName, interval, version, "dev")
        self.modelRepository.saveModel(modelProd, stockName, interval, version, "production")



    def getFittingModel(self, stockName, interval):

        model = self.modelRepository.loadModel(stockName, interval, "production", "test")
        if model is None:
            self.logger.info({
                "event": "model_miss",
                "message": f"no fitting model for {stockName} found",
                "model_name": stockName,
                "interval": interval,
                "thread": threading.current_thread().name
            })
            return None
        return model


    def containsModel(self, stockName, interval):

        return self.modelRepository.containsModel(stockName, interval, "dev", "test")

    def getModelInfo(self, stockName, interval):
        return self.modelRepository.loadModel(stockName, interval, "dev", "test").info

    def isModelUpdated(self, stockUpdateInfo):

        modelUpdateTime = self.modelRepository.getModelUpdateTime(
            stockUpdateInfo.stockName, 
            stockUpdateInfo.interval, 
            stage="dev", 
            version="test"
        )

        return modelUpdateTime >= stockUpdateInfo.latestUpdateTime

