from xgboost import XGBRegressor
import os
from shared.ml import Model
from shared.ml import ModelInfo
from joblib import dump, load
import json
from dataclasses import asdict
from datetime import datetime, timezone

class ModelFiles:

    def loadModel(self, modelPath, scalerPath, infoPath):
        model = XGBRegressor()


        try:
            model.load_model(modelPath)

        except Exception as e:
            print(f"Error loading model from {modelPath}: {e}")
            return None



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

                # JSON can't save datetime objects, so we need to convert them back
                infoDict['latestUpdate'] = datetime.fromisoformat(infoDict['latestUpdate']).replace(tzinfo=timezone.utc)
                infoDict['trainUntil'] = datetime.fromisoformat(infoDict['trainUntil']).replace(tzinfo=timezone.utc)

                info = ModelInfo.ModelInfo(**infoDict)
                return info
        except Exception as e:
            print(f"Error loading info for model {infoPath}: {e}")
            return None





    def saveModel(self, model, rootDirectory):

        rootDirectory.mkdir(parents=True, exist_ok=True)

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
                json.dump(model.getInfo().toDict(), f, indent=4)
        except Exception as e:
            print(f"Error saving info: {e}")
            return None


        return {
            "model_path": modelPath,
            "scaler_path": scalerPath,
            "info_path": infoPath
        }