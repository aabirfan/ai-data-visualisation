import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Any
from fastapi import HTTPException
import json
from fastapi.responses import JSONResponse

## FUNCTION IMPORTS

from utils.query_processor import process_sensor_query

from models.chart_generation import manual_chart_builder #Pipeline 1
from models.embeddings import process_user_query #Pipeline 2
from models.llm_pipeline import process_llm_pipeline #Pipeline 3

from models.chart_archiving import addArchivedChart
from models.chart_archiving import get_chart_data
from models.chart_archiving import remove_saved_data

from models.prompt_history import add_prompt_history, get_prompt_history, clear_prompt_history

from utils.fetch_assets import fetch_assets_from_db

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
    selectedAsset: str

class ChartData(BaseModel):
    chartData: Any
    chartOptions: Any
    chartType: str
    date: int
    title: str
    description: str
    asset_id: str

class removeData(BaseModel):
    timestamp: int

class asset_req(BaseModel):
    asset_id: str  

class PromptRequest(BaseModel):
    query: str 
    asset_id: str


@app.get("/")
def read_root():    
    return {"Hello": "World test"}

@app.post("/query")
async def process_query(query_request: PromptRequest):
    print(f"Received query_request: {query_request}")
    print(f"Asset ID: {query_request.asset_id}")
    #Temporary, the prompt has to start with manual to receive a manual chart
    if query_request.query.lower().startswith("manual"):
        response, sensor_name  = process_sensor_query(query_request.query,  query_request.asset_id)

        print(f"DEBUG: Sensor Name received in process_query: {sensor_name}")

        if isinstance(response, dict) and "error" in response:
            return {"error": response["error"]}
        
        chart = manual_chart_builder(response, sensor_name)
        return {"message": chart}
    
    #Temporary, the prompt has to start with rag to receive a rag chart
    if query_request.query.lower().startswith("rag"):
        return process_user_query(query_request.query, query_request.asset_id)  

    #PIPELINE 3
    return process_llm_pipeline(query_request.query, query_request.asset_id)


@app.post("/save_chart")
async def process_saving_chart(data: ChartData):
    try:
        # Convert the ChartData to a dictionary and then to a JSON string
        chart_dict = data.dict()  # Convert the Pydantic model to a dictionary
        chart_json = json.dumps(chart_dict)  # Convert the dictionary to a JSON string

        addArchivedChart(chart_json)

        return {"message": "Chart saved successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    

@app.post("/get_chart_data")
async def process_getting_saved_charts(data: asset_req):
   list = get_chart_data(data.asset_id)
   return JSONResponse(content={"data": list})  

@app.post("/remove_saved_chart")
async def remove_saved_chart(data: removeData):
    post_id = data.timestamp
    remove_saved_data(post_id)
    return JSONResponse(content={"data": post_id})   

@app.post("/api/save-prompt/")
async def save_prompt(data: PromptRequest):
    add_prompt_history(data.query, data.asset_id)  
    return JSONResponse(content={"message": "Prompts saved"})

@app.post("/api/get-prompt-history/")
async def fetch_prompt_history(data: asset_req):
    history = get_prompt_history(data.asset_id)
    return JSONResponse(content={"data": history}, media_type="application/json")  

@app.delete("/api/clear-prompt-history/")
async def delete_prompt_history(data: asset_req):
    return clear_prompt_history(data.asset_id)

@app.get("/assets")
async def get_assets():
    assets = fetch_assets_from_db()
    print(assets)
    return JSONResponse(content={"data": assets})





