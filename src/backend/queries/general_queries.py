from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import lru_cache

load_dotenv("../../.env.local")
MONGO_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGO_URI)
db = client["PlantDatabase"]
collection = db["Telemetry"]  

SENSOR_UNITS = {
    "pH": "",
    "Flow in total counter": "L",  
    "CO2": "ppm",  
    "Temperature": "°C"  
}

@lru_cache(maxsize=50)  
def fetch_sensor_values(start_date, end_date, sensor_name, limit=None, query_type="values"):
    try:
        query = {"metadata.name": {"$regex": f"^{sensor_name}", "$options": "i"}}

        if start_date:
            date_range = {"$gte": datetime.strptime(start_date, "%Y-%m-%d")}
            if end_date and start_date != end_date:
                date_range["$lt"] = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            else:
                end_date = start_date  
                date_range["$lt"] = date_range["$gte"] + timedelta(days=1)

            query["timestamp"] = date_range

        print(f"\nDEBUG: Running MongoDB query:\n{query}")

        cursor = collection.find(query, {"timestamp": 1, "metadata.name": 1, "value": 1, "_id": 0})
        results = list(cursor)

        print("\nDEBUG: MongoDB Results:\n", results)

        if not results:
            return {"message": f"Sorry, no {sensor_name} data was found for {start_date}."}

        unit = SENSOR_UNITS.get(sensor_name, "")

        if start_date == end_date:
            date_text = f"on {start_date}"
        else:
            date_text = f"from {start_date} to {end_date}"

        if query_type == "total":
            total_value = sum(doc["value"] for doc in results if isinstance(doc["value"], (int, float)))
            return {"message": f"The total {sensor_name} value {date_text} is {round(total_value, 2)} {unit}."}

        elif query_type == "average":
            values = [doc["value"] for doc in results if isinstance(doc["value"], (int, float))]
            avg_value = sum(values) / len(values) if values else 0
            return {"message": f"The average {sensor_name} value {date_text} is {round(avg_value, 2)} {unit}."}

        elif query_type == "values":
            values_list = [str(doc["value"]) for doc in results if isinstance(doc["value"], (int, float))]
            formatted_values = ", ".join(values_list)

            return {
                "message": f"The recorded {sensor_name} values {date_text} are: {formatted_values} {unit}."
            }

    except Exception as e:
        return {"error": str(e)}
