# Encapsulating stock data in a class


class Stock():
   
    def __init__(self, name, data):
        self.name = name
        #pandas data frame
        self.data = data

    def getName(self):
        return self.name


    def getData(self):
        return self.data

