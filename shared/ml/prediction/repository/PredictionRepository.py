
from shared.ml.prediction import PredictionPacket
import shared.ml.prediction.repository.PredictionDB as PredictionDB
import threading
import queue

class PredictionRepository:

    def __init__(self, predictor, predictionQueue):
        self.predictionsDB = PredictionDB.PredictionDB()
        self.predictor = predictor
        self.predictionQueue = predictionQueue
        self.chacheLock = threading.Lock()
        self.timeOutQueue=0.5


        self.currentPredictionsHour = self.predictionsDB.loadAllCurrent("1h")
        self.currentPredictionsDay = self.predictionsDB.loadAllCurrent("1d")


    def getAllLatestPredictions(self, stockNames, interval):
            allPredictions = {}
            for stockName in stockNames:
                allPredictions[stockName] = self.getLatestPrediction(stockName, interval)[0]
            return allPredictions

    def getLatestPrediction(self, stockName, interval):

        currentPredictions = self.currentPredictionsHour if interval == "1h" else self.currentPredictionsDay

        if stockName in currentPredictions:
            stepDict = currentPredictions[stockName]
            prediction_list = [stepDict[step] for step in sorted(stepDict.keys())]
            return prediction_list
        else:
            predictions = self.predictor.predict(stockName, 3, interval)
            self.predictionsDB.savePrediction(stockName, interval, predictions)
        
            with self.chacheLock:
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
                step_list.append(date_to_step_preds.get(date.isoformat(), {}).get(step, None))
            historical[date.isoformat()] = step_list
    
        return historical



    def updatePredictionLoop(self):
        while True:
            try:
                stockInfo = self.predictionQueue.get(timeout=self.timeOutQueue)
                interval = stockInfo.interval
                stockName = stockInfo.stockName

                print(f"Updating predictions for {stockName} ({interval})", flush=True)

                table_cache = self.currentPredictionsHour if interval == "1h" else self.currentPredictionsDay

                predictionPacketList = self.predictor.predict(stockName, 3, interval)

                self.predictionsDB.savePrediction(stockName, interval, predictionPacketList)

                step_dict = {i + 1: pkt for i, pkt in enumerate(predictionPacketList)}

                with self.chacheLock:
                    table_cache[stockName] = step_dict
            except queue.Empty:
                continue
