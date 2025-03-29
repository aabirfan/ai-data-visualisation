import json
from datetime import datetime
from pymongo import ASCENDING
import google.generativeai as genai
import os
from .database import collection as Telemetry  
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv("../../.env.local")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

@lru_cache(maxsize=1)
def get_all_sensor_names():
    return Telemetry.distinct("metadata.name")

def generate_mongo_query_from_prompt(prompt):
    reference_query_sensors = {
        "metadata": {"name": {"$in": ["pH in", "pH out"]}},
        "timestamp": {
            "$gte": "2022-09-27T00:00:00Z",
            "$lt": "2022-09-27T23:59:59Z"
        },
        "sort": {"timestamp": 1}
    }

    reference_query_distribution = [
        {"$match": {
            "timestamp": {
                "$gte": "2022-09-27T00:00:00Z",
                "$lt": "2022-09-27T23:59:59Z"
            }
        }},
        {"$group": {"_id": "$value", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    known_sensors = get_all_sensor_names()
    sensor_list_string = "\n- " + "\n- ".join(sorted(known_sensors))

    system_instruction = (
        "You are an AI that generates MongoDB queries based on user requests. "
        "Your response **must be a JSON object** or a list of aggregation stages depending on context.\n\n"
        f"### Valid Sensor Names:\n{sensor_list_string}\n\n"
        "### 1. Standard Sensor Queries (Line/Bar Charts):\n"
        f"{json.dumps(reference_query_sensors, indent=2)}\n\n"
        "### 2. Pie Chart (Distribution Queries) [**Use a List!**]:\n"
        f"{json.dumps(reference_query_distribution, indent=2)}\n\n"
        "### Rules for Query Generation:\n"
        "- Resolve any fuzzy, approximate, or misspelled sensor names to the closest valid name from the list.\n"
        "- Time-based requests must include timestamp filtering.\n"
        "- Use `$in` if user asks for multiple sensors.\n"
        "- Pie charts must use an aggregation pipeline.\n"
        "- No markdown or explanations, only return valid MongoDB syntax."
        "- Only generate an aggregation pipeline (a list of stages) when the prompt mentions: distribution, proportion, or pie chart"
        "- Otherwise, always generate a standard MongoDB query (a JSON object)."
    )

    print(f"Sending prompt to LLM for query generation: {prompt}")

    try:
        response = model.generate_content(f"{system_instruction}\nUser Query: {prompt}")
        raw_response = response.text.strip()

        clean_response = raw_response.strip("```json").strip("```").strip()
        mongo_query = json.loads(clean_response)

        if isinstance(mongo_query, list):
            for stage in mongo_query:
                if "$match" in stage and "timestamp" in stage["$match"]:
                    ts = stage["$match"]["timestamp"]
                    if "$gte" in ts:
                        ts["$gte"] = datetime.fromisoformat(ts["$gte"].replace("Z", "+00:00"))
                    if "$lt" in ts:
                        ts["$lt"] = datetime.fromisoformat(ts["$lt"].replace("Z", "+00:00"))

        elif isinstance(mongo_query, dict) and "timestamp" in mongo_query:
            ts = mongo_query["timestamp"]
            if "$gte" in ts:
                ts["$gte"] = datetime.fromisoformat(ts["$gte"].replace("Z", "+00:00"))
            if "$lt" in ts:
                ts["$lt"] = datetime.fromisoformat(ts["$lt"].replace("Z", "+00:00"))

        print(f"Final MongoDB Query: {json.dumps(mongo_query, indent=2, default=str)}")
        return mongo_query

    except json.JSONDecodeError as e:
        print("LLM JSON Error:", str(e))
        return None
    except Exception as e:
        print("LLM Error:", str(e))
        return None
