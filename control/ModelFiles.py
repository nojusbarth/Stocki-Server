from xgboost import XGBRegressor
import os
from control import Model
from joblib import dump, load

class ModelFiles:

    def __init__(self, filepath):
        self.filePath = filepath



    def loadModel(self, modelName):

        loaded_model = XGBRegressor()

        print(f"Loading model from {self.filePath}:")

        try:
            loaded_model.load_model(os.path.join(self.filePath, f"{modelName}.json"))
        except Exception as e:
            print(f"Error loading model {modelName}: {e}")
            return None


        print(f"Model {modelName} loaded successfully.")


        scaler = None
        #load scaler
        try:
            scaler = load(os.path.join(self.filePath, f"{modelName}_scaler.joblib"))
        except:
            print(f"Error loading scaler for model {modelName}")
            return None


        return Model.Model(loaded_model, scaler)


    def saveModel(self, model, modelName):
        print(f"Saving model to {self.filePath}:")
        try:
            model.getModel().save_model(os.path.join(self.filePath, f"{modelName}.json"))
        except Exception as e:
            print(f"Error saving model {modelName}: {e}")
            return
        
        #save scaler

        try:
            dump(model.getScaler(), os.path.join(self.filePath, f"{modelName}_scaler.joblib"))
        except Exception as e:
            print(f"Error saving scaler for model {modelName}: {e}")
            return

        print(f"Model {modelName} saved successfully.")