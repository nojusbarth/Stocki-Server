
from ml.prediction import PredictionPacket
import ml.prediction.repository.PredictionDB as PredictionDB
import threading

class PredictionRepository:

    def __init__(self, predictor):
        self.predictionsDB = PredictionDB.PredictionDB()
        self.predictor = predictor
        self.lock = threading.Lock()


        self.currentPredictionsHour = self.predictionsDB.loadAllCurrent("1h")
        self.currentPredictionsDay = self.predictionsDB.loadAllCurrent("1d")


    def getAllLatestPredictions(self, stockNames, interval):
            allPredictions = {}
            for stockName in stockNames:
                allPredictions[stockName] = self.getLatestPrediction(stockName, interval)[0]
            return allPredictions

    def getLatestPrediction(self, stockName, interval):

        currentPredictions = self.currentPredictionsHour if interval == "1h" else self.currentPredictionsDay
        with self.lock:
            if stockName in currentPredictions:
                stepDict = currentPredictions[stockName]
                prediction_list = [stepDict[step] for step in sorted(stepDict.keys())]
                return prediction_list
            else:
                predictions = self.predictor.predict(stockName, 3, interval)
                self.predictionsDB.savePrediction(stockName, interval, predictions)

                if interval == "1h":
                    self.currentPredictionsHour[stockName] = {i+1: pred for i, pred in enumerate(predictions)}
                else:
                    self.currentPredictionsDay[stockName] = {i+1: pred for i, pred in enumerate(predictions)}

                return predictions

    def getHistoricalPredictions(self, stockName, interval, dates, steps=[1, 2, 3]):
        historical = {}
    
        date_to_step_preds = {}
        for step in steps:
            preds = self.predictionsDB.loadPredictionForDates(stockName, dates, interval, step)
            for date, pkt in preds.items():
                if date not in date_to_step_preds:
                    date_to_step_preds[date] = {}
                date_to_step_preds[date][step] = pkt
    
        for date in dates:
            step_list = []
            for step in steps:
                step_list.append(date_to_step_preds.get(date, {}).get(step, None))
            historical[date] = step_list
    
        return historical



    def updatePrediction(self, stockName, interval):

        table_cache = self.currentPredictionsHour if interval == "1h" else self.currentPredictionsDay

        with self.lock:
            
            predictionPacketList = self.predictor.predict(stockName, 3, interval)

            self.predictionsDB.savePrediction(stockName, interval, predictionPacketList)

            step_dict = {i + 1: pkt for i, pkt in enumerate(predictionPacketList)}
            table_cache[stockName] = step_dict