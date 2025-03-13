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

class ChartData(BaseModel):
    chartData: Any
    chartOptions: Any
    chartType: str
    date: int
    title: str
    description: str

class removeData(BaseModel):
    timestamp: int

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

    #Temporary, the prompt has to start with manual to receive a manual chart
    if query_request.query.lower().startswith("manual"):
        chart = manual_chart_builder(response, sensor_name=sensor_name)
        return {"message": chart}
    
    #Temporary, the prompt has to start with rag to receive a rag chart
    if query_request.query.lower().startswith("rag"):
        return process_user_query(query_request.query)  

    #PIPELINE 3
    return process_llm_pipeline(query_request.query)


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
    

@app.get("/get_chart_data")
async def process_getting_saved_charts():
   list = get_chart_data()
   print(list)
   return JSONResponse(content={"data": list})  

@app.post("/remove_saved_chart")
async def remove_saved_chart(data: removeData):
    post_id = data.timestamp
    remove_saved_data(post_id)
    return JSONResponse(content={"data": post_id})   

