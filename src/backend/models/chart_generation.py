import json
from collections import defaultdict
from datetime import datetime
import google.generativeai as genai
import os
import json

from dotenv import load_dotenv
load_dotenv("../../.env.local")


def llmPrompt(calculations):
    genai.configure(api_key=my_api_key)

    model = genai.GenerativeModel(
    "models/gemini-1.5-flash",
    system_instruction= "You are a bot providing only Chart.js configuration in JSON format, specifically designed for use in TypeScript. "
                        "The configuration should be a properly formatted JSON object" 
                        "Make sure to include only the chart configuration starting with the config and the rest of the Chart.js configuration as valid JSON. "
                        "Do not include any other text or code, only the JSON object. The JSON object should have keys and string values enclosed in double quotes. No dates, only raw example data")

    response = model.generate_content("Chart code for sensor data for one day.")

    try:
        json_data = json.loads(response.text) 
        print(response.text)
        return json_data  
    except json.JSONDecodeError as e:
        print("Error: Invalid JSON received from LLM:", e)
        return None 


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
                        "displayFormats": {
                            "hour": "HH"
                        },
                    },
                
                },
                "y": {
                    "grid": {
                        "color": "rgba(255, 255, 255, 0.2)",
                    }
                }
            }
        }
    }
    return json.dumps(chart_config)
