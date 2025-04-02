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

def generate_llm_chart_config(sensor_name, num_data_points, query, summary_stats):
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
                    "beginAtZero": False,
                    "grid": {
                    "color": "rgba(255, 255, 255, 0.2)"},
                    "ticks": {
                    "precision": 0},
                    "suggestedMin": 0,  
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

### User Query:
"{query}"

### Data Summary:
- Count: {summary_stats.length}
- Mean: {summary_stats.avg}
- Median: {summary_stats.median}
- Std Dev: {summary_stats.std_dev}
- Range: [{summary_stats.min} → {summary_stats.max}]

### Chart Type Guidelines (fallback if unsure):
- **Pie**: When the user is asking for a *distribution* or *percent breakdown* of categories.
- **Bar**: When comparing values across discrete groups or categories.
- **Line**: When showing trends, changes, or progressions *over time*.
- **Scatter**: When plotting unaggregated raw points (often time vs value or x vs y).

### Output Format:
- Return **only** a valid JSON object representing a Chart.js configuration.
- Do **not** include markdown, explanations, or extra text.
- Use placeholders like `[]` for data and labels to be filled in later.
- Always include both `scales.y.min` and `scales.y.max` in the config.
- Use the actual observed range provided: `min = {summary_stats.min}`, `max = {summary_stats.max}`.
- Add a small buffer (~10%) around the min and max if needed to make the chart more readable.
- Do not use `suggestedMin` or `suggestedMax`; use explicit `min` and `max`.




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




