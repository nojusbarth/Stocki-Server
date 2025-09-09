
import pandas as pd
from data import StockFiles, StockUpdateInfo
import yfinance as yf
from data import Stock
from pathlib import Path

#Manages stock data
#stock data is stored in a file at given file path

class StockManager():

    def __init__(self, filePath=r"C:\Users\nojob\Programmieren\Visual Studio\python\Stocki\project\financedata"):
        self.stockFiler = StockFiles.StockFiles(Path(filePath))
        self.stocks = []
        #when adding a new stock, this is the earliest date to fetch from
        self.latestFetchPoint = "2020-01-01"

        #load all stocks
        self.loadStocks()

        

    def loadStocks(self):
        for stockName, stockData in self.stockFiler.fetchData().items():
            self.stocks.append(Stock.Stock(stockName, stockData))


    #minimum update interval is 1 day,
    # jfinance returns no data on weekends and holidays, which needs to be considered when updating
    def updateStocks(self):
        
        currentDate = pd.Timestamp.now()

        for stock in self.stocks:
            #only update if the stock data is older than 1 day
            if(abs(stock.getLatestUpdateTime() - currentDate) >= pd.Timedelta(days=1)):
                print(f"Updating stock: {stock.getName()}")
                
                #auto adjust false is very important otherwise adj close will not be garanteed to be in dataframe 
                newData = yf.download(stock.getName(), start=stock.getLatestUpdateTime(), end=currentDate, interval='1d', auto_adjust=True)
                if isinstance(newData.columns, pd.MultiIndex):
                    newData.columns = newData.columns.get_level_values(0) #needed to avoid formatting issues

                relevantData = stock.updateData(newData)

                if not relevantData.empty:
                    self.stockFiler.appendStockData(stock.getName(), relevantData)
                    print(f"stock {stock.getName()} updated with {len(relevantData)} new rows")
                else:
                    stock.forceUpdateTime(currentDate)
            else:
                print(f"stock {stock.getName()} is up to date")
                    



    def addStock(self, stockName):
        if not any(stock.getName() == stockName for stock in self.stocks):
            
            stockData = yf.download(stockName, start=self.latestFetchPoint, end=pd.Timestamp.now(), interval='1d', auto_adjust=True)
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


    def getLatestUpdateInfo(self):
        
        latestUpdateInfo = []
        for stock in self.stocks:
            latestUpdateInfo.append(StockUpdateInfo.StockUpdateInfo(stockName=stock.getName(), 
                                                                    latestUpdateTime=stock.getLatestUpdateTime().strftime("%Y-%m-%d")))

        return latestUpdateInfo


    def getStockNames(self):
        return [stock.getName() for stock in self.stocks]



    