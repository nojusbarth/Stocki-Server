

class StockWriter:

    def __init__(self, pool):
        self.pool = pool



    def addStockData(self, stockName, stockData, interval, table):

        conn = self.pool.get_connection()
        cursor = conn.cursor()


        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        numEntriesBefore = cursor.fetchone()[0]

        cols = ", ".join(stockData.columns)
        placeholders = ", ".join(["%s"] * len(stockData.columns))

        query = f"INSERT IGNORE INTO {table} ({cols}) VALUES ({placeholders})"

        values = [tuple(x) for x in stockData.to_numpy()]

        if values:
            cursor.executemany(query, values)
            conn.commit()

        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        numEntriesAfter = cursor.fetchone()[0]

        addedRows = numEntriesAfter - numEntriesBefore

        cursor.close()
        conn.close()

        return addedRows
