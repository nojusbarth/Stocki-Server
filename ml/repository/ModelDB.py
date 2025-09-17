
import sqlite3


class ModelDB:

    def __init__(self):

        self.dbName = "models"
        self.conn = sqlite3.connect(f"{self.dbName}.db", check_same_thread=False)
        self.cursor = self.conn.cursor()


        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   
            name TEXT NOT NULL,                     
            interval TEXT NOT NULL,                 
            version TEXT NOT NULL,
            stage TEXT NOT NULL CHECK(stage IN ('dev', 'production', 'archived')),
            model_path TEXT NOT NULL,               
            scaler_path TEXT NOT NULL,              
            info_path TEXT NOT NULL,                
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, interval, version, stage)
        );
        """)



    def registerModel(self, name, interval, version, stage, modelPath, scalerPath, infoPath):

        self.cursor.execute("""
            INSERT OR REPLACE INTO models (name, interval, version, stage, model_path, scaler_path, info_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, interval, version, stage, modelPath, scalerPath, infoPath))

        self.conn.commit()

        print(f"registered model {name} to db")



    def getModelPaths(self, name, interval, stage, version=None):

        query = "SELECT model_path, scaler_path, info_path FROM models WHERE name=? AND interval=?"
        params = [name, interval]

        if version is not None:
            query += " AND version=?"
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