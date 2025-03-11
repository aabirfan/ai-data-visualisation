import json
from collections import defaultdict
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
from utils.data_calculations import calc_pipeline
from models.llm_chart import generate_llm_chart_config
from models.embeddings import process_user_query
from models.fill_chart import fill_llm_chart_data, fill_pie_chart_data


load_dotenv("../../.env.local")
my_api_key = os.getenv("GEMINI_API_KEY")

def parse_timestamp(timestamp_str):
    return datetime.fromisoformat(timestamp_str)

def manual_chart_builder(nums, sensor_name="Unknown Sensor"):
    labels = []
    data = []

    for items in nums:
        isotime, value = items
        if value != 0: 
            labels.append(str(isotime))  
            data.append(value) 

    iso_labels = [datetime.strptime(label, "%Y-%m-%d %H:%M:%S").isoformat() for label in labels]

    sensor_label_map = {
        "pH in": "PH In",
        "pH out": "PH Out",
        "pH reg": "PH Regulation",
        "CO2 rack remaining": "CO2 Remaining (KG)",
        "CO2 usage": "CO2 Usage (KG)",
        "Flocculant tank": "Flocculant Tank (L)",
        "Flocculant usage": "Flocculant Usage (ML)",
        "Flow in": "Flow In (L/h)",
        "Flow in total counter": "Flow In Total (L)",
        "Flow out": "Flow Out (L/h)",
        "Flow out total counter": "Flow Out Total (L)",
        "Turbidity in": "Turbidity In (NTU)",
        "Turbidity out": "Turbidity Out (NTU)"
    }

    normalized_sensor_name = sensor_name.strip()
    chart_label = sensor_label_map.get(normalized_sensor_name, "Unknown Sensor")

    chart_config = {
        "type": "line",
        "data": {
            "labels": iso_labels,
            "datasets": [{
                "label": chart_label,
                "data": data,
                "borderColor": "rgb(0, 243, 255)",
                "backgroundColor": "rgb(0, 243, 255)"
            }]
        },
        "options": {
            "scales": {  
                "x": {
                    "type": "time",
                    "time": {
                        "unit": "hour",
                        "displayFormats": {"hour": "HH"},
                    },
                },
                "y": {
                    "grid": {"color": "rgba(255, 255, 255, 0.2)"},
                }
            }
        }
    }
    return json.dumps(chart_config)

def map_query_to_chart_type(user_query):
    user_query = user_query.lower()

    if "distribution" in user_query or "percentage" in user_query or "pie" in user_query:
        print("DEBUG: Pie chart detected.")
        return "pie"
    elif "compare" in user_query:
        print("DEBUG: Line chart detected.")
        return "line"
    elif "trend" in user_query or "over time" in user_query:
        print("DEBUG: Line chart detected.")
        return "line"
    else:
        print("DEBUG: Bar chart detected.")
        return "bar"

    
def generate_llm_chart_config(sensor_name, num_data_points, user_query):
    chart_type = map_query_to_chart_type(user_query)  

    reference_chart = {
        "type": chart_type,
        "data": {
            "labels": [],  
            "datasets": [{
                "label": f"{sensor_name} Sensor Data",
                "data": [],
                "backgroundColor": [
                    "rgb(255, 99, 132)", "rgb(54, 162, 235)", "rgb(255, 206, 86)",
                    "rgb(75, 192, 192)", "rgb(153, 102, 255)", "rgb(255, 159, 64)"
                ] if chart_type == "pie" else "rgb(0, 243, 255)",  
                "borderWidth": 1 if chart_type == "pie" else 2
            }]
        },
        "options": {}
    }

    if chart_type == "pie":
        reference_chart["options"]["plugins"] = {
            "title": {"display": True, "text": f"{sensor_name} Value Distribution"}
        }
    
    print(f"DEBUG: Final Selected Chart Type: {chart_type}")
    return reference_chart

def generate_chart(query):
    sensor_data, sensor_name = process_user_query(query)

    if isinstance(sensor_data, dict) and "error" in sensor_data:
        return {"error": sensor_data["error"]}

    llm_chart_code = generate_llm_chart_config(sensor_name, len(sensor_data), query)

    if map_query_to_chart_type(query) == "pie":
        print("INFO: Generating pie chart format.")
        return {"message": fill_pie_chart_data(llm_chart_code, sensor_data)}

    return {"message": fill_llm_chart_data(llm_chart_code, sensor_data)} if llm_chart_code else {"error": "Failed to generate chart"}
