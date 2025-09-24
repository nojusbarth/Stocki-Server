from numpy.__config__ import show
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import matplotlib.pyplot as plt


class ModelEvaluator():

    def __init__(self):
        pass


    def evaluateModel(self, model, testX, testY, testCloses, showPlot=False):
        
        yPredRet = model.predict(testX)

        yTruePrice = testCloses * (1 + testY)
        yPredPrice = testCloses * (1 + yPredRet)

        rmse = np.sqrt(mean_squared_error(yTruePrice, yPredPrice))
        mae  = mean_absolute_error(yTruePrice, yPredPrice)
        r2   = r2_score(yTruePrice, yPredPrice)


        print(f"model evaluation results:")
        print("RMSE:", rmse)
        print("MAE:", mae)
        print("R squared:", r2)

        if showPlot:
            self.showPlot(yTruePrice, yPredPrice)

        return dict(RMSE=rmse, MAE=mae, R2=r2)


    #takes dollar predictions
    def showPlot(self,yValidPrice, yPredPrice):
        plt.figure(figsize=(12,6))
        plt.plot(yValidPrice, label="True Prices", color="blue")
        plt.plot(yPredPrice, label="Predicted Prices", color="red", linestyle="dashed")
        plt.title("XGBoost Predictions vs True Values (Test Set)")
        plt.xlabel("Days")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.show()