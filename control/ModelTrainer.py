import numpy as np


class ModelTrainer:

    def __init__(self):
        pass


    def trainModel(self, model, Xtrain, Ytrain):
        
        # Fit the model on the training data
        model.fit(Xtrain, Ytrain)

        return model

