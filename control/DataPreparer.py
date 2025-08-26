import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class DataPreparer():

    def __init__(self):
        self.scaler = MinMaxScaler()
        self.features = ["Open", "High", "Low", "Close", "Volume",
            "Return", "Volatility", "High_Low", "Close_Open",
            "SMA_10", "SMA_30", "Volume_Change"]


    #WARNING: data should be copied before passing to this function
    def prepareFeatures(self, data, numSampes=None):

        if numSampes is not None:
            data = data.tail(numSampes)

        data = data.copy() # only needed to prevent pandas warnings filling debug
        data["Return"] = data["Close"].pct_change(fill_method=None)
        data["Volatility"] = (data["High"] - data["Low"]) / data["Open"]
        data["High_Low"] = data["High"] - data["Low"]
        data["Close_Open"] = data["Close"] - data["Open"]
        data["SMA_10"] = data["Close"].rolling(10).mean()
        data["SMA_30"] = data["Close"].rolling(30).mean()
        data["Volume_Change"] = data["Volume"].pct_change(fill_method=None)

        data = data.dropna()

        X = data[self.features].values
        y = data["Close"].shift(-1).dropna().values #shift all values up by one row to predict next day's close price   

        X = X[:-1] #cut last line to match y length

        return X, y


    def scaleTranform(self, data, fit=False):
        if not fit:
            return self.scaler.transform(data)
        else:
            return self.scaler.fit_transform(data)


    def inverseTransform(self, data):
        return self.scaler.inverse_transform(np.array(data).reshape(-1, 1))




    def createSplit(self, X, y, trainTestSplit,):

        trainingWindow = int(len(X) * trainTestSplit)

        trainX = X[:trainingWindow]
        trainY = y[:trainingWindow]

        testX = X[trainingWindow:]
        testY = y[trainingWindow:]

        return trainX, trainY, testX, testY


    
    def createNextDayFeatures(self, lastData, closePrediction):


        nextDate = lastData.index[-1] + pd.Timedelta(days=1)

        newRow = pd.DataFrame(index=[nextDate], columns=lastData.columns)


        newRow['Close'] = closePrediction
        newRow['Adj Close'] = closePrediction


        #open equals previous close
        newRow['Open'] = lastData['Close'].iloc[-1]

        #high and low are heuristics based on previous day

        volatility_factor = np.random.uniform(0.005, 0.02)  # 0,5% bis 2% Schwankung
        newRow["High"] = closePrediction * (1 + volatility_factor)
        newRow["Low"] = closePrediction * (1 - volatility_factor)

        #volume is average of last 10 days with some noise
        avg_volume = lastData["Volume"].tail(10).mean()
        newRow["Volume"] = avg_volume * np.random.uniform(0.95, 1.05)

        newRow = newRow.reindex(columns=lastData.columns)
        return newRow

