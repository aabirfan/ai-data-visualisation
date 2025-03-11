import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

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

def generate_llm_chart_config(sensor_name, num_data_points, query):
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
                    "type": "category",
                    "labels": [],
                    "ticks": {"autoSkip": True, "maxTicksLimit": 10}
                },
                "y": {
                    "grid": {"color": "rgba(255, 255, 255, 0.2)"}
                }
            }
        }
    }

    prompt = f"""
    Based on the following user query, determine the best chart type and generate a valid Chart.js configuration.

    **User Query:** "{query}"
    **Sensor Name:** {sensor_name}
    **Number of Data Points:** {num_data_points}

    **Guidelines for Selecting Chart Type:**
    - **Line Chart** (default): Used for continuous time-series data.
    - **Bar Chart**: Use if comparing categories or summing values per category.
    - **Scatter Plot**: Use if plotting individual data points without continuous trends.
    - **Pie Chart**: Use if showing percentage breakdowns of categories.
    
    **Format Rules:**
    - The output **must be a valid JSON object**.
    - Use `"type"` to specify the correct chart type.
    - Labels should match the dataset structure.

    **Example Format:**
    {json.dumps(reference_chart, indent=2)}
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

        chart_config = json.loads(clean_response)

        if "type" not in chart_config or "data" not in chart_config:
            raise ValueError("Invalid Chart.js configuration format")

        print(f"DEBUG: LLM Selected Chart Type: {chart_config['type']}")
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



