

class StockWriter:

    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn



    def addStockData(self, stockName, stockData, interval, table):

        print(f"Adding entries for {stockName} [interval = {interval}] into {table}...")

        self.cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        numEntriesBefore = self.cursor.fetchone()[0]

        cols = ", ".join(stockData.columns)
        placeholders = ", ".join(["%s"] * len(stockData.columns))

        query = f"INSERT IGNORE INTO {table} ({cols}) VALUES ({placeholders})"

        values = [tuple(x) for x in stockData.to_numpy()]

        if values:
            self.cursor.executemany(query, values)
            self.conn.commit()

        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
        numEntriesAfter = self.cursor.fetchone()[0]

        addedRows = numEntriesAfter - numEntriesBefore
        print(f"Added {addedRows} new entries to {stockName} [interval = {interval}] in {table}")
