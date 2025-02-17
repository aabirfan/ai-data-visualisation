import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

## FUNCTION IMPORTS

from utils.query_processor import process_sensor_query

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

    ## TIMESTAMP + VALUE 
    ##response = process_sensor_query(query_request.query)

    ## VECTOR SEARCH (Embeds query and matches it with saved queries
    response = vector_search(query_request.query)

    ## calculations = calc_pipeline(response)
        
    ## UNCOMMENT & SET AS RETURN TO ENABLE LLM PIPELINE 
    ##llm_response = await llmPrompt(calculations)

    ##chart = chart_data(response)

    return {"message": response}


