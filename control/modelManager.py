import pandas as pd
from control import DataPreparer, ModelTrainer, ModelEvaluator
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error


class ModelManager():

    def __init__(self, stockManager):

        self.stockManager = stockManager
        self.dataPreparer = DataPreparer.DataPreparer()
        self.modelTrainer = ModelTrainer.ModelTrainer()
        self.modelEvaluator = ModelEvaluator.ModelEvaluator()

        stock = stockManager.getStock("AAPL")


        data = stock.getData().copy()

        dataX, dataY = self.dataPreparer.prepareFeatures(data, numSampes=365*2)
        dataX = self.dataPreparer.scaleTranform(dataX, fit=True)
        trainTestSplit = 0.8


        Xtrain, Ytrain, Xtest, Ytest = self.dataPreparer.createSplit(dataX, dataY, trainTestSplit)

        # Initialize and train the XGBoost model
        self.xgb_model = XGBRegressor(objective ='reg:squarederror', colsample_bytree = 0.3, learning_rate = 0.1, max_depth = 5, n_estimators = 200)

        self.xgb_model = self.modelTrainer.trainModel(self.xgb_model, Xtrain, Ytrain)
        

        #self.modelEvaluator.evaluateModel(self.xgb_model, Xtest, Ytest, showPlot=True)


    #WARNING XGBOOST AND HEURISTICS TO PREDICT NEXT DAY's DATA ARE ONLY RELIABE FOR 1-3 DAYS AHEAD
    def predict(self, days, showPlot= False):
        
        predictedPrices = []
        stock = self.stockManager.getStock("AAPL")

        # prediction requires 34 days of data to create features (32 needed for surviving nand, 1 because of shifting
        # (shifting only needed in training))
        # WARNING: Ensure that the last 34 days werent used in training!
        
        data = stock.getData().tail(34).copy()

        for i in range(days):

            #y not needed for prediction
            Xdata, _ = self.dataPreparer.prepareFeatures(data)
            Xdata = self.dataPreparer.scaleTranform(Xdata)
            

            nextDayPred = self.xgb_model.predict(Xdata[-1].reshape(1, -1))[0]
            predictedPrices.append(nextDayPred)
            
            data = pd.concat([data, self.dataPreparer.createNextDayFeatures(data, nextDayPred)])

        if showPlot:

            allData = stock.getData()['Close'].copy()

            plt.plot(allData.index[-100:], allData.tail(100), label='Historical Prices')
            plt.plot(pd.date_range(allData.index[-1], periods=days), predictedPrices, linestyle='dashed', color='red', label='Future Predictions')
            plt.title(f"Stock Price Prediction for Next {days} Days using XGBoost")
            plt.xlabel('Date')
            plt.ylabel('Close Price (USD)')
            plt.legend()
            plt.show()

        return predictedPrices

