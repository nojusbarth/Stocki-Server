import numpy as np
import pandas as pd

class DataPreparer():

    def __init__(self):
        self.features = [
        "Return",
        "Volatility",
        "High_Low",
        "Close_Open",
        "SMA_10",
        "SMA_30",
        "Volume_Change",
        "Rolling_Vol_10",
        "Momentum_5",
        "Momentum_10"]

    def getFeaturesNames(self):
        return self.features

    #WARNING: data should be copied before passing to this function
    def prepareFeatures(self, data, numSampes):

        data = data.tail(numSampes)

        data = data.copy() # only needed to prevent pandas warnings filling debug
        data["Return"] = data["Close"].pct_change(fill_method=None)
        data["Volatility"] = (data["High"] - data["Low"]) / data["Open"]
        data["High_Low"] = data["High"] - data["Low"]
        data["Close_Open"] = data["Close"] - data["Open"]
        data["SMA_10"] = data["Close"].rolling(10).mean()
        data["SMA_30"] = data["Close"].rolling(30).mean()
        data["Volume_Change"] = data["Volume"].pct_change(fill_method=None)

        data["Rolling_Vol_10"] = data["Return"].rolling(10).std()
        data["Momentum_5"] = data["Close"].pct_change(periods=5)
        data["Momentum_10"] = data["Close"].pct_change(periods=10)

        data = data.dropna()

        X = data[self.features].values
        y = data["Return"].shift(-1).dropna().values #shift all values up by one row to predict next day's target

        X = X[:-1] #cut last line to match y length

        return X, y


    def createSplit(self, X, y, trainTestSplit):
        trainingWindow = int(len(X) * trainTestSplit)

        trainX = X[:trainingWindow]
        trainY = y[:trainingWindow]

        testX = X[trainingWindow:]
        testY = y[trainingWindow:]

        return trainX, trainY, testX, testY


    
    def createNextDayFeatures(self, lastData, predictedReturn):

        nextDate = lastData.index[-1] + pd.Timedelta(days=1)

        newRow = pd.DataFrame(index=[nextDate], columns=lastData.columns)

        prevClose = lastData["Close"].iloc[-1]
        nextClose = prevClose * (1 + predictedReturn)

        newRow['Close'] = nextClose

        #open equals previous close
        newRow['Open'] = prevClose

        #high and low are heuristics based on previous day

        volatility_factor = np.random.uniform(0.005, 0.02)
        newRow["High"] = nextClose * (1 + volatility_factor)
        newRow["Low"] = nextClose * (1 - volatility_factor)

        #volume is average of last 10 days with some noise
        avg_volume = lastData["Volume"].tail(10).mean()
        newRow["Volume"] = avg_volume * np.random.uniform(0.95, 1.05)

        newRow = newRow.reindex(columns=lastData.columns)
        return newRow

