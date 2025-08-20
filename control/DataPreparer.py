import numpy as np
from sklearn.preprocessing import MinMaxScaler

class DataPreparer():

    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    

    def prepareSamples(self, data, numLastSamples):

        data = data.tail(numLastSamples).to_numpy()

        # Scale the data
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))

        return scaled_data


    def inverseTransform(self, data):
        # Inverse transform the scaled data
        return self.scaler.inverse_transform(np.array(data).reshape(-1, 1))


    def createDataset(self, data, time_step):
        X, y = [], []
        for i in range(len(data) - time_step - 1):
            X.append(data[i:(i + time_step), 0])
            y.append(data[i + time_step, 0])
        return np.array(X), np.array(y)


    def createSplit(self, data, trainTestSplit, timeStep):
        # Split the data into training and validation sets
        training_data_len = int(len(data) * trainTestSplit)
        train_data = data[:training_data_len]
        valid_data = data[training_data_len:]

        X_train, y_train = self.createDataset(train_data, timeStep)
        X_valid, y_valid = self.createDataset(valid_data, timeStep)

        return X_train, y_train, X_valid, y_valid
