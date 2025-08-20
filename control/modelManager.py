import pandas as pd
from controller import DataPreparer, ModelTrainer, ModelEvaluator
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


        data = stock.getData()['Close'].copy()

        scaled_data = self.dataPreparer.prepareSamples(data, numLastSamples=365*2)

        trainTestSplit = 0.8
        timeStep = 20


        Xtrain, Ytrain, Xvalid, Yvalid = self.dataPreparer.createSplit(scaled_data, trainTestSplit, timeStep)

        # Initialize and train the XGBoost model
        xgb_model = XGBRegressor(objective ='reg:squarederror', colsample_bytree = 0.3, learning_rate = 0.1, max_depth = 5, alpha = 10, n_estimators = 100)

        xgb_model = self.modelTrainer.trainModel(xgb_model, Xtrain, Ytrain)
        
        # Predict future prices
        future_prices = []
        
        # Get the last 60 days of data
        last_60_days = scaled_data[-timeStep:].reshape(1, -1)
        
        for i in range(10):
            pred_price = xgb_model.predict(last_60_days)
            future_prices.append(pred_price[0])
            last_60_days = np.append(last_60_days, pred_price.reshape(1, -1), axis=1)[:, 1:]
        
        # Inverse transform the predicted prices
        future_prices = self.dataPreparer.inverseTransform(future_prices)


        plt.plot(data.index[-100:], data.tail(100), label='Historical Prices')
        plt.plot(pd.date_range(data.index[-1], periods=10), future_prices, linestyle='dashed', color='red', label='Future Predictions')
        plt.title('Stock Price Prediction for Next 10 Days using XGBoost')
        plt.xlabel('Date')
        plt.ylabel('Close Price (USD)')
        plt.legend()
        plt.show()

        self.modelEvaluator.evaluateModel(xgb_model, Xvalid, Yvalid, self.dataPreparer.scaler, showPlot=True)

        input("Press Enter to exit...")


