
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime
import re


class TickerMapper:

    def __init__(self, tickers):

        self.csvPath = Path("tickermap.csv")

        if self.csvPath.exists():
            self.table = pd.read_csv(self.csvPath)
        else:
            self.table = pd.DataFrame(columns=["ticker", "name"])
        self.updateCSV(tickers)

    #private
    def updateCSV(self, tickers):

        tickersObj = yf.Tickers(" ".join(tickers))
        
        rows = []

        for t in tickers:
            try:
                info = tickersObj.tickers[t].info
                name = info.get("shortName") or info.get("longName") or t
                rows.append({"ticker": t.upper(), "name": name})
            except Exception as e:
                print(f"{t} couldn't update shortname: {e}")
        
        new_df = pd.DataFrame(rows)
        self.table = pd.concat([self.table[self.table["ticker"].isin(tickers) == False], new_df], ignore_index=True)
        self.table.to_csv(self.csvPath, index=False)



    def getName(self, ticker):
        row = self.table[self.table["ticker"].str.upper() == ticker.upper()]
        if len(row) == 0:
            return None
        return row["name"].values[0]

    def getTicker(self, name):
        row = self.table[self.table["name"].str.upper() == name.upper()]
        if len(row) == 0:
            return None
        return row["ticker"].values[0]