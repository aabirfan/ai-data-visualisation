from models.database import collection as Telemetry
import re

SENSOR_NAMES_CACHE = None

def generate_keywords(sensor_name):
    variations = [
        sensor_name.lower(),
        sensor_name.replace(" ", ""),
        sensor_name.replace(" ", "").lower()
    ]
    
    return variations


def get_sensor_types():
    global SENSOR_NAMES_CACHE
    
    if SENSOR_NAMES_CACHE is None:
        print("INFO: Loading sensor names from database (lazy loading)...")
        SENSOR_NAMES_CACHE = list(Telemetry.distinct("metadata.name"))
        print(f"INFO: Loaded {len(SENSOR_NAMES_CACHE)} sensor names.")
        
        if SENSOR_NAMES_CACHE:
            print(f"DEBUG: First few sensors: {SENSOR_NAMES_CACHE[:5]}")
        else:
            print("WARNING: No sensor names found in database")
    
    return SENSOR_NAMES_CACHE

def extract_sensor(query_text):
    query_text = query_text.lower().strip()

    sensor_types = get_sensor_types()
    
    sensor_keywords_map = {}
    
    for sensor in sensor_types:
        sensor_keywords_map[sensor] = generate_keywords(sensor)
    
    for sensor, keywords in sensor_keywords_map.items():
        if any(keyword in query_text for keyword in keywords):
            if "distribution" in query_text or "pie chart" in query_text:
                print(f"INFO: Detected request for pie chart for sensor: {sensor}")
            return sensor
    
    if "distribution" in query_text or "sensor types" in query_text or "pie chart" in query_text:
        print("INFO: Detected request for a pie chart of all sensors. Fetching sensor types from DB.")
        if not sensor_types:
            print("ERROR: No sensor types found in the database.")
            return {"error": "No sensor types found."}
        return sensor_types  

    return {"error": "Unknown sensor type."}
