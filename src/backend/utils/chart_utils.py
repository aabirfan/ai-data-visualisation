from utils.data_calculations import calc_pipeline
from models.llm_chart import generate_llm_chart_config
from models.fill_chart import fill_pie_chart_data, fill_llm_chart_data

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

def generate_chart_from_query_results(user_query, query_results):
    if not query_results or not isinstance(query_results, list) or len(query_results) == 0:
        return {"error": "No data retrieved from MongoDB."}

    print(f"First five data points extracted: {query_results[:5]}")

    selected_chart_type = map_query_to_chart_type(user_query)
    query_is_pie_chart = selected_chart_type == "pie"

    if query_is_pie_chart:
        return {"message": fill_pie_chart_data(query_results)}

    sensor_names = list(set(entry["metadata"]["name"] for entry in query_results if "metadata" in entry and "name" in entry["metadata"]))
    print(f"DEBUG: Sensors detected in data: {sensor_names}")

    sensor_values = [entry["value"] for entry in query_results if "value" in entry and isinstance(entry["value"], (int, float))]

    data_summary = calc_pipeline(sensor_values)

    print(f"Stats: Std Dev: {data_summary.std_dev}, Avg: {data_summary.avg}, Median: {data_summary.median}, Count: {data_summary.length}")

    selected_chart_type = map_query_to_chart_type(user_query)
    print(f"DEBUG: Selected chart type for query '{user_query}': {selected_chart_type}")

    chart_config = generate_llm_chart_config("Comparison Chart", data_summary.length, user_query)

    return {"message": fill_llm_chart_data(chart_config, query_results, sensor_label=sensor_names)}
