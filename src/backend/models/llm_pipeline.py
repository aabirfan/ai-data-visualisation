from models.fill_chart import fill_llm_chart_data_pipeline3
from utils.data_calculations import calc_pipeline  
from models.llm_chart import generate_llm_chart_config
from models.fill_chart import fill_pie_chart_data
from models.mongo_queries import execute_pie_chart_query, execute_mongo_query, generate_mongo_query_from_prompt
from dotenv import load_dotenv


def process_llm_pipeline(user_query):
    print(f"Pipeline is running for: {user_query}")

    mongo_query = generate_mongo_query_from_prompt(user_query)
    if not mongo_query:
        return {"error": "Failed to generate MongoDB query."}

    print(f"DEBUG: Type of mongo_query BEFORE execution: {type(mongo_query)}")

    
    query_is_pie_chart = isinstance(mongo_query, list) and any("$group" in step for step in mongo_query)

    if query_is_pie_chart:

        sensor_data = execute_pie_chart_query(mongo_query)
    else:
        sensor_data = execute_mongo_query(mongo_query)

    if isinstance(sensor_data, dict) and "error" in sensor_data:
        return sensor_data  

    if not sensor_data or not isinstance(sensor_data, list):
        return {"error": "No data retrieved from MongoDB."}

    if len(sensor_data) == 0:
        return {"error": "Query returned no results."}

    print(f"First five data points extracted: {sensor_data[:5]}")

    if isinstance(sensor_data[0], dict) and "_id" in sensor_data[0] and "count" in sensor_data[0]:
        print("INFO: Detected pie chart data, calling fill_pie_chart_data().")
        return {"message": fill_pie_chart_data(sensor_data)}

    data_summary = calc_pipeline([entry["value"] for entry in sensor_data if "value" in entry])
    print(f"Summarized stats: Std Dev: {data_summary.std_dev}, Avg: {data_summary.avg}, Median: {data_summary.median}, Count: {data_summary.length}")

    sensor_label = "Sensor Value Distribution"

    chart_config = generate_llm_chart_config(sensor_label, data_summary.length, user_query)
    if not chart_config:
        return {"error": "LLM failed to generate Chart.js config."}

    return {"message": fill_llm_chart_data_pipeline3(chart_config, sensor_data, sensor_label)}
