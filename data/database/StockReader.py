
import pandas as pd
from sqlalchemy import create_engine
import os


class StockReader:

    _engine = None

    def __init__(self, pool):
        self.pool = pool

        if StockReader._engine is None:
            StockReader._engine = create_engine(os.getenv("DATABASE_URL_STOCKS"),pool_size=10, max_overflow=20)

        #only needed to safely read from sql to pandas dataframe
        self.engine = StockReader._engine



    #dont set tickers if all available data should be fetched
    def fetchDataBatch(self, interval, table, tickers=None):

        conn = self.pool.get_connection()
        cursor = conn.cursor()

        stockMap: dict[str, pd.DataFrame] = {}


        if tickers is None:
            tickers = cursor.execute(f"SELECT DISTINCT ticker FROM {table}").fetchall()
            tickers = [t[0] for t in tickers]  # Flatten

        for ticker in tickers:
            df = pd.read_sql_query(
                f"SELECT * FROM {table} WHERE ticker=%s ORDER BY date",
                self.engine,
                params=(ticker,)
            )

            stockMap[ticker] = df

        cursor.close()
        conn.close()
        return stockMap



    def getAllTickers(self):
        conn = self.pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT ticker FROM stocks_daily
            UNION
            SELECT DISTINCT ticker FROM stocks_hourly
        """)
        all_tickers = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        return all_tickers


    def getLatestUpdateTime(self, ticker, table):
        conn = self.pool.get_connection()
        cursor = conn.cursor()


        cursor.execute(
            f"SELECT MAX(date) FROM {table} WHERE ticker=%s",
            (ticker,)
        )

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result is None or result[0] is None:
            return None
        else:
            return pd.to_datetime(result[0], utc=True)

