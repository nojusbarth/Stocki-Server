from control import DataPreparer
from control.model_core import ModelInfo
from control.model_core import ModelTrainer
from control.model_core import ModelEvaluator
from control.model_core import HyperTuner
from control.model_core import Model


from xgboost import XGBRegressor
from sklearn.preprocessing import MinMaxScaler
from datetime import date

class ModelMaker:
    def __init__(self):
       self.modelTrainer = ModelTrainer.ModelTrainer()
       self.modelEvaluator = ModelEvaluator.ModelEvaluator()
       self.dataPreparer = DataPreparer.DataPreparer()
       self.hyperTuner = HyperTuner.HyperTuner()
       self.numberOfSamples = 365*2


    def createModel(self, data, hyperTune=False, showStats=False):

        dataX, dataY = self.dataPreparer.prepareFeatures(data, numSampes=self.numberOfSamples)
        Xtrain, Ytrain, Xtest, Ytest = self.dataPreparer.createSplit(dataX, dataY, self.modelTrainer.getSplit())

        #create model
        hyperParams = self.getParams(hyperTune, Xtrain, Ytrain, Xtest, Ytest)

        model = Model.Model(XGBRegressor(**hyperParams), MinMaxScaler())


        #train
        model = self.modelTrainer.trainModel(model, Xtrain, Ytrain)
        latestTrain = data.index[(len(data) - len(Xtest))-1].strftime("%Y-%m-%d")

        metrics = self.getMetrics(model, Xtest, Ytest, showStats)

        model.addInfo(self.createInfo(hyperParams, metrics, latestTrain))

        return model



    #PRIVATE FUNCTION
    def getMetrics(self, model, Xtest, Ytest, showStats):
        metrics = None

        if showStats:
            metrics = self.modelEvaluator.evaluateModel(model, Xtest, Ytest, showPlot=True)
        else:
            metrics = self.modelEvaluator.evaluateModel(model, Xtest, Ytest, showPlot=False)

        return metrics


    #PRIVATE FUNCTION
    def getParams(self, hyperTune, Xtrain, Ytrain, Xtest, Ytest):
        if hyperTune:
            return self.hyperTuner.chooseParametersXGBOOST(Xtrain, Ytrain, Xtest, Ytest)
        else:
            return self.hyperTuner.getDefaultParams()


    #PRIVATE FUNCTION
    def createInfo(self, hyperParams,  metrics, latestTrain):

        return ModelInfo.ModelInfo(
            latestUpdate=date.today().strftime("%Y-%m-%d"),
            trainUntil=latestTrain,
            metrics=metrics,
            features=self.dataPreparer.getFeaturesNames(),
            hyperParameters=hyperParams,
            numSamples = self.numberOfSamples,
            trainTestSplit=self.modelTrainer.getSplit())
