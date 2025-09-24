import os
import mysql.connector
from dotenv import load_dotenv


class ModelDB:

    _pool = None

    def __init__(self):
  
        
        if ModelDB._pool is None:
            ModelDB._pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="modelpool",
                pool_size=5,
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DBMODELS")
            )

        self.pool = ModelDB._pool



    def registerModel(self, name, interval, version, stage, modelPath, scalerPath, infoPath):

        conn = self.pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO models (name, interval_name, version, stage, model_path, scaler_path, info_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                stage = VALUES(stage),
                model_path = VALUES(model_path),
                scaler_path = VALUES(scaler_path),
                info_path = VALUES(info_path)
        """, (name, interval, version, stage, modelPath, scalerPath, infoPath))

        conn.commit()


        cursor.close()
        conn.close()



    def getModelPaths(self, name, interval, stage, version):

        conn = self.pool.get_connection()
        cursor = conn.cursor()

        query = "SELECT model_path, scaler_path, info_path FROM models WHERE name=%s AND interval_name=%s AND stage=%s AND version=%s"
        params = [name, interval, stage, version]
        
        
        cursor.execute(query, params)
        
        row = cursor.fetchone()
        
        if row is None:
            raise ValueError(f"No Model found for name={name}, interval={interval}, version={version}, stage={stage}")

        cursor.close()
        conn.close()

        return {
            "model_path": row[0],
            "scaler_path": row[1],
            "info_path": row[2]
        }


    def containsModel(self, name, interval, stage, version):
        conn = self.pool.get_connection()
        cursor = conn.cursor()        
        
        query = "SELECT COUNT(*) FROM models WHERE name=%s AND interval_name=%s AND stage=%s AND version=%s"
        params = [name, interval, stage, version]
        
        cursor.execute(query, params)
        
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return row[0] > 0