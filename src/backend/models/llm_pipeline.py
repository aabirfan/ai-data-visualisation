from utils.mongo_executor import execute_queries  
from utils.chart_utils import generate_chart_from_query_results, fill_pie_chart_data
from models.mongo_query_generation import generate_mongo_query_from_prompt


def process_llm_pipeline(user_query, asset_id):
    print(f"Pipeline 3 is running for: {user_query}")

    mongo_query = generate_mongo_query_from_prompt(user_query)
    if not mongo_query:
        return {"error": "Failed to generate MongoDB query."}

    print(f"Type of mongo query: {type(mongo_query)}")

    query_results = execute_queries([mongo_query], asset_id)

    return generate_chart_from_query_results(user_query, query_results)

