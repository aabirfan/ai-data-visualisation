from .prompt_history import get_prompt_history
from utils.sensor_parser import get_sensor_types
from utils.date_parser import get_date_range
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")


def get_suggested_prompts(asset_id: str) -> list[str]:
    try:
        history_entries = get_prompt_history(asset_id)

        if history_entries:
            history_text = "\n".join(f"{i+1}. {entry['query']}" for i, entry in enumerate(history_entries))
            prompt = f"""
You are an assistant for a chart generation tool.

Suggest 3 simple and clear chart prompts based on the user's previous queries.
Each suggestion should:
- Be short and under 15 words
- Avoid technical terms or abstract language
- Be something a beginner would understand
- Avoid repeating ideas already seen in the history

Prompt History:
{history_text}

Return exactly 3 suggestions. No numbering or bullet points.
"""
        else:
            sensor_names = get_sensor_types()
            sensor_list = "\n- " + "\n- ".join(sensor_names[:30])

            start_date, end_date = get_date_range(asset_id)
            date_range_text = f"Available data ranges from {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}." if start_date and end_date else "Date range unknown."

            prompt = f"""
You are an assistant for a chart generation tool.

The user has not submitted any queries yet.

Here is a list of available sensor names:
{sensor_list}

{date_range_text}

Based on these sensors and available time range, suggest 3 beginner-friendly chart prompts.
Each suggestion should:
- Use specific sensor names from the list, but **do not wrap them in quotes**
- Include realistic and recent dates from the range if possible
- Be short (under 15 words)
- Focus on trends, comparisons, or breakdowns

Return exactly 3 suggestions. No numbering or bullet points.
"""

        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        if "\n" in raw_text:
            suggestions = [line.strip("• ").strip() for line in raw_text.splitlines() if line.strip()]
        else:
            suggestions = [s.strip() for s in raw_text.split(". ") if len(s.strip()) > 5]

        return suggestions[:3]

    except Exception as e:
        print(f"LLM prompt suggestion error: {e}")
        return [
            "pH in on the 27th September 2022", 
            "Show a line chart of Turbidity out 30/09/2022", 
            "PH distribution in September 2022"
        ]
