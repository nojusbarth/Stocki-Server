#hyperparameter tuning module

import optuna
import numpy as np
from ml.pipeline import ModelEvaluator
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_squared_error

class HyperTuner:

    def __init__(self):

        self.validSplit = 0.05
        self.trainingDataX = None
        self.trainingDataY = None

        self.defaultParams = {"objective" : 'reg:squarederror', 
                                          "colsample_bytree" : 0.6203095920963915, 
                                          "learning_rate" : 0.05768766306891758, 
                                          "max_depth" : 10, "n_estimators" : 1941, 
                                          "subsample" : 0.9026219130291653, 
                                          "random_state" : 42}

    
    def chooseParametersXGBOOST(self, trainingDataX, trainingDataY):

        self.trainingDataX = trainingDataX
        self.trainingDataY = trainingDataY

        print("Starting hyperparameter tuning with early stopping...")
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(direction="minimize")
        study.optimize(self.objective, n_trials=100)

        # Beste Parameter
        print("Beste Parameter:", study.best_params)
        print("Best RMSE:", study.best_value)
               

        return study.best_params


    def getDefaultParams(self):
        return self.defaultParams



    def objective(self,trial):

        param = {
            "objective": "reg:squarederror",
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "n_estimators": trial.suggest_int("n_estimators", 100, 2000),
            "eval_metric": "rmse"
        }

        rmses = []

        n_train = len(self.trainingDataX)
        validSize = int(n_train * self.validSplit)
        step = validSize

        for end in range(validSize, n_train, step):
            X_tr = self.trainingDataX[:end]
            X_val = self.trainingDataX[end:end+validSize]
            y_tr = self.trainingDataY[:end]
            y_val = self.trainingDataY[end:end+validSize]
        
            if len(X_val) < validSize:
                break  #skip last window if not enough data
        
            model = XGBRegressor(**param, early_stopping_rounds=10, random_state=42)
            model.fit(
                X_tr, y_tr,
                eval_set=[(X_val, y_val)],
                verbose=False
            )
        
            preds = model.predict(X_val)
            rmse = np.sqrt(mean_squared_error(y_val, preds))
            rmses.append(rmse)
        
        weights = np.linspace(0.5, 1.0, len(rmses))
        mean_weighted_rmse = np.average(rmses, weights=weights)

        return mean_weighted_rmse
