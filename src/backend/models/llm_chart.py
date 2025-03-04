import json
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict 
from datetime import datetime
import json

load_dotenv("../../.env.local")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    "models/gemini-1.5-flash",
    system_instruction=(
        "You are a bot providing only Chart.js configuration in JSON format, specifically designed for use in TypeScript. "
        "The configuration should be a properly formatted JSON object. "
        "Ensure the structure closely resembles the provided reference chart format. "
        "Do not include any explanations, extra text, or markdown. "
        "Use placeholders (`[]`) for labels and data to be filled dynamically later."
    )
)

def generate_llm_chart_config(sensor_name, num_data_points):
    reference_chart = {
        "type": "line",
        "data": {
            "labels": [],
            "datasets": [{
                "label": f"{sensor_name} Sensor Data",
                "data": [],
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
                        "displayFormats": {"hour": "HH"}
                    },
                },
                "y": {
                    "grid": {"color": "rgba(255, 255, 255, 0.2)"}
                }
            }
        }
    }

    prompt = f"""
    Generate a valid Chart.js configuration for visualizing {sensor_name} sensor data.

    Reference Example (Mimic this format but adjust for new data):
    {json.dumps(reference_chart, indent=2)}

    Context Information:
    - Sensor Name: {sensor_name}
    - Number of Data Points: {num_data_points}
    - Ensure placeholders (`[]`) for labels and data, which will be dynamically filled later.
    - DO NOT include explanations, markdown (```), or any surrounding text.
    """

    try:
        print(f"DEBUG: Sending request to LLM for {sensor_name} with {num_data_points} points")
        response = model.generate_content(prompt)

        if not response.text.strip():
            print("ERROR: LLM returned an empty response.")
            return None

        print(f"DEBUG: LLM Raw Response: {repr(response.text)}")

        clean_response = response.text.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:] 
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3] 

        print(f"DEBUG: Cleaned LLM Response: {repr(clean_response)}")

        chart_config = json.loads(clean_response)
        if "type" not in chart_config or "data" not in chart_config:
            raise ValueError("Invalid Chart.js configuration format")

        return chart_config

    except json.JSONDecodeError as e:
        print("LLM JSON Error:", str(e))
        return None
    except ValueError as e:
        print(f"ERROR: Invalid Chart.js config received. {str(e)}")
        return None
    except Exception as e:
        print("LLM Error:", str(e))
        return None

"""
def fill_llm_chart_data(chart_config, sensor_data):
    if not chart_config or not isinstance(chart_config, dict):
        print("ERROR: Invalid chart config")
        return None

    try:
        if not isinstance(sensor_data, list) or not all(isinstance(d, tuple) and len(d) == 2 for d in sensor_data):
            print("ERROR: sensor_data is not in the expected format (list of (timestamp, value) tuples)")
            return None

        labels = [datetime.strptime(str(data[0]), "%Y-%m-%d %H:%M:%S").isoformat() for data in sensor_data]
        values = [data[1] for data in sensor_data]

        if "data" not in chart_config or "datasets" not in chart_config["data"] or not chart_config["data"]["datasets"]:
            print("ERROR: Chart.js config is missing required fields")
            return None

        chart_config["data"]["labels"] = labels
        chart_config["data"]["datasets"][0]["data"] = values

        print("Successfully filled LLM-generated chart with sensor data")

        return json.dumps(chart_config)

    except Exception as e:
        print("ERROR while filling chart data:", str(e))
        return None

"""
### WORK IN PROGRESS (Seperate Lines for seperate dates)

def fill_llm_chart_data(chart_config, sensor_data):
    if not chart_config or not isinstance(chart_config, dict):
        print("ERROR: Invalid chart config")
        return None

    try:
        grouped_data = defaultdict(list)

        for timestamp, value in sensor_data:
            if isinstance(timestamp, datetime):  
                dt = timestamp
            else:
                dt = datetime.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S")

            date_str = dt.date().isoformat()  
            grouped_data[date_str].append((dt, value))

        chart_config["data"]["datasets"] = []
        unique_timestamps = set()
        colors = ["rgb(0, 243, 255)", "rgb(255, 99, 132)", "rgb(75, 192, 192)", "rgb(255, 206, 86)"]

        for idx, (date, values) in enumerate(grouped_data.items()):
            values.sort()  

            timestamps = [dt.isoformat() for dt, _ in values]
            sensor_values = [value for _, value in values]

            unique_timestamps.update(timestamps)

            dataset = {
                "label": f"{date} Data",
                "data": sensor_values,
                "borderColor": colors[idx % len(colors)],
                "backgroundColor": colors[idx % len(colors)]
            }

            chart_config["data"]["datasets"].append(dataset)

        chart_config["data"]["labels"] = sorted(unique_timestamps)

        print("CHart data is filled")
        return json.dumps(chart_config)

    except Exception as e:
        print("ERROR while filling chart data:", str(e))
        return None

