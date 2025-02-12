from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai

from utils.query_processor import process_sensor_query
from utils.query_processor import process_llm_query

from utils.data_calculations import calc_pipeline

load_dotenv("../../.env.local")
my_api_key = os.getenv("GOOGLE_API_KEY")

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




generation_config = {
  "temperature": 1,
  "top_p": 1,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}


@app.get("/")
def read_root():
    return {"Hello": "World test"}

@app.post("/prompt")
async def process_prompt(prompt_request: QueryRequest):
    query = prompt_request.query
    response = llmPrompt(query)
    return {"message": response}

@app.post("/query")
async def process_query(query_request: QueryRequest):
    response = process_sensor_query(query_request.query)
    calculations = calc_pipeline(response)
    print("Calculations:", calculations.std_dev)  

    if calculations is None:
        return {"error": "Calculations returned None. Please check the calculation pipeline."}
    
    llm_response = await llmPrompt(calculations)
    return {"message": llm_response}


async def llmPrompt(calculations):
    genai.configure(api_key=my_api_key)
    model = genai.GenerativeModel(
    "models/gemini-1.5-flash",
    system_instruction= "You are a bot providing only Highcharts.js configuration in JSON format, specifically designed for use in TypeScript. "
                        "The configuration should be a properly formatted JSON object" 
                        "Make sure to include only the chart configuration starting with the 'chart' key and the rest of the Highcharts configuration as valid JSON. "
                        "Do not include any other text or code, only the JSON object. The JSON object should have keys and string values enclosed in double quotes. No dates, only raw example data")

    response = model.generate_content("Chart code for PH levels for one day.")
    ## TODO: Only example for now. Data calculations + prompt should be passed as a response below then fed with right data.

    print(response.text)
    return response.text
