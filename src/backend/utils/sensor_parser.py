from models.database import collection as Telemetry

SENSOR_KEYWORDS = {
    "pH in": ["ph in"],
    "pH out": ["ph out"],
    "pH reg": ["ph reg", "ph regulation"],
    "Flow in": ["flow in"],
    "Flow out": ["flow out"],
    "Flow in total counter": ["flow in total", "flow counter in"],
    "Flow out total counter": ["flow out total", "flow counter out"],
    "CO2 usage": ["co2 usage"],
    "CO2 rack remaining": ["co2 rack"],
    "Flocculant tank": ["flocculant tank"],
    "Flocculant usage": ["flocculant usage"],
    "Turbidity in": ["turbidity in"],
    "Turbidity out": ["turbidity out"]
}

def extract_sensor(query_text):
    query_text = query_text.lower().strip()

    for sensor, keywords in SENSOR_KEYWORDS.items():
        if any(keyword in query_text for keyword in keywords):
            if "distribution" in query_text or "pie chart" in query_text:
                print(f"INFO: Detected request for pie chart for sensor: {sensor}")
                return sensor  
            return sensor  

    if "distribution" in query_text or "sensor types" in query_text or "pie chart" in query_text:
        print("INFO: Detected request for a pie chart of all sensors. Fetching sensor types from DB.")
        sensor_types = Telemetry.distinct("metadata.name")
        if not sensor_types:
            print("ERROR: No sensor types found in the database.")
            return {"error": "No sensor types found."}
        return sensor_types  


    if "ph" in query_text and not any(keyword in query_text for keyword in ["ph in", "ph out", "ph reg"]):
        return {"error": "Please specify 'pH in', 'pH out', or 'pH reg'."}  

    for sensor, keywords in SENSOR_KEYWORDS.items():
        if any(keyword in query_text for keyword in keywords):
            return sensor

    return {"error": "Unknown sensor type."}

