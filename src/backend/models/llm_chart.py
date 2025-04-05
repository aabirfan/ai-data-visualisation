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
        "Include a descriptive and dynamic `plugins.title.text` based on the user's query and sensor name. "
        "Do not include any explanations, extra text, or markdown. "
        "Use placeholders (`[]`) for labels and data to be filled dynamically later."
    )
)

def generate_llm_chart_config(sensor_name, num_data_points, query, summary_stats):
    reference_chart = {
        "type": "line",
        "data": {
            "labels": [],
            "datasets": [{
                "label": f"",
                "data": [],
                "borderColor": "rgb(0, 243, 255)",
                "backgroundColor": "rgb(0, 243, 255)"
            }]
        },
        "options": {
            "plugins": {
                "title": {
                "display": True,
                "text": "Fluctuation of pH in Throughout the Day",
            "font": {
                "size": 15,         
                "weight": "bold"  
            },
                "color": "white"
       }
            },
            "scales": {
                "x": {
                    "type": "category",
                    "labels": [],
                    "ticks": {"autoSkip": True, "maxTicksLimit": 10}
                },
                "y": {
                    "beginAtZero": False,
                    "grid": {"color": "rgba(255, 255, 255, 0.2)"},
                    "ticks": {"precision": 0}
                }
            }
        }
    }

    prompt = f"""
You are a Chart.js assistant. Your task is to choose the most suitable chart type for the user’s query and generate a complete Chart.js configuration in JSON format.

### Your Responsibilities:
- Select the chart type based on the user's intent and the provided data summary.
- Be flexible and context-aware: prioritize what *makes the most sense visually*.
- If you're unsure, fall back to the rules below.
- **IMPORTANT**: If the chart type is "pie", do NOT include `scales` in the configuration.
- **IMPORTANT**: Title must be clean and descriptive. Include the full sensor name and date if available.

### User Query:
"{query}"

### Sensor Name:
{sensor_name}

### Data Summary:
- Count: {summary_stats.length}
- Mean: {summary_stats.avg}
- Median: {summary_stats.median}
- Std Dev: {summary_stats.std_dev}
- Range: [{summary_stats.min} → {summary_stats.max}]

### Chart Type Guidelines:
- **Pie**: Use when showing *distribution* or *percent breakdown*.
- **Bar**: Use for comparing categories.
- **Line**: Use for changes over time.
- **Scatter**: Use for individual data points (XY).

### Output Format:
- Return **only** a valid JSON object representing a Chart.js configuration.
- Do **not** include markdown or extra explanation.
- Use placeholders (`[]`) for data and labels to be filled later.
- Do NOT include `"scales"` if the chart is a pie chart.
Add a descriptive title in `plugins.title.text` based on:
- the user's query
- the full list of sensors involved (e.g., “pH in vs pH out”)
- and the intent behind the chart (trend, comparison, distribution, etc.)


### Reference Format:
{json.dumps(reference_chart, indent=2)}
"""


    try:
        print(f"Sending request to LLM for '{sensor_name}' with summary stats")
        response = model.generate_content(prompt)

        if not response.text.strip():
            print("LLM returned empty config.")
            return None

        clean_response = response.text.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]

        chart_config = json.loads(clean_response)
        chart_type = chart_config.get("type", "bar")

        print(f"LLM selected chart type: {chart_type}")
        return {
            "chart_type": chart_type,
            "config": chart_config
        }

    except Exception as e:
        print("LLM Error (chart config generation):", str(e))
        return None
    
    
