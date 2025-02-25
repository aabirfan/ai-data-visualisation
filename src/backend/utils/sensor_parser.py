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

    if "ph" in query_text and not any(keyword in query_text for keyword in ["ph in", "ph out", "ph reg"]):
        return {"error": "Please specify 'pH in', 'pH out', or 'pH reg'."}  

    for sensor, keywords in SENSOR_KEYWORDS.items():
        if any(keyword in query_text for keyword in keywords):
            return sensor

    return {"error": "Unknown sensor type."}
