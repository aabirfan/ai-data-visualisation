from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from utils.query_processor import process_sensor_query

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

def llmPrompt(query: str):
    genai.configure(api_key=my_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(query)
    return response.text

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
    return process_sensor_query(query_request.query.lower())
