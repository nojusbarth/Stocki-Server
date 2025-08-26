from numpy.__config__ import show
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import matplotlib.pyplot as plt


class ModelEvaluator():

    def __init__(self):
        pass


    def evaluateModel(self, model, X_valid, y_valid, showPlot=False):

        yPred = model.predict(X_valid)

        rmse = np.sqrt(mean_squared_error(y_valid, yPred))
        mae  = mean_absolute_error(y_valid, yPred)
        r2   = r2_score(y_valid, yPred)


        print(f"model evaluation results:")
        print("RMSE:", rmse)
        print("MAE:", mae)
        print("R squared:", r2)

        if showPlot:
            self.showPlot(y_valid, yPred)



    def showPlot(self,yValidPrice, yPredPrice):
        plt.figure(figsize=(12,6))
        plt.plot(yValidPrice, label="True Prices", color="blue")
        plt.plot(yPredPrice, label="Predicted Prices", color="red", linestyle="dashed")
        plt.title("XGBoost Predictions vs True Values (Test Set)")
        plt.xlabel("Days")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.show()