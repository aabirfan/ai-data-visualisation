from utils.data_calculations import calc_pipeline
from models.llm_chart import generate_llm_chart_config
from models.fill_chart import fill_pie_chart_data, fill_llm_chart_data


def generate_chart_from_query_results(user_query, query_results):
    if not query_results or not isinstance(query_results, list):
        return {"error": "No data retrieved from MongoDB."}

    sensor_names = list(set(
        entry["metadata"]["name"]
        for entry in query_results
        if "metadata" in entry and "name" in entry["metadata"]
    ))
    print(f"Sensors detected in data: {sensor_names}")

    sensor_values = [
        entry["value"]
        for entry in query_results
        if "value" in entry and isinstance(entry["value"], (int, float))
    ]

    data_summary = calc_pipeline(sensor_values)
    print(f"Stats: Std Dev: {data_summary.std_dev}, Avg: {data_summary.avg}, Median: {data_summary.median}, Count: {data_summary.length}")

    llm_result = generate_llm_chart_config(
        sensor_name="Comparison Chart",
        num_data_points=data_summary.length,
        query=user_query,
        summary_stats=data_summary
    )

    if not llm_result:
        return {"error": "Failed to generate chart config from LLM."}

    chart_type = llm_result["chart_type"]
    chart_config = llm_result["config"]

    if chart_type == "pie":
        return {"message": fill_pie_chart_data(query_results)}
    else:
        return {"message": fill_llm_chart_data(chart_config, query_results, sensor_label=sensor_names)}
