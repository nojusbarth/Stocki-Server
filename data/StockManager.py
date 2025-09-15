
import pandas as pd
from data.database import StockDB
from data import StockUpdateInfo
from stockMath import StockMath
import yfinance as yf
from data import Stock
from pathlib import Path


class StockManager():

    def __init__(self):
        self.stockDB = StockDB.StockDB()
        #when adding a new stock, this is the earliest date to fetch from
        self.latestFetchPointDaily = "2020-01-01"
        #using period for hourly request because its easier
        self.fetchPeriodHourly = "60d"

        

    def updateStocks(self, interval):

        currentTime = pd.Timestamp.now()

            
        delta = pd.Timedelta(days=1) if interval == "1d" else pd.Timedelta(hours=1)
    
        tickers = self.stockDB.getAllTickers()
    
        for ticker in tickers:
            lastUpdate = self.stockDB.getLatestUpdateTime(ticker, interval=interval)
    
            # Prüfen, ob Update nötig ist
            if abs(currentTime - lastUpdate) >= delta:
                print(f"Updating [interval={interval}] stock: {ticker}")
    
                # Neue Daten von yfinance laden
                newData = yf.download(
                    ticker,
                    start=lastUpdate,
                    end=currentTime,
                    interval=interval,
                    auto_adjust=True
                )
    
                if isinstance(newData.columns, pd.MultiIndex):
                    newData.columns = newData.columns.get_level_values(0)
    
                # In die DB schreiben
                addedRows = self.stockDB.addStockData(ticker, newData, interval=interval)
                print(f"Updated {interval} stock: {ticker}, added {addedRows} rows")



    def addStock(self, stockName):
        if not stockName in self.stockDB.getAllTickers():
            
            stockDataDaily = yf.download(stockName, start=self.latestFetchPointDaily, end=pd.Timestamp.now(), interval='1d', auto_adjust=True)
            stockDataHourly = yf.download(stockName, interval='1h', auto_adjust=True, period=self.fetchPeriodHourly)

            if isinstance(stockDataDaily.columns, pd.MultiIndex):
                stockDataDaily.columns = stockDataDaily.columns.get_level_values(0) #needed to avoid formatting issues

            if isinstance(stockDataHourly.columns, pd.MultiIndex):
                stockDataHourly.columns = stockDataHourly.columns.get_level_values(0) #needed to avoid formatting issues

            if stockDataDaily.empty or stockDataHourly.empty:
                print(f"Stock {stockName} not found.")
                return

            self.stockDB.addStockData(stockName, stockDataDaily, interval='1d')
            self.stockDB.addStockData(stockName, stockDataHourly, interval='1h')
        else:
            print(f"Stock {stockName} already exists in data base.")


    def getStockData(self, name, interval):
        return self.stockDB.fetchDataSingle(name,interval)


    def getLatestUpdateInfo(self):
        intervals = ["1d", "1h"]
        latestUpdateDict = {}

    
        for interval in intervals:
            intervalInfo = []
    
            for ticker in self.stockDB.getAllTickers():
                latestTime = self.stockDB.getLatestUpdateTime(ticker, interval)
                if latestTime is not None:
                    if interval == "1d":
                        timeStr = latestTime.strftime("%Y-%m-%d")
                    elif interval == "1h":
                        timeStr = latestTime.strftime("%Y-%m-%d %H")
                    
    
                    intervalInfo.append(
                        StockUpdateInfo.StockUpdateInfo(
                            stockName=ticker,
                            latestUpdateTime=timeStr
                        )
                    )
    
            latestUpdateDict[interval] = intervalInfo
    
        return latestUpdateDict



    def getStockNames(self):
        return self.stockDB.getAllTickers()


    