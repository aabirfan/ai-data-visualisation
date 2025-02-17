import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv("../../.env.local")
MONGO_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGO_URI)
db = client["PlantDatabase"]

collection = db["Telemetry"]  
vector_collection = db["queries"]

