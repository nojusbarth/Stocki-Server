from datetime import timedelta
from shared.ml.pipeline import DataPreparer
from shared.ml.prediction import PredictionDateMapper, PredictionPacket, RiskCalculator
from shared.ml import ModelManager

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from shared.data import StockManager

class Predictor():


    def __init__(self, modelManager, stockManager):
        self.dataPreparer = DataPreparer.DataPreparer()
        self.modelManager = modelManager
        self.stockManager = stockManager

        self.riskCalculator = RiskCalculator.RiskCalculator()
        self.dateMapper = PredictionDateMapper.PredictionDateMapper()
        self.model = None





    #WARNING XGBOOST AND HEURISTICS TO PREDICT NEXT DAY's DATA ARE ONLY RELIABE FOR 1-3 DAYS AHEAD
    def predict(self, stockName, period, interval, showPlot= False):
       
        stockData = self.stockManager.getStockData(stockName, interval)


        self.model = self.modelManager.getFittingModel(stockName, interval)

        if self.model is None:
            print("No fitting model found, cannot predict.")
            return None


        predictedReturns = self.doPrediction(stockData, period)

        lastClose = stockData["Close"].iloc[-1]
        
        predictedPrices = []
        currentPrice = lastClose

        for r in predictedReturns:
            currentPrice = currentPrice * (1 + r)
            predictedPrices.append(currentPrice)           
        
        predictedPrices = np.array(predictedPrices)


        if showPlot:
            self.showPlot(stockData, period, predictedPrices)

        return self.buildPackets(startDate = stockData.index[-1], returns=predictedReturns, closes=predictedPrices, interval=interval)


    
    #PRIVATE FUNCTION
    def doPrediction(self, stockData, period):

        predictedReturns = []

        # prediction requires 34 days of data to create features (32 needed for surviving nand, 1 because of shifting
        # (shifting only needed in training))
        # WARNING: Ensure that the last 34 days werent used in training!
        
        data = stockData.tail(34).copy()

        for i in range(period):

            #y not needed for prediction
            Xdata, _ = self.dataPreparer.prepareFeatures(data, 34)

            nextDayPred = self.model.predict(Xdata[-1].reshape(1, -1))[0]
            predictedReturns.append(nextDayPred)
            
            data = pd.concat([data, self.dataPreparer.createNextDayFeatures(data, nextDayPred)])

        return predictedReturns



    #PRIVATE FUNCTION
    def showPlot(self, stockData, days, predictedPrices):
        allData = stockData['Close'].copy()
        
        plt.plot(allData.index[-100:], allData.tail(100), label='Historical Prices')
        plt.plot(pd.date_range(allData.index[-1], periods=days), predictedPrices, linestyle='dashed', color='red', label='Future Predictions')
        plt.title(f"Stock Price Prediction for Next {days} Days using XGBoost")
        plt.xlabel('Date')
        plt.ylabel('Close Price (USD)')
        plt.legend()
        plt.show()

    #private
    def buildPackets(self, startDate, returns, closes, interval):


        predictionPackets = []

        for r, c in zip(returns, closes):
            packet = PredictionPacket.PredictionPacket(
                date=None,
                closePrediction=float(c),
                pctReturn=float(r * 100),  # in percent
                riskScore=self.riskCalculator.calculateRisk(self.model.info, c, len(predictionPackets) + 1, interval)
            )
            predictionPackets.append(packet)

        predictionPackets = self.dateMapper.mapPredictions(startDate=startDate, predictionPackets=predictionPackets, interval=interval)

        return predictionPackets