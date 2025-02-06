SENSOR_KEYWORDS = {
    "pH": ["ph"],
    "Flow in total counter": ["flow", "liters"],
    "CO2": ["co2"],
    "Temperature": ["temperature", "temp"]
}

def extract_sensor(query_text):
    query_text = query_text.lower()
    for sensor, keywords in SENSOR_KEYWORDS.items():
        if any(keyword in query_text for keyword in keywords):
            return sensor
    return None 

