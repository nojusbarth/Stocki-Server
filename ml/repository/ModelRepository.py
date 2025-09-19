

from pathlib import Path
from ml.repository import ModelDB, ModelFiles


class ModelRepository:

    def __init__(self):

        self.rootPath = Path(r"C:\Users\nojob\Programmieren\Visual Studio\python\Stocki\project\predictionModels")

        self.modelFiler = ModelFiles.ModelFiles()
        self.modelDB = ModelDB.ModelDB()



    def saveModel(self, model, name, interval, version, stage):

        rootDirectory = self.findRootDirectory(name, interval, version, stage)
        
        paths = self.modelFiler.saveModel(model, rootDirectory)

        self.modelDB.registerModel(name,interval,version,stage,paths["model_path"], paths["scaler_path"], paths["info_path"])



    def loadModel(self, name, interval, stage, version):

        paths = self.modelDB.getModelPaths(name, interval, stage, version)

        model = self.modelFiler.loadModel(paths["model_path"], paths["scaler_path"], paths["info_path"])
        
        return model
        

    def getModelUpdateTime(self, name, interval, stage, version):

        paths = self.modelDB.getModelPaths(name, interval, stage, version)

        info = self.modelFiler.loadModelInfo(paths["info_path"])

        return info.latestUpdate


    def containsModel(self, name, interval, stage, version):

        return self.modelDB.containsModel(name, interval, stage, version)


    #PRIVATE FUNCTION
    def findRootDirectory(self, name, interval, version, stage):

        byName = self.rootPath / name
        byInterval = byName / interval
        byVersion = byInterval / version
        byStage = byVersion / stage

        return byStage

