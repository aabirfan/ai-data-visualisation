from typing import Union
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI 
import google.generativeai as genai
from dotenv import load_dotenv


app = FastAPI()
load_dotenv("../../.env.local")
my_api_key = os.getenv("GOOGLE_API_KEY")
print("this is the key", my_api_key)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str


def llmPrompt(query: str):
    genai.configure(api_key=my_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(query)
    return response.text



@app.get("/")
def read_root():
    return {"Hello": "World test"}


@app.post("/prompt")
async def process_prompt(prompt_request: PromptRequest):
    query = prompt_request.prompt
    print("this is the query:", query)
    response = llmPrompt(query)
    return {"message": f"{response}"}


