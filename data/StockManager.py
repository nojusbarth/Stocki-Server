
import pandas as pd
from data import StockDB, StockUpdateInfo
from stockMath import StockMath
import yfinance as yf
from data import Stock
from pathlib import Path

#Manages stock data
#stock data is stored in a file at given file path

class StockManager():

    def __init__(self):
        self.stockDB = StockDB.StockDB()
        self.stocks: dict[str, Stock.Stock] = {}        
        #when adding a new stock, this is the earliest date to fetch from
        self.latestFetchPoint = "2020-01-01"

        #load all stocks
        self.loadStocks()

        

    def loadStocks(self):
        for stockName, stockData in self.stockDB.fetchData().items():
            self.stocks[stockName] = Stock.Stock(stockName, stockData)


    #minimum update interval is 1 day,
    # jfinance returns no data on weekends and holidays, which needs to be considered when updating
    def updateStocks(self):

        currentDate = pd.Timestamp.now()

        stocksToUpdate = [
            stock for stock in self.stocks.values()
            if abs(self.stockDB.getLatestUpdateTime(stock.getName()) - currentDate) >= pd.Timedelta(days=1)
        ]
            
        for stock in stocksToUpdate:
            print(f"Updating stock: {stock.getName()}")
            
            #auto adjust false is very important otherwise adj close will not be garanteed to be in dataframe 
            newData = yf.download(stock.getName(), 
                                  start=self.stockDB.getLatestUpdateTime(stock.getName()), 
                                  end=currentDate, 
                                  interval='1d', 
                                  auto_adjust=True)
            

            if isinstance(newData.columns, pd.MultiIndex):
                newData.columns = newData.columns.get_level_values(0) #needed to avoid formatting issues

            
            addedRows = self.stockDB.addStockData(stock.getName(), newData)

            if addedRows > 0:
                self.stocks[stock.getName()] = Stock.Stock(stock.getName() ,self.stockDB.fetchData(stock.getName()))

            print(f"Updated stock: {stock.getName()}")


    def addStock(self, stockName):
        if stockName not in self.stocks:
            
            stockData = yf.download(stockName, start=self.latestFetchPoint, end=pd.Timestamp.now(), interval='1d', auto_adjust=True)
            if isinstance(stockData.columns, pd.MultiIndex):
                stockData.columns = stockData.columns.get_level_values(0) #needed to avoid formatting issues

            if stockData.empty:
                print(f"Stock {stockName} not found.")
                return

            self.stockDB.addStockData(stockName, stockData)
            self.stocks[stockName] = Stock.Stock(stockName, stockData)
        else:
            print(f"Stock {stockName} already exists in data base.")


    def getStock(self, name):

        return self.stocks[name]


    def getLatestUpdateInfo(self):
        
        latestUpdateInfo = []
        for stock in self.stocks.values():
            latestUpdateInfo.append(StockUpdateInfo.StockUpdateInfo(stockName=stock.getName(), 
                                                                    latestUpdateTime=self.stockDB.getLatestUpdateTime(stock.getName()).strftime("%Y-%m-%d")))

        return latestUpdateInfo


    def getStockNames(self):
        return list(self.stocks.keys())


    