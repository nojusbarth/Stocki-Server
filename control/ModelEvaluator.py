from numpy.__config__ import show
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import matplotlib.pyplot as plt


class ModelEvaluator():

    def __init__(self):
        pass


    def evaluateModel(self, model, testX, testY, showPlot=False):

        yPred = model.predict(testX)

        rmse = np.sqrt(mean_squared_error(testY, yPred))
        mae  = mean_absolute_error(testY, yPred)
        r2   = r2_score(testY, yPred)


        print(f"model evaluation results:")
        print("RMSE:", rmse)
        print("MAE:", mae)
        print("R squared:", r2)

        if showPlot:
            self.showPlot(testY, yPred)



    def showPlot(self,yValidPrice, yPredPrice):
        plt.figure(figsize=(12,6))
        plt.plot(yValidPrice, label="True Prices", color="blue")
        plt.plot(yPredPrice, label="Predicted Prices", color="red", linestyle="dashed")
        plt.title("XGBoost Predictions vs True Values (Test Set)")
        plt.xlabel("Days")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.show()