from numpy.__config__ import show
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import matplotlib.pyplot as plt


class ModelEvaluator():

    def __init__(self):
        pass


    def evaluateModel(self, model, X_valid, y_valid, scaler, showPlot=False):

        yPred = model.predict(X_valid)

        yValidPrice = scaler.inverse_transform(y_valid.reshape(-1, 1))
        yPredPrice = scaler.inverse_transform(yPred.reshape(-1, 1))

        rmse = np.sqrt(mean_squared_error(yValidPrice, yPredPrice))
        mae  = mean_absolute_error(yValidPrice, yPredPrice)
        r2   = r2_score(yValidPrice, yPredPrice)


        print(f"model evaluation results:")
        print("RMSE:", rmse)
        print("MAE:", mae)
        print("R squared:", r2)

        if showPlot:
            self.showPlot(yValidPrice, yPredPrice)



    def showPlot(self,yValidPrice, yPredPrice):
        plt.figure(figsize=(12,6))
        plt.plot(yValidPrice, label="True Prices", color="blue")
        plt.plot(yPredPrice, label="Predicted Prices", color="red", linestyle="dashed")
        plt.title("XGBoost Predictions vs True Values (Test Set)")
        plt.xlabel("Days")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.show()