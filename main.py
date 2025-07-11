import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

app = FastAPI()

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "my-org")

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCPsI_Qqp5kXl1mPK_A0apddXI1-WqqEoU")

llm = ChatGoogleGenerativeAI(
    google_api_key=GEMINI_API_KEY,
    model="gemini-pro"
)

# Prompt for generating a Flux query from a user question
flux_query_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in InfluxDB and Flux. Given a user's question about time series data, generate the most appropriate Flux query. Only output the query, nothing else."),
    ("human", "{question}")
])

# Prompt for generating a user-friendly answer from query results
answer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Given the user's question and the raw results from InfluxDB, provide a concise, user-friendly answer."),
    ("human", "Question: {question}\nResults: {results}")
])

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
    # Step 1: Use Gemini to generate a Flux query
    try:
        flux_query_chain = flux_query_prompt | llm
        flux_query = flux_query_chain.invoke({"question": request.question}).content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Flux query: {e}")

    # Step 2: Run the Flux query
    try:
        tables = query_api.query(flux_query, org=INFLUXDB_ORG)
        results = []
        for table in tables:
            for record in table.records:
                results.append(record.values)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to run Flux query: {e}")

    # Step 3: Use Gemini to generate a user-friendly answer
    try:
        answer_chain = answer_prompt | llm
        answer = answer_chain.invoke({"question": request.question, "results": str(results)}).content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {e}")

    return {"answer": answer, "flux_query": flux_query, "details": results}