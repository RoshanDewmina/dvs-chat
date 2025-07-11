import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi

app = FastAPI()

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "my-org")

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask_question(request: QueryRequest):
    try:
        tables = query_api.query(request.query, org=INFLUXDB_ORG)
        results = []
        for table in tables:
            for record in table.records:
                results.append(record.values)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))