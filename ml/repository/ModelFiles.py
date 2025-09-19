from xgboost import XGBRegressor
import os
from ml import Model
from ml import ModelInfo
from joblib import dump, load
import json
from dataclasses import asdict
from datetime import datetime

class ModelFiles:

    def loadModel(self, modelPath, scalerPath, infoPath):
        model = XGBRegressor()

        print(f"Loading model from {modelPath}:")

        try:
            model.load_model(modelPath)

        except Exception as e:
            print(f"Error loading model from {modelPath}: {e}")
            return None


        print(f"Model from {modelPath} loaded successfully.")


        scaler = None
        #load scaler
        try:
            scaler = load(scalerPath)
        except:
            print(f"Error loading scaler for model {scalerPath}")
            return None



        loadedModel = Model.Model(model, scaler)
        loadedModel.addInfo(self.loadModelInfo(infoPath))

        return loadedModel


    def loadModelInfo(self, infoPath):

        #load info 
        info = None
        try:
            with open(infoPath, 'r') as f:
                infoDict = json.load(f)
                info = ModelInfo.ModelInfo(**infoDict)
        except Exception as e:
            print(f"Error loading info for model {infoPath}: {e}")
            return None

        return info




    def saveModel(self, model, rootDirectory):

        rootDirectory.mkdir(parents=True, exist_ok=True)
        print(f"Saving model to {rootDirectory}:")

        modelPath = os.path.join(rootDirectory, "model_pred.json")
        scalerPath = os.path.join(rootDirectory, "model_scaler.joblib")
        infoPath = os.path.join(rootDirectory, "model_info.json")

        #save model
        try:
            model.getModel().save_model(modelPath)
        except Exception as e:
            print(f"Error saving model: {e}")
            return None
        
        #save scaler
        try:
            dump(model.getScaler(),scalerPath)
        except Exception as e:
            print(f"Error saving scaler: {e}")
            return None

        #save info
        try:
            with open(infoPath, 'w') as f:
                json.dump(asdict(model.getInfo()), f, indent=4)
        except Exception as e:
            print(f"Error saving info: {e}")
            return None

        print(f"Model saved successfully to {rootDirectory}.")

        return {
            "model_path": modelPath,
            "scaler_path": scalerPath,
            "info_path": infoPath
        }



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