
from re import S
from ml.prediction import AccuracyPacket
import pandas as pd

class AccuracyPackager:
    def __init__(self, stockManager, predictionRepository):
        self.stockManager = stockManager
        self.predictionRepository = predictionRepository



    def buildPackets(self, stockName, interval, num):
    
        stockData = self.stockManager.getStockData(stockName, interval).tail(num)
    
        dates = stockData.index.tolist()
    
        predictionMap = self.predictionRepository.getHistoricalPredictions(
            stockName, interval, dates, steps=[1, 2, 3]
        )
    
        packetsByDate = {}
        datesStr = [date.isoformat() for date in dates]

        for i, date_str in enumerate(datesStr):
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

