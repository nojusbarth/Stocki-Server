import pandas as pd
import os
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

from ml.prediction import PredictionPacket


class PredictionDB:

    def __init__(self):
        load_dotenv()        
        
        self.conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DBPREDICTIONS")
        )

        self.cursor = self.conn.cursor(dictionary=True)


    def savePrediction(self, stockName, interval, predictionPacketList):
        table = self.getTableName(interval)
        query = f"""
        INSERT INTO {table} (ticker, date, step, pctReturn, closePrediction, riskScore)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            pctReturn = VALUES(pctReturn),
            closePrediction = VALUES(closePrediction),
            riskScore = VALUES(riskScore)
        """
    
        try:
            for i, predictionPacket in enumerate(predictionPacketList):
                step = i + 1
                values = (
                    stockName.upper(),
                    predictionPacket.date,
                    step,
                    predictionPacket.pctReturn,
                    predictionPacket.closePrediction,
                    predictionPacket.riskScore
                )
                self.cursor.execute(query, values)
    
            self.conn.commit()
    
        except Error as e:
            print(f"Error saving predictions for {stockName}: {e}")
    
    
    def loadPredictionForDates(self, stockName, dates, interval, step):
        table = self.getTableName(interval)
        result = {}
    
        for date in dates:
            query = f"""
            SELECT pctReturn, closePrediction, riskScore
            FROM {table}
            WHERE ticker=%s AND date=%s AND step=%s
            """
            try:
                self.cursor.execute(query, (stockName.upper(), date, step))
                row = self.cursor.fetchone()
    
                if row:
                    pkt = PredictionPacket.PredictionPacket(
                        date=date,
                        pctReturn=row['pctReturn'],
                        closePrediction=row['closePrediction'],
                        riskScore=row['riskScore']
                    )
                    result[date] = pkt
                else:
                    result[date] = None
    
            except Error as e:
                print(f"Error loading prediction for {stockName} on {date}: {e}")
                result[date] = None
    
        return result
    

    
    
    def loadAllCurrent(self, interval, steps=[1, 2, 3]):
        table = self.getTableName(interval)
        resultCache = {}
    
        try:
            self.cursor.execute(f"SELECT DISTINCT ticker FROM {table}")
            tickers = [row['ticker'] for row in self.cursor.fetchall()]
    
            for ticker in tickers:
                resultCache[ticker] = {}
    
                for step in steps:
                    query = f"""
                    SELECT date, pctReturn, closePrediction, riskScore
                    FROM {table}
                    WHERE ticker=%s AND step=%s
                    ORDER BY date DESC
                    LIMIT 1
                    """
                    self.cursor.execute(query, (ticker, step))
                    row = self.cursor.fetchone()
                    if row:
                        pkt = PredictionPacket.PredictionPacket(
                            date=row['date'],
                            pctReturn=row['pctReturn'],
                            closePrediction=row['closePrediction'],
                            riskScore=row['riskScore']
                        )
                        resultCache[ticker][step] = pkt
    
            return resultCache
    
        except Error as e:
            print(f"Error loading all current predictions: {e}")
            return {}


    #private
    def getTableName(self, interval):
        if interval == "1d":
            return "predictions_daily"
        elif interval == "1h":
            return "predictions_hourly"
        else:
            raise ValueError(f"Unknown interval: {interval}")