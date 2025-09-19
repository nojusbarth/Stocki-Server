
import pandas as pd
from data.database import StockDB
from data.update import StockUpdateInfo
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

        

    def updateStocks(self, interval, tickers):

        currentTime = pd.Timestamp.now(tz="UTC")
        delta = pd.Timedelta(days=1) if interval == "1d" else pd.Timedelta(hours=1)

        tickersToUpdate = []
        lastUpdates = []
        for ticker in tickers:
            lastUpdate = self.stockDB.getLatestUpdateTime(ticker, interval=interval)
            if abs(currentTime - lastUpdate) >= delta:
                tickersToUpdate.append(ticker)
                lastUpdates.append(lastUpdate)

        if not tickersToUpdate:
            print(f"No stocks need updating for interval {interval}.")
            return

        latestUpdate = min(lastUpdates) if lastUpdates else currentTime


        print(f"Updating [interval={interval}] stocks: {tickers}")
    
        newData = yf.download(
            tickers=tickers,
            start=latestUpdate,
            end=currentTime,
            interval=interval,
            auto_adjust=True
        )
    
        for ticker in tickers:
            if isinstance(newData.columns, pd.MultiIndex):
                tickerData = newData.xs(ticker, level=1, axis=1).copy()
            else:
                tickerData = newData.copy()

            tickerData = self.cleanUpdateData(tickerData)

            if not tickerData.empty:
                self.stockDB.addStockData(ticker, tickerData, interval=interval)




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


    def getLatestUpdateInfo(self, interval):

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
                        latestUpdateTime=timeStr,
                        interval=interval
                    )
                )
   
        return intervalInfo



    def getStockNames(self):
        return self.stockDB.getAllTickers()



    #private 
    def cleanUpdateData(self, data):
        data = data.dropna(how="any")
        data = data[(data != 0).all(axis=1)]

        return data


    