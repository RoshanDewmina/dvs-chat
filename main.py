import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from typing import Optional

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

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
def chat(request: ChatRequest):
    # Simple rule-based mapping from question to Flux query
    q = request.question.lower()
    if "bottleneck" in q and "aura" in q:
        # Example: look for high latency or error rates in project Aura
        flux_query = '''
        from(bucket: "project_metrics")
          |> range(start: -1h)
          |> filter(fn: (r) => r["project"] == "Aura" and (r["metric"] == "latency" or r["metric"] == "error_rate"))
          |> mean()
        '''
        try:
            tables = query_api.query(flux_query, org=INFLUXDB_ORG)
            results = []
            for table in tables:
                for record in table.records:
                    results.append(record.values)
            if not results:
                return {"answer": "No bottlenecks detected for project Aura in the last hour."}
            # Example logic: if latency or error_rate is high, report a bottleneck
            answer = "No significant bottlenecks detected for project Aura."
            for r in results:
                if r.get("_value", 0) > 1000:  # Example threshold
                    answer = "Yes, there are bottlenecks with project Aura (high latency or error rate)."
                    break
            return {"answer": answer, "details": results}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        return {"answer": "Sorry, I don't know how to answer that yet."}