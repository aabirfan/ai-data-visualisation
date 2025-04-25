from utils.mongo_executor import execute_queries  
from utils.chart_utils import generate_chart_from_query_results, fill_pie_chart_data
from models.mongo_query_generation import generate_mongo_query_from_prompt


def process_llm_pipeline(user_query, asset_id, previous_prompt, isReply):
    print(f"Pipeline 3 is running for: {user_query}")

    if (isReply):
        mongo_query_result = generate_mongo_query_from_prompt(user_query, previous_prompt)
    else:
        mongo_query_result = generate_mongo_query_from_prompt(user_query, None)

    if not mongo_query_result:
        return {"error": "Failed to generate MongoDB query."}
    
    if isinstance(mongo_query_result, dict) and mongo_query_result.get("success") is False:
        return mongo_query_result

    raw_query = mongo_query_result["query"]
    chart_intent = mongo_query_result["intent"]

    print(f"Type of mongo query: {type(raw_query)}")

    query_results = execute_queries([raw_query], asset_id)

    if isinstance(query_results, dict) and (query_results.get("error") or query_results.get("success") is False):
        return query_results

    if (isReply):
        return generate_chart_from_query_results(user_query, query_results, None, previous_prompt)
    else:
        return generate_chart_from_query_results(user_query, query_results, None, None)

