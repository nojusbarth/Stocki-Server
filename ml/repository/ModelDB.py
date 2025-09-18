import os
import mysql.connector
from dotenv import load_dotenv


class ModelDB:

    def __init__(self):

        load_dotenv()

        self.conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DBMODELS")
        )
        self.cursor = self.conn.cursor()



    def registerModel(self, name, interval, version, stage, modelPath, scalerPath, infoPath):

        self.cursor.execute("""
            INSERT INTO models (name, interval_name, version, stage, model_path, scaler_path, info_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                stage = VALUES(stage),
                model_path = VALUES(model_path),
                scaler_path = VALUES(scaler_path),
                info_path = VALUES(info_path)
        """, (name, interval, version, stage, modelPath, scalerPath, infoPath))

        self.conn.commit()

        print(f"registered model {name} to db")



    def getModelPaths(self, name, interval, stage, version=None):

        query = "SELECT model_path, scaler_path, info_path FROM models WHERE name=%s AND interval_name=%s"
        params = [name, interval]
        
        if version is not None:
            query += " AND version=%s"
            params.append(version)
        
        self.cursor.execute(query, params)
        
        row = self.cursor.fetchone()
        
        if row is None:
            raise ValueError(f"No Model found for name={name}, interval={interval}, version={version}, stage={stage}")


        return {
            "model_path": row[0],
            "scaler_path": row[1],
            "info_path": row[2]
        }