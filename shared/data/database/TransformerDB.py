import pandas as pd


class TransformerDB:

    def __init__(self, columnsDB, columnsDF):
        self.columnsDB = columnsDB
        self.columnsDF = columnsDF



    def dataToDB(self, dataFrame, ticker, interval):

        if not isinstance(dataFrame.index, pd.DatetimeIndex):
            dataFrame.index = pd.to_datetime(dataFrame.index)

        if interval == "1d":
            dataFrame.index = dataFrame.index.normalize()
        elif interval == "1h":
            dataFrame.index = dataFrame.index.floor('h')
        
        #timezone not allowed in db (sql error)
        if dataFrame.index.tzinfo is not None:
            dataFrame.index.tz_convert(None)

        #columns are saved lower case in DB
        dataFrame.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)

        
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
        dataFrame.index = pd.to_datetime(dataFrame.index, utc=True)

        dataFrame.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)

        dataFrame = dataFrame[self.columnsDF]

        return dataFrame


