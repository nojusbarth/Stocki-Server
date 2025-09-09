import pandas as pd
import os
import sqlite3


class StockDB:

    def __init__(self):
        self.dbName = "stocks"
        self.conn = sqlite3.connect(f"{self.dbName}.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        )
        """)

        self.conn.commit()


    def fetchData(self, tickers="all"):

        stockMap: dict[str, pd.DataFrame] = {}

        print("Loading stocks from database")

        # alle tickers in db
        if tickers == "all":
            tickers = self.cursor.execute(f"SELECT DISTINCT ticker FROM {self.dbName}").fetchall()
            tickers = [t[0] for t in tickers]  # Flatten

        # list of tickers otherwise
        if not isinstance(tickers, list):
            tickers = [tickers]

        for ticker in tickers:
            print(f"Loading stock: {ticker}")
            df = pd.read_sql_query(
                f"SELECT * FROM {self.dbName} WHERE ticker='{ticker}' ORDER BY date",
                self.conn,
                parse_dates=["date"],
                index_col="date"
            )
            df.rename(columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume"
            }, inplace=True)


            stockMap[ticker] = df



        print(f"{len(stockMap)} stocks loaded successfully.")
        return stockMap


    def addStockData(self, stockName, stockData):

        stockData = stockData.copy()

        stockData.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)

        stockData = self.fitDataFrame(stockData, stockName)

        print(f"Updating entry for {stockName}...")

        numEntriesBefore = self.cursor.execute(f"SELECT COUNT(*) FROM {self.dbName}").fetchone()[0]

        #temporary table to automatically ignore dublicates
        stockData.to_sql("temp_table", self.conn, if_exists="replace", index=False)

        self.cursor.execute(f"""
            INSERT OR IGNORE INTO {self.dbName}
            SELECT * FROM temp_table
        """)

        numEntriesAfter = self.cursor.execute(f"SELECT COUNT(*) FROM {self.dbName}").fetchone()[0]
        
        self.conn.commit()

        addedRows = numEntriesAfter-numEntriesBefore
        print(f"Added {addedRows} new entries to {stockName}")

        return addedRows


    def getLatestUpdateTime(self, ticker):
        result = self.cursor.execute(
            f"SELECT MAX(date) FROM {self.dbName} WHERE ticker=?",
            (ticker,)
        ).fetchone()
    
        if result is None or result[0] is None:
            return None  # keine Daten vorhanden
        else:
            return pd.to_datetime(result[0])


    #private function: converts df to be compatible with database format
    def fitDataFrame(self, df, ticker):

        columns = ["ticker", "date", "open", "high", "low", "close", "volume"]
        
        if "date" not in df.columns:
            df = df.reset_index()  # index to column
            if "Date" in df.columns and "date" not in df.columns:
                df.rename(columns={"Date": "date"}, inplace=True)
        
        if "ticker" not in df.columns:
            df["ticker"] = ticker
        
        df = df[columns]

        return df