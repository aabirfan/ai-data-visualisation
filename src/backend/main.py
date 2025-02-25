import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv


## FUNCTION IMPORTS

from utils.query_processor import process_sensor_query
from models.general_queries import fetch_embedded_queries

from models.chart_generation import manual_chart_builder
from models.chart_generation import llmPrompt

from models.embeddings import embed_query
from models.embeddings import vector_search

from utils.data_calculations import calc_pipeline

load_dotenv("../../.env.local")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"Hello": "World test"}

@app.post("/query")
async def process_query(query_request: QueryRequest):

    ##TIMESTAMP + VALUE 
    response, sensor_name = process_sensor_query(query_request.query) 

    ## VECTOR SEARCH (Embeds query and matches it with saved queries
    ##prompt = vector_search(query_request.query)
    ## print("prompt:", prompt)

    ##response = fetch_embedded_queries(prompt)

    ##print("respones", response)


    ## calculations = calc_pipeline(response)
        
    ## UNCOMMENT & SET AS RETURN TO ENABLE LLM PIPELINE 
    ##llm_response = await llmPrompt(calculations)

    print(f"DEBUG: Sensor Name received in process_query: {sensor_name}")

    if isinstance(response, dict) and "error" in response:
        return {"error": response["error"]}

    chart = manual_chart_builder(response, sensor_name=sensor_name)  

    return {"message": chart}


