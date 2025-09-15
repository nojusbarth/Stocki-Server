

class StockWriter:

    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn



    def addStockData(self, stockName, stockData, interval, table):

        print(f"Adding entries for {stockName} [interval = {interval}] into {table}...")

        numEntriesBefore = self.cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        #temporary table to avoid dublicate insertions
        stockData.to_sql("temp_table", self.conn, if_exists="replace", index=False)

        self.cursor.execute(f"""
            INSERT OR IGNORE INTO {table}
            SELECT * FROM temp_table
        """)

        numEntriesAfter = self.cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        self.conn.commit()

        addedRows = numEntriesAfter - numEntriesBefore
        print(f"Added {addedRows} new entries to {stockName} [interval = {interval}] in {table}")

        return addedRows