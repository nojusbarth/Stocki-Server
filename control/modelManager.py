import pandas as pd
from control import DataPreparer, Model, ModelTrainer, ModelEvaluator, HyperTuner, ModelFiles
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
from pathlib import Path


class ModelManager():

    def __init__(self, stockManager):

        self.stockManager = stockManager
        self.dataPreparer = DataPreparer.DataPreparer()
        self.modelTrainer = ModelTrainer.ModelTrainer()
        self.modelEvaluator = ModelEvaluator.ModelEvaluator()
        self.hyperTuner = HyperTuner.HyperTuner()
        self.numberOfSamples = 365*2 #number of days used for model initally 
        self.model = None
        self.modelFiler = ModelFiles.ModelFiles(Path(r"C:\Users\nojob\Programmieren\Visual Studio\python\Stocki\project\predictionModels"))



    def createNewModel(self, stockName, modelName, hyperTune=False, showStats=False):

        if self.stockManager.getStock(stockName) is None:
            print(f"Stock {stockName} not found. Cannot create model.")
            return

        stock = self.stockManager.getStock(stockName)

        #fetch data

        data = stock.getData().copy()

        dataX, dataY = self.dataPreparer.prepareFeatures(data, numSampes=self.numberOfSamples)
        Xtrain, Ytrain, Xtest, Ytest = self.dataPreparer.createSplit(dataX, dataY, self.modelTrainer.getSplit())


        #create model

        if hyperTune:
            self.model = Model.Model(XGBRegressor(**self.hyperTuner.chooseParametersXGBOOST(Xtrain,Ytrain,Xtest,Ytest), showTest=False), MinMaxScaler())
        else:
            self.model = Model.Model(XGBRegressor(objective ='reg:squarederror', 
                                          colsample_bytree = 0.6203095920963915, 
                                          learning_rate = 0.05768766306891758, 
                                          max_depth = 10, n_estimators = 1941, 
                                          subsample = 0.9026219130291653, 
                                          random_state=42), MinMaxScaler())


        #train and test

        self.model = self.modelTrainer.trainModel(self.model, Xtrain, Ytrain)

        if showStats:
            self.modelEvaluator.evaluateModel(self.model, Xtest, Ytest, showPlot=True)


        #save model
    
        answer = input('should model be saved?:')
        
        if answer.lower() in ['y', 'yes']:
            self.modelFiler.saveModel(self.model, modelName)




    #WARNING XGBOOST AND HEURISTICS TO PREDICT NEXT DAY's DATA ARE ONLY RELIABE FOR 1-3 DAYS AHEAD
    def predict(self, days, showPlot= False):
        
        if self.model is None:
            self.model = self.modelFiler.loadModel("XGBOOSTV3")
            if self.model is None:
                print("No model loaded. Cannot predict.")
                return



        predictedPrices = []
        stock = self.stockManager.getStock("AAPL")

        # prediction requires 34 days of data to create features (32 needed for surviving nand, 1 because of shifting
        # (shifting only needed in training))
        # WARNING: Ensure that the last 34 days werent used in training!
        
        data = stock.getData().tail(34).copy()

        for i in range(days):

            #y not needed for prediction
            Xdata, _ = self.dataPreparer.prepareFeatures(data)            

            nextDayPred = self.model.predict(Xdata[-1].reshape(1, -1))[0]
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

