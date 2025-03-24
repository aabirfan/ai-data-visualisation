from .database import prompt_history_collection as collection
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime
import pytz


def add_prompt_history(query: str, asset_id: str):
    try:
        timestamp = datetime.utcnow()
        entry = {"query": query, "timestamp": timestamp, "asset_id": asset_id }
        
        result = collection.insert_one(entry)  
        
        if result.inserted_id is None:
            raise HTTPException(status_code=500)

        if collection.count_documents({}) > 10:
            oldest_entry = collection.find().sort("timestamp", 1).limit(1)
            collection.delete_one({"_id": oldest_entry[0]["_id"]})

    except PyMongoError as e:
        raise HTTPException(status_code=500)

def get_prompt_history(asset_id):
    try:
        history = list(
            collection.find({"asset_id": asset_id}, {"_id": 0, "query": 1, "timestamp": 1})
            .sort("timestamp", 1)
            .limit(10)
        )

        local_tz = pytz.timezone("Europe/Oslo") 
        for entry in history:
            if "timestamp" in entry and isinstance(entry["timestamp"], datetime):
                entry["timestamp"] = entry["timestamp"].replace(tzinfo=pytz.utc).astimezone(local_tz).isoformat()

        return history if history else []

    except PyMongoError as e:
        raise HTTPException(status_code=500)
    
def clear_prompt_history():
    try:
        collection.delete_many({})  
        return 
    except PyMongoError as e:
        raise HTTPException(status_code=500)

