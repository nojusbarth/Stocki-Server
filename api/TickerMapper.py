
import pandas as pd
import locks
import yfinance as yf
from pathlib import Path
from datetime import datetime


class TickerMapper:

    def __init__(self, tickers):
        self.csvPath = Path("tickermap.csv")

        if self.csvPath.exists():
            self.table = pd.read_csv(self.csvPath)
        else:
            self.table = pd.DataFrame(columns=["ticker", "name"])

        self.updateCSV(tickers)

    # private
    def updateCSV(self, tickers):
        tickers_to_update = [
            t for t in tickers 
            if t.upper() not in self.table["ticker"].str.upper().values
        ]

        if not tickers_to_update:
            return

        with locks.yfLock:
            tickersObj = yf.Tickers(" ".join(tickers_to_update))

            rows = []
            for t in tickers_to_update:
                try:
                    info = tickersObj.tickers[t].info
                    name = info.get("shortName") or info.get("longName") or t
                    rows.append({"ticker": t.upper(), "name": name})
                except Exception as e:
                    print(f"{t} couldn't update shortname: {e}")
                    rows.append({"ticker": t.upper(), "name": t})  # Fallback

        new_df = pd.DataFrame(rows)
        self.table = pd.concat([self.table, new_df], ignore_index=True)
        self.table.to_csv(self.csvPath, index=False)

    def getName(self, ticker: str):
        row = self.table[self.table["ticker"].str.upper() == ticker.upper()]
        if len(row) == 0:
            return ticker
        return row["name"].values[0]

    def getTicker(self, name: str):
        row = self.table[self.table["name"].str.upper() == name.upper()]
        if len(row) == 0:
            return name
        return row["ticker"].values[0]
