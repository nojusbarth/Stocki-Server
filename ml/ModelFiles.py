from xgboost import XGBRegressor
import os
from ml.model_core import Model
from ml.model_core import ModelInfo
from joblib import dump, load
import json
from dataclasses import asdict
from datetime import datetime

class ModelFiles:

    def __init__(self, filepath):
        self.filePath = filepath



    def loadModel(self, stockName):

        model = XGBRegressor()

        print(f"Loading model for {stockName} from {self.filePath}:")

        try:
            modelPath = os.path.join(self.filePath, stockName, f"{stockName}_pred.json")
            model.load_model(modelPath)

        except Exception as e:
            print(f"Error loading model for {stockName}: {e}")
            return None


        print(f"Model for {stockName} loaded successfully.")


        scaler = None
        #load scaler
        try:
            scalerPath = os.path.join(self.filePath, stockName, f"{stockName}_scaler.joblib")            
            scaler = load(scalerPath)
        except:
            print(f"Error loading scaler for model {stockName}")
            return None


        #load info 
        info = None
        try:
            infoPath = os.path.join(self.filePath, stockName, f"{stockName}_info.json")
            with open(infoPath, 'r') as f:
                infoDict = json.load(f)
                info = ModelInfo.ModelInfo(**infoDict)
        except Exception as e:
            print(f"Error loading info for model {stockName}: {e}")
            return None

        loadedModel = Model.Model(model, scaler)
        loadedModel.addInfo(info)

        return loadedModel



    def saveModel(self, model, stockName):

        modelDir = os.path.join(self.filePath, stockName)
        print(f"Saving model to {modelDir}:")

        if not os.path.exists(modelDir):
            os.makedirs(modelDir)

        #save model
        try:
            model.getModel().save_model(os.path.join(modelDir, f"{stockName}_pred.json"))
        except Exception as e:
            print(f"Error saving model {stockName}: {e}")
            return
        

        #save scaler
        try:
            dump(model.getScaler(), os.path.join(modelDir, f"{stockName}_scaler.joblib"))
        except Exception as e:
            print(f"Error saving scaler for model {stockName}: {e}")
            return

        #save info

        try:
            infoPath = os.path.join(modelDir, f"{stockName}_info.json")
            with open(infoPath, 'w') as f:
                json.dump(asdict(model.getInfo()), f, indent=4)
        except Exception as e:
            print(f"Error saving info for model {stockName}: {e}")
            return


        print(f"Model {stockName} saved successfully.")



    def isModelUpdated(self, modelName, latestStockUpdate):
        model = self.loadModel(modelName)
        if model is None:
            print(f"No saved model found for stock {modelName}.")
            return False
        modelInfo = model.getInfo()

        if modelInfo is None:
            print(f"Model info for {modelName} is missing.")
            return False
        if datetime.strptime(modelInfo.latestUpdate, "%Y-%m-%d") >= datetime.strptime(latestStockUpdate, "%Y-%m-%d"):
            print(f"Model for {modelName} is up to date.")
            return True
        else:
            print(f"Model for {modelName} is outdated.")
            return False