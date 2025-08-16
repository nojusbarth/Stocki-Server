import pandas as pd
import os

#new 

# Encapsulating stock data in a class
# enabling update polling on stock data


class Stock():
   
    def __init__(self, name, data):
        self.name = name
        #pandas data frame
        self.data = data
        
        self.latestUpdate = data.index[-1] if not data.empty else None


    #returns the stock data, which wasn't already in data base in order to update the stock file
    def updateData(self, newData):

        toAdd = newData[newData.index > self.latestUpdate]

        if not toAdd.empty:
            self.data = pd.concat([self.data, toAdd], ignore_index=False)
            self.latestUpdate = toAdd.index[-1]

        return toAdd


    def getName(self):
        return self.name

    def getLatestUpdateTime(self):
        return self.latestUpdate

