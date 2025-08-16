import pandas as pd
import os

class StockFiles:

    def __init__(self, filePath):

        self.filePath = filePath


    def fetchData(self):

        stockMap: dict[str, pd.DataFrame] = {}

        print(f"Loading stocks from {self.filePath}:")

        for csv_stock in self.filePath.glob("*.csv"):
            stockName = csv_stock.stem
            print(f"Loading stock: {stockName}")
            #load stock data from csv file
            stockData = pd.read_csv(csv_stock, index_col="Date", header=2, parse_dates=["Date"])
            stockMap[stockName] = stockData

        print(f"{len(stockMap)} Stocks loaded successfully.")

        return stockMap


    def addStockFile(self, stockName, stockData):
        
        fileLocation = os.path.join(self.filePath, f"{stockName}.csv")

        if not os.path.exists(fileLocation):
            print(f"Creating new stock file for {stockName}...")
            stockData.to_csv(fileLocation, index=True)
            print(f"stock file for {stockName} created")
        else:
            print(f"Stock file for {stockName} already exists. Adding new file failed.")


    #WANRING: NO SAFETY CHECK WHETHER DATA MAKES SENSE!
    def appendStockData(self, stockName, dataToAppend):
        if not dataToAppend.empty:

            fileLocation = os.path.join(self.filePath, f"{stockName}.csv")

            if os.path.exists(fileLocation):
                print(f"Appending data to existing stock file for {stockName}...")
                dataToAppend.to_csv(fileLocation, mode='a', header=False)
                print(f"Appended {len(dataToAppend)} new rows to {stockName}.csv")
            else:
                print(f"Stock file for {stockName} does not exist. Update failed.")
