
import pandas as pd
from data.database import StockDB
from data.update import StockUpdateInfo
from stockMath import StockMath
import yfinance as yf
from data import Stock
from pathlib import Path
import locks
import logging
import threading

class StockManager():

    def __init__(self):
        self.stockDB = StockDB.StockDB()
        #when adding a new stock, this is the earliest date to fetch from
        self.latestFetchPointDaily = "2020-01-01"
        #using period for hourly request because its easier
        self.fetchPeriodHourly = "60d"
        self.logger = logging.getLogger("stock")

        

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
            self.logger.info(f"No stocks to update for interval {interval}.")
            return

        latestUpdate = min(lastUpdates) if lastUpdates else currentTime    

        newData = self.downloadData(tickersToUpdate, latestUpdate, currentTime, interval)

        updatePackages = []
        addedRows = 0

        for ticker in tickersToUpdate:
            if isinstance(newData.columns, pd.MultiIndex):
                tickerData = newData.xs(ticker, level=1, axis=1).copy()
            else:
                tickerData = newData.copy()

            #convert minutes to hours
            if interval == "1h" and not tickerData.empty:
                tickerData = tickerData.resample("1h", label="right", closed="right").agg({
                    "Open": "first",
                    "High": "max",
                    "Low": "min",
                    "Close": "last",
                    "Volume": "sum"
                })
                tickerData = tickerData[tickerData.index <= currentTime.floor("h")]

            
            tickerData = self.cleanUpdateData(tickerData)
            if not tickerData.empty:
                addedRowsStock= self.stockDB.addStockData(ticker, tickerData, interval=interval)
                
                if addedRowsStock > 0:
                    updatePackages.append(self.buildUpdatePackage(ticker,tickerData,interval))
                    addedRows += addedRowsStock

        self.logger.info({
            "event": "stock_update_finished",
            "message": f"stock update for interval {interval} finished",
            "stock_names": tickersToUpdate,
            "added_rows": addedRows,
            "thread": threading.current_thread().name
        })
        return updatePackages



    def addStock(self, stockName):
        if not stockName in self.stockDB.getAllTickers():
            with locks.yfLock:
                stockDataDaily = yf.download(stockName, start=self.latestFetchPointDaily, end=pd.Timestamp.now(), interval='1d', auto_adjust=True)
                stockDataHourly = yf.download(stockName, interval='1h', auto_adjust=True, period=self.fetchPeriodHourly)

            if isinstance(stockDataDaily.columns, pd.MultiIndex):
                stockDataDaily.columns = stockDataDaily.columns.get_level_values(0) #needed to avoid formatting issues

            if isinstance(stockDataHourly.columns, pd.MultiIndex):
                stockDataHourly.columns = stockDataHourly.columns.get_level_values(0) #needed to avoid formatting issues

            if stockDataDaily.empty or stockDataHourly.empty:
                print(f"Stock {stockName} not found.")

            self.stockDB.addStockData(stockName, stockDataDaily, interval='1d')
            self.stockDB.addStockData(stockName, stockDataHourly, interval='1h')
        else:
            print(f"Stock {stockName} already exists in data base.")


    def getStockData(self, name, interval):
        return self.stockDB.fetchDataSingle(name,interval)

    #private
    def buildUpdatePackage(self, ticker, data, interval):
        ts = pd.to_datetime(data.index[-1])

        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        else:
            ts = ts.tz_convert("UTC")

        if interval == "1h":
            ts = ts.floor("h")
        elif interval == "1d":
            ts = ts.normalize()

        return StockUpdateInfo.StockUpdateInfo(
            stockName=ticker,
            latestUpdateTime=ts,
            interval=interval
        )




    def getStockTickers(self):
        return self.stockDB.getAllTickers()

    #private
    def downloadData(self, tickersToUpdate, latestUpdate, currentTime, interval):
        newData = None
        if interval == "1h":
            # By switching to 1m data for 1h updates, we can get prepost market data 
            # (ONLY WORKS IF LAST UPDATE WAS AT MAX 7 DAYS AGO    
            allData = [] #prepost only allows single ticker download
            with locks.yfLock:
                for ticker in tickersToUpdate:
                    df = yf.download(
                        ticker,
                        start=latestUpdate,
                        end=currentTime,
                        interval="1m",
                        auto_adjust=True,
                        prepost=True
                    )
                    if isinstance(df.columns, pd.MultiIndex):
                        df = df.copy()
                        df.columns = df.columns.get_level_values(0)
                    df.columns = pd.MultiIndex.from_product([df.columns, [ticker]])
                    allData.append(df)

            newData = pd.concat(allData, axis=1)

        elif interval=="1d":
            with locks.yfLock:

                newData = yf.download(
                    tickers=tickersToUpdate,
                    start=latestUpdate.date(),
                    end=currentTime.date(),
                    interval=interval,
                    auto_adjust=True
                )

        return newData


    #private 
    def cleanUpdateData(self, data):
        data = data.dropna(how="any")
        cols_to_check = [c for c in data.columns if c.lower() != "volume"]
        data = data[(data[cols_to_check] != 0).all(axis=1)]
        
        return data


    