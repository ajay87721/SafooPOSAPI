# main.py - FastAPI app running on your server
from fastapi import FastAPI
import pyodbc
from datetime import date, timedelta
import json

app = FastAPI()

def get_pos_data():
    conn_str = (
        "DRIVER=SQL Anywhere 17;"
        "UID=reportuser;"
        "PWD=pixel1047;"
        "ServerName=PixelSqlBase_HO;"
        "Host=212.118.112.195:2638;"
        "DBN=PixelSqlBase_HO"
    )

    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        query = """...your SQL query here..."""  # same as before
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

@app.get("/api/pixel-pos-data")
def read_data():
    data = get_pos_data()
    return {"data": data, "date": (date.today() - timedelta(days=1)).isoformat()}
