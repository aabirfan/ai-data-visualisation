from utils.date_parser import extract_date_range
from utils.sensor_parser import extract_sensor
from queries.general_queries import fetch_sensor_values



def process_sensor_query(query_text: str):
    start_date, end_date, error_message = extract_date_range(query_text)
    if error_message:
        return {"error": error_message}  

    sensor_name = extract_sensor(query_text)
    if isinstance(sensor_name, dict): 
        return sensor_name  

    query_type = (
        "total" if "total" in query_text else
        "average" if "average" in query_text or "avg" in query_text else
        "values"
    )

    return fetch_sensor_values(start_date, end_date, sensor_name, limit=50, query_type=query_type)


def process_llm_query(calculations):

    prompt = [
        f"You should only give out highcharts.js code. You are not given the raw data, but you are given statistical details.",
      ],

    return prompt
