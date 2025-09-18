
import pandas as pd
from sqlalchemy import create_engine


class StockReader:

    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

        #only needed to safely read from sql to pandas dataframe
        self.engine = create_engine("mysql+mysqlconnector://root:Binoderhund1!_@127.0.0.1/stocks")



    #dont set tickers if all available data should be fetched
    def fetchDataBatch(self, interval, table, tickers=None):

        stockMap: dict[str, pd.DataFrame] = {}

        print(f"Loading stocks from database with intervall set to: {interval}")


        if tickers is None:
            tickers = self.cursor.execute(f"SELECT DISTINCT ticker FROM {table}").fetchall()
            tickers = [t[0] for t in tickers]  # Flatten

        # list of tickers otherwise
        for ticker in tickers:
            print(f"Loading stock: {ticker}")
            df = pd.read_sql_query(
                "SELECT * FROM stocks_daily WHERE ticker=%s ORDER BY date",
                self.engine,
                params=(ticker,)
            )

            stockMap[ticker] = df



        print(f"{len(stockMap)} stocks loaded successfully.")
        return stockMap



    def getAllTickers(self):
        self.cursor.execute("""
            SELECT DISTINCT ticker FROM stocks_daily
            UNION
            SELECT DISTINCT ticker FROM stocks_hourly
        """)
        all_tickers = [row[0] for row in self.cursor.fetchall()]
        return all_tickers


    def getLatestUpdateTime(self, ticker, table):

        self.cursor.execute(
            f"SELECT MAX(date) FROM {table} WHERE ticker=%s",
            (ticker,)
        )

        result = self.cursor.fetchone()

        if result is None or result[0] is None:
            return None
        else:
            return pd.to_datetime(result[0], utc=True)