from ml.pipeline import DataPreparer
from ml import ModelInfo
from ml.pipeline import ModelTrainer
from ml.pipeline import ModelEvaluator
from ml.pipeline import HyperTuner
from ml import Model


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

        dateFormat = "%Y-%m-%d" if interval == "1d" else "%Y-%m-%d %H"

        numSamples = self.numberOfSamples[interval]

        if numSamples is None:
            numSamples = data.shape[0]


        dataX, dataY = self.dataPreparer.prepareFeatures(data, numSampes=numSamples)

        Xtrain, Ytrain, Xtest, Ytest = self.dataPreparer.createSplit(dataX, dataY, self.modelTrainer.getSplit())

        #create model
        hyperParams = self.getParams(hyperTune, Xtrain, Ytrain, Xtest, Ytest)

        model = Model.Model(XGBRegressor(**hyperParams), MinMaxScaler())


        #train
        model = self.modelTrainer.trainModel(model, Xtrain, Ytrain)


        latestTrain = data.index[(len(data) - len(Xtest))-1].strftime(dateFormat)
        latestSeen = data.index[-1].strftime(dateFormat)

        testCloses = data["Close"].iloc[-len(Xtest)-1:-1].values

        metrics = self.getMetrics(model, Xtest, Ytest, testCloses, showStats)

        model.addInfo(self.createInfo(latestSeen,hyperParams, metrics, latestTrain, numSamples))

        return model



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
            return self.hyperTuner.chooseParametersXGBOOST(Xtrain, Ytrain, Xtest, Ytest)
        else:
            return self.hyperTuner.getDefaultParams()


    #PRIVATE FUNCTION
    def createInfo(self, latestUpdate,hyperParams,  metrics, latestTrain, numSamples):

        return ModelInfo.ModelInfo(
            latestUpdate=latestUpdate,
            trainUntil=latestTrain,
            metrics=metrics,
            features=self.dataPreparer.getFeaturesNames(),
            hyperParameters=hyperParams,
            numSamples = numSamples,
            trainTestSplit=self.modelTrainer.getSplit())
