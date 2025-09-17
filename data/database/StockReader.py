
import pandas as pd

class StockReader:

    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn


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
                f"SELECT * FROM {table} WHERE ticker=? ORDER BY date",
                self.conn,
                params=(ticker,)
            )

            stockMap[ticker] = df



        print(f"{len(stockMap)} stocks loaded successfully.")
        return stockMap



    def getAllTickers(self):
        tickers_daily = self.cursor.execute(
            "SELECT DISTINCT ticker FROM stocks_daily"
        ).fetchall()
        tickers_hourly = self.cursor.execute(
            "SELECT DISTINCT ticker FROM stocks_hourly"
        ).fetchall()
    
        # flatten and remove duplicates
        all_tickers = {t[0] for t in tickers_daily} | {t[0] for t in tickers_hourly}
        return list(all_tickers)


    def getLatestUpdateTime(self, ticker, table):

        result = self.cursor.execute(
            f"SELECT MAX(date) FROM {table} WHERE ticker=?",
            (ticker,)
        ).fetchone()

        if result is None or result[0] is None:
            return None
        else:
            return pd.to_datetime(result[0], utc=True)