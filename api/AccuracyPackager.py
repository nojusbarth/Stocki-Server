
from re import S
from ml.prediction import AccuracyPacket
import pandas as pd

class AccuracyPackager:
    def __init__(self, stockManager, predictionRepository):
        self.stockManager = stockManager
        self.predictionRepository = predictionRepository



    def buildPackets(self, stockName, interval, num):
    
        stockData = self.stockManager.getStockData(stockName, interval).tail(num)
    
        if interval == "1d":
            dates = [pd.to_datetime(d).strftime("%Y-%m-%d") for d in stockData.index]
        else:
            dates = [pd.to_datetime(d).strftime("%Y-%m-%d-%H") for d in stockData.index]
    
        predictionMap = self.predictionRepository.getHistoricalPredictions(
            stockName, interval, dates, steps=[1, 2, 3]
        )
    
        packetsByDate = {}
    
        for i, date_str in enumerate(dates):
            stepPackets = []
            preds_for_date = predictionMap.get(date_str, [])
            actualClose = stockData.iloc[i]['Close']
    
            for pkt in preds_for_date:
                if pkt is None:
                    stepPackets.append(None)
                else:
                    accPkt = AccuracyPacket.AccuracyPacket(
                        closePrediction=pkt.closePrediction,
                        pctReturnPrediction=pkt.pctReturn,
                        actualClose=actualClose,
                        riskPrediction=pkt.riskScore
                    )
                    stepPackets.append(accPkt)
    
            packetsByDate[date_str] = stepPackets

        return packetsByDate

