import json
from datetime import datetime, timezone
from pymongo import ASCENDING
import google.generativeai as genai
import os
from .database import collection as Telemetry  
from dotenv import load_dotenv

load_dotenv("../../.env.local")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

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

    system_instruction = (
        "You are an AI that generates MongoDB queries based on user requests. "
        "Your response **must be a JSON object** and follow one of these formats:\n\n"
        "### 1. Standard Sensor Queries (Line/Bar Charts):\n"
        f"{json.dumps(reference_query_sensors, indent=2)}\n\n"
        "### 2. Pie Chart (Distribution Queries) [**Use a List!**]:\n"
        f"{json.dumps(reference_query_distribution, indent=2)}\n\n"
        "### Rules for Query Generation:\n"
        "- **Time-based requests**: Always include 'timestamp' with '$gte' and '$lt'.\n"
        "- **Sensor selection**: If the user asks for multiple sensors, use '$in'.\n"
        "- **Comparisons**: If the query involves 'compare', return a query for multiple sensors.\n"
        "- **Pie Charts (Distribution Queries)**: **Use an aggregation pipeline!**\n"
        "  - **DO NOT** use 'metadata.name' directly.\n"
        "  - Instead, use `$group` to count occurrences.\n"
        "  - **DO NOT** include 'ALL_SENSORS' or 'REMOVE_METADATA' in metadata.name.\n"
        "- **Sorting**: Always include 'sort': { 'timestamp': 1 } for time-based queries.\n"
        "- **Only return a JSON object (or list for aggregation queries)—no explanations, markdown, or extra text.**"
    )

    print(f"DEBUG: Sending prompt to LLM for query generation: {prompt}")

    try:
        response = model.generate_content(f"{system_instruction}\nUser Query: {prompt}")

        if not response.text.strip():
            print("ERROR: LLM returned an empty query response.")
            return None

        clean_response = response.text.strip().strip("```json").strip("```")
        mongo_query = json.loads(clean_response)

        if isinstance(mongo_query, dict) and "metadata" in mongo_query and "name" in mongo_query["metadata"]:
            if mongo_query["metadata"]["name"] in ["None", "ALL_SENSORS", None]:
                print("INFO: LLM mistakenly included 'metadata.name'. Replacing with correct aggregation pipeline.")
                mongo_query = [  
                    {"$match": {"timestamp": mongo_query["timestamp"]}},  
                    {"$group": {"_id": "$metadata.name", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ]


        if isinstance(mongo_query, dict) and "timestamp" in mongo_query:
            if "$gte" in mongo_query["timestamp"]:
                mongo_query["timestamp"]["$gte"] = datetime.fromisoformat(
                    mongo_query["timestamp"]["$gte"].replace("Z", "+00:00")
                )
            if "$lt" in mongo_query["timestamp"]:
                mongo_query["timestamp"]["$lt"] = datetime.fromisoformat(
                    mongo_query["timestamp"]["$lt"].replace("Z", "+00:00")
                )

        print(f"DEBUG: Final MongoDB Query (Corrected): {json.dumps(mongo_query, indent=2, default=str)}")

        return mongo_query

    except json.JSONDecodeError as e:
        print("LLM JSON Error:", str(e))
        return None
    except Exception as e:
        print("LLM Error:", str(e))
        return None
    
def execute_pie_chart_query(query):
    print("INFO: Executing pie chart aggregation.")

    for stage in query:
        if "$match" in stage and "timestamp" in stage["$match"]:
            if "$gte" in stage["$match"]["timestamp"] and isinstance(stage["$match"]["timestamp"]["$gte"], str):
                stage["$match"]["timestamp"]["$gte"] = datetime.strptime(
                    stage["$match"]["timestamp"]["$gte"], "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=timezone.utc)
            if "$lt" in stage["$match"]["timestamp"] and isinstance(stage["$match"]["timestamp"]["$lt"], str):
                stage["$match"]["timestamp"]["$lt"] = datetime.strptime(
                    stage["$match"]["timestamp"]["$lt"], "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=timezone.utc)

    results = list(Telemetry.aggregate(query))  

    if not results:
        print("INFO: No results found for aggregation query.")
        return {"error": "No distribution data available."}

    print(f"INFO: Retrieved {len(results)} records from aggregation.")
    return results


def execute_mongo_query(query):
    print(f"Executing MongoDB Query: {json.dumps(query, indent=2, default=str)}")

    if not isinstance(query, dict):
        print(f"ERROR: Query is not a dictionary! Type: {type(query)} -> Value: {query}")
        return {"error": "Invalid query format"}

    if "timestamp" in query:
        if "$gte" in query["timestamp"] and isinstance(query["timestamp"]["$gte"], str):
            query["timestamp"]["$gte"] = datetime.fromisoformat(query["timestamp"]["$gte"].replace("Z", "+00:00"))
        if "$lt" in query["timestamp"] and isinstance(query["timestamp"]["$lt"], str):
            query["timestamp"]["$lt"] = datetime.fromisoformat(query["timestamp"]["$lt"].replace("Z", "+00:00"))

    if "metadata" in query and isinstance(query["metadata"], dict) and "name" in query["metadata"]:
        sensor_filter = query["metadata"]["name"]
        
        if isinstance(sensor_filter, dict) and "$in" in sensor_filter:
            sensor_names = sensor_filter["$in"]
            print(f"INFO: Querying for multiple sensors: {sensor_names}")

            query["metadata.name"] = {"$in": sensor_names}
            del query["metadata"] 

    sort_field = query.pop("sort", None) if "sort" in query else None

    print(f"Executing Final MongoDB Query:\n{json.dumps(query, indent=2, default=str)}")

    try:
        if sort_field and isinstance(sort_field, dict):
            sort_list = [(k, v) for k, v in sort_field.items()]
            results = list(Telemetry.find(query).sort(sort_list))  
        else:
            results = list(Telemetry.find(query))

    except Exception as e:
        return {"error": "MongoDB query execution failed."}

    if not results:
        return {"error": "No matching data found."}

    print(f"INFO: Retrieved {len(results)} records.")
    return results
