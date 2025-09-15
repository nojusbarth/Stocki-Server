import pandas as pd


class TransformerDB:

    def __init__(self, columnsDB, columnsDF):
        self.columnsDB = columnsDB
        self.columnsDF = columnsDF



    def dataToDB(self, dataFrame, ticker):

        #columns are saved lower case in DB
        dataFrame.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)


        if not isinstance(dataFrame.index, (pd.DatetimeIndex, pd.MultiIndex)):
            raise TypeError("Expected DataFrame with DatetimeIndex")
        
        dataFrame = dataFrame.reset_index()
        dataFrame.rename(columns={dataFrame.columns[0]: "date"}, inplace=True)

        if "ticker" not in dataFrame.columns:
            dataFrame["ticker"] = ticker

        missing_cols = [c for c in self.columnsDB if c not in dataFrame.columns]
        if missing_cols:
            raise KeyError(f"Transformer data->db mis: {missing_cols}")

        dataFrame = dataFrame[self.columnsDB]
        return dataFrame


    def DBtoData(self, dataFrame):

        dataFrame = dataFrame.set_index("date")
        dataFrame.index = pd.to_datetime(dataFrame.index)

        dataFrame.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)

        dataFrame = dataFrame[self.columnsDF]

        return dataFrame


