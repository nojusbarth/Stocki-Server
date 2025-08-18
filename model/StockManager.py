
import pandas as pd
from model import StockFiles
import yfinance as yf
from model import Stock
from pathlib import Path

#Manages stock data
#stock data is stored in a file at given file path

class StockManager():

    def __init__(self, filePath=r"C:\Users\nojob\Programmieren\Visual Studio\python\Stocki\project\financedata"):
        self.stockFiler = StockFiles.StockFiles(Path(filePath))
        self.stocks = []

        #load all stocks
        self.loadStocks()

        

    def loadStocks(self):
        for stockName, stockData in self.stockFiler.fetchData().items():
            self.stocks.append(Stock.Stock(stockName, stockData))


    #minimum update interval is 1 day
    def updateStocks(self):
        currentDate = pd.Timestamp.now()

        for stock in self.stocks:
            #only update if the stock data is older than 1 day
            if(abs(stock.getLatestUpdateTime() - currentDate) >= pd.Timedelta(days=1)):
                print(f"Updating stock: {stock.getName()}")
                #fetch new data from the internet
                newData = yf.download(stock.getName(), start=stock.getLatestUpdateTime(), end=currentDate, interval='1d')
                if isinstance(newData.columns, pd.MultiIndex):
                    newData.columns = newData.columns.get_level_values(0) #needed to avoid formatting issues

                self.stockFiler.appendStockData(stock.getName(), stock.updateData(newData))
                    



    def addStock(self, stockName):
        if not any(stock.getName() == stockName for stock in self.stocks):
            
            stockData = yf.download(stockName, period='max', interval='1d', auto_adjust=False)
            if isinstance(stockData.columns, pd.MultiIndex):
                stockData.columns = stockData.columns.get_level_values(0) #needed to avoid formatting issues

            if stockData.empty:
                print(f"Stock {stockName} not found.")
                return

            self.stockFiler.addStockFile(stockName, stockData)
            self.stocks.append(Stock.Stock(stockName, stockData))
        else:
            print(f"Stock {stockName} already exists in data base.")


    def getStock(self, name):

        for stock in self.stocks:
            if stock.getName() == name:
                return stock
        return None


    def getStockNames(self):
        return [stock.getName() for stock in self.stocks]
