#hyperparameter tuning module

import optuna
import numpy as np
from control import ModelEvaluator
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_squared_error

class HyperTuner:

    def __init__(self):

        self.validSplit = 0.95 #meaning only 1 - ..% of training data is used for validation
        self.trainingDataX = None
        self.trainingDataY = None
        self.validDataX = None
        self.validDataY = None
        self.nSplits = 3


    
    def chooseParametersXGBOOST(self, trainingDataX, trainingDataY, testDataX, testDataY, showTest=False):

        self.trainingDataX = trainingDataX
        self.trainingDataY = trainingDataY

        print("Starting hyperparameter tuning with early stopping...")

        study = optuna.create_study(direction="minimize")
        study.optimize(self.objective, n_trials=100)

        # Beste Parameter
        print("Beste Parameter:", study.best_params)
        print("Best RMSE:", study.best_value)
               
        if showTest:
            #evaluate model on test data

            bestModel = XGBRegressor(**study.best_params)

            bestModel.fit(self.trainingDataX, self.trainingDataY)

            modelEvaluator = ModelEvaluator.ModelEvaluator()

            modelEvaluator.evaluateModel(bestModel, testDataX, testDataY, showPlot=True)

        return study.best_params


    def objective(self,trial):

        param = {
            "objective": "reg:squarederror",
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "n_estimators": trial.suggest_int("n_estimators", 100, 2000)
        }


        tscv = TimeSeriesSplit(n_splits=self.nSplits)
        rmses = []

        for train_idx, valid_idx in tscv.split(self.trainingDataX):
            X_train, X_valid = self.trainingDataX[train_idx], self.trainingDataX[valid_idx]
            y_train, y_valid = self.trainingDataY[train_idx], self.trainingDataY[valid_idx]

            model = XGBRegressor(**param, early_stopping_rounds=10, random_state=42)
            model.fit(
                X_train, y_train,
                eval_set=[(X_valid, y_valid)],
                verbose=False
            )

            preds = model.predict(X_valid)
            mse = mean_squared_error(y_valid, preds)
            rmse = np.sqrt(mse)
            rmses.append(rmse)

        return np.mean(rmses)
