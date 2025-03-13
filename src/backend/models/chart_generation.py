import json
from collections import defaultdict
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
from utils.chart_utils import generate_chart_from_query_results


load_dotenv("../../.env.local")
my_api_key = os.getenv("GEMINI_API_KEY")

def parse_timestamp(timestamp_str):
    return datetime.fromisoformat(timestamp_str)
#MANUAL
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

    
#PIPELINE 2 & 3 CHART
def generate_chart(user_query, raw_results):
 return generate_chart_from_query_results(user_query, raw_results)
