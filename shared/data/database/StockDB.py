import pandas as pd
import os
import mysql.connector
from dotenv import load_dotenv


from shared.data.database import StockReader, StockWriter, TransformerDB


class StockDB:

    _pool = None

    def __init__(self):

        load_dotenv()        
        
        if StockDB._pool is None:
            StockDB._pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="stockpool",
                pool_size=5,
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DBSTOCKS")
            )

        self.pool = StockDB._pool


        self.columnsDB = ["ticker", "date", "open", "high", "low", "close", "volume"]
        self.columnsDF = ["Open", "High", "Low", "Close", "Volume"]

        self.dbTranformer = TransformerDB.TransformerDB(self.columnsDB, self.columnsDF)
        self.dbWriter = StockWriter.StockWriter(self.pool)
        self.dbReader = StockReader.StockReader(self.pool)


    def fetchDataSingle(self, ticker, interval):
        tickers=[ticker]
        
        data = self.dbReader.fetchDataBatch(interval, self.getTableName(interval), tickers=tickers)[ticker]

        return self.dbTranformer.DBtoData(data)

    #dont set tickers if all available data should be fetched
    def fetchDataBatch(self, interval, tickers=None):
        
        dataDict = self.dbReader.fetchDataBatch(interval, self.getTableName(interval), tickers=tickers)

        for key, value in dataDict.items():
            dataDict[key] = self.dbTranformer.DBtoData(value)

        return dataDict

    def addStockData(self, stockName, stockData, interval):
        stockData = stockData.copy()

        stockData = self.dbTranformer.dataToDB(stockData, stockName, interval)

        return self.dbWriter.addStockData(stockName, stockData, interval, self.getTableName(interval))


    def getLatestUpdateTime(self, ticker, interval):
        return self.dbReader.getLatestUpdateTime(ticker, self.getTableName(interval))


    def getAllTickers(self):
        return self.dbReader.getAllTickers()


    def getTableName(self, interval):
        if interval == "1d":
            return "stocks_daily"
        elif interval == "1h":
            return "stocks_hourly"
        else:
            raise ValueError(f"Unknown interval: {interval}")