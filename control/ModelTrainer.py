import numpy as np

class ModelTrainer:

    def __init__(self):
        self.trainTestSplit = 0.8


    def trainModel(self, model, Xtrain, Ytrain):

        # Fit the model on the training data
        model.fit(Xtrain, Ytrain)

        return model


    def getSplit(self):
        return self.trainTestSplit

