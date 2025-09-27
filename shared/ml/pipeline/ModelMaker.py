from shared.ml.pipeline import DataPreparer
from shared.ml import ModelInfo
from shared.ml.pipeline import ModelTrainer
from shared.ml.pipeline import ModelEvaluator
from shared.ml.pipeline import HyperTuner
from shared.ml import Model
import logging

from xgboost import XGBRegressor
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

class ModelMaker:
    def __init__(self):

       self.modelTrainer = ModelTrainer.ModelTrainer()
       self.modelEvaluator = ModelEvaluator.ModelEvaluator()
       self.dataPreparer = DataPreparer.DataPreparer()
       self.hyperTuner = HyperTuner.HyperTuner()
       
       self.numberOfSamples = {
           "1d" : 365 * 2,
           "1h" : None #use all data
           }


    def createModel(self, data, interval, hyperTune=False, showStats=False):

        numSamples = self.numberOfSamples[interval]

        if numSamples is None:
            numSamples = data.shape[0]


        dataX, dataY = self.dataPreparer.prepareFeatures(data, numSampes=numSamples)
        Xtrain, Ytrain, Xtest, Ytest = self.dataPreparer.createSplit(dataX, dataY, self.modelTrainer.getSplit())


        #devModel
        hyperParams = self.getParams(hyperTune, Xtrain, Ytrain, Xtest, Ytest)
        modelDev = Model.Model(XGBRegressor(**hyperParams), MinMaxScaler())

 
        modelDev = self.modelTrainer.trainModel(modelDev, Xtrain, Ytrain)
        testCloses = data["Close"].iloc[-len(Xtest)-1:-1].values
        metrics = self.getMetrics(modelDev, Xtest, Ytest, testCloses, showStats)


        #prodModel
        modelProd = Model.Model(XGBRegressor(**hyperParams), MinMaxScaler())
        modelProd = self.modelTrainer.trainModel(modelProd, dataX, dataY)
        

        modelDev.addInfo(self.createInfo(data.index[-1],
                                      hyperParams, 
                                      metrics, 
                                      data.index[(len(data) - len(Xtest))-1], 
                                      numSamples))
        modelProd.addInfo(modelDev.info)

        return modelDev, modelProd






    #PRIVATE FUNCTION
    def getMetrics(self, model, Xtest, Ytest, testClose, showStats):
        metrics = None

        if showStats:
            metrics = self.modelEvaluator.evaluateModel(model, Xtest, Ytest, testClose, showPlot=True)
        else:
            metrics = self.modelEvaluator.evaluateModel(model, Xtest, Ytest, testClose, showPlot=False)

        return metrics


    #PRIVATE FUNCTION
    def getParams(self, hyperTune, Xtrain, Ytrain, Xtest, Ytest):
        if hyperTune:
            return self.hyperTuner.chooseParametersXGBOOST(Xtrain, Ytrain)
        else:
            return self.hyperTuner.getDefaultParams()


    #PRIVATE FUNCTION
    def createInfo(self, latestUpdate, hyperParams, metrics, latestTrain, numSamples):

        return ModelInfo.ModelInfo(
            latestUpdate=latestUpdate,
            trainUntil=latestTrain,
            metrics=metrics,
            features=self.dataPreparer.getFeaturesNames(),
            hyperParameters=hyperParams,
            numSamples = numSamples,
            trainTestSplit=self.modelTrainer.getSplit())
