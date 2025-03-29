from datetime import datetime, timezone
from pymongo import ASCENDING
from models.database import collection as Telemetry  

#Converts timestamp fields in a query to UTC datetime objects.
def clean_query_timestamps(query):
    if isinstance(query, dict) and "timestamp" in query:
        if "$gte" in query["timestamp"] and isinstance(query["timestamp"]["$gte"], str):
            query["timestamp"]["$gte"] = datetime.fromisoformat(query["timestamp"]["$gte"].replace("Z", "+00:00"))
        if "$lt" in query["timestamp"] and isinstance(query["timestamp"]["$lt"], str):
            query["timestamp"]["$lt"] = datetime.fromisoformat(query["timestamp"]["$lt"].replace("Z", "+00:00"))

    return query

#Executes for pie chart data (format is different)
def execute_pie_chart_query(query):
    print("Executing pie chart.")
    
    # Convert timestamp strings in $match to datetime
    for stage in query:
        if "$match" in stage and "timestamp" in stage["$match"]:
            if "$gte" in stage["$match"]["timestamp"] and isinstance(stage["$match"]["timestamp"]["$gte"], str):
                stage["$match"]["timestamp"]["$gte"] = datetime.strptime(
                    stage["$match"]["timestamp"]["$gte"].replace("Z", ""),
                    "%Y-%m-%dT%H:%M:%S"
                ).replace(tzinfo=timezone.utc)

            if "$lt" in stage["$match"]["timestamp"] and isinstance(stage["$match"]["timestamp"]["$lt"], str):
                stage["$match"]["timestamp"]["$lt"] = datetime.strptime(
                    stage["$match"]["timestamp"]["$lt"].replace("Z", ""),
                    "%Y-%m-%dT%H:%M:%S"
                ).replace(tzinfo=timezone.utc)

    try:
        results = list(Telemetry.aggregate(query))
    except Exception as e:
        return {"error": "Aggregation query execution failed."}

    if not results:
        return {"error": "No distribution data available."}

    print(f"INFO: Retrieved {len(results)} records from aggregation.")

    patched_results = []
    for r in results:
        if isinstance(r.get("_id"), dict) and {"hour", "sensor"}.issubset(r["_id"]):
            hour = r["_id"]["hour"]
            sensor = r["_id"]["sensor"]
            date = query[0]["$match"]["timestamp"]["$gte"].date()

            timestamp = datetime(
                year=date.year, month=date.month, day=date.day, hour=hour, tzinfo=timezone.utc
            )

            patched_results.append({
                "timestamp": timestamp,
                "value": r.get("avgValue") or r.get("averageValue"),
                "metadata": {"name": sensor}
            })
        else:
            patched_results.append({
            "_id": str(r.get("_id", "Unknown")),
            "count": r.get("count", 0)
            })


    return patched_results

#Executes single query
def execute_query(query, asset_id):
    if not isinstance(query, (dict, list)):  
        print(f"ERROR: Query is not a valid MongoDB format! Type: {type(query)} -> Value: {query}")
        return {"error": "Invalid query format"}

    if isinstance(query, list) and any("$group" in step for step in query):
        return execute_pie_chart_query(query)  

    query = clean_query_timestamps(query)

    if isinstance(query, dict):
        query["metadata.asset_id"] = asset_id

    if "metadata" in query and isinstance(query["metadata"], dict) and "name" in query["metadata"]:
        sensor_filter = query["metadata"]["name"]
        query["metadata.name"] = sensor_filter  
        del query["metadata"]


    sort_field = query.pop("sort", None) if "sort" in query else None

    try:
        print(f"Executing MongoDB Query:\n{query}")
        if sort_field and isinstance(sort_field, dict):
            sort_list = [(k, v) for k, v in sort_field.items()]
            results = list(Telemetry.find(query).sort(sort_list))
        else:
            results = list(Telemetry.find(query))

    except Exception as e:
        print(f"ERROR: MongoDB query execution failed. Reason: {str(e)}")
        return {"error": "MongoDB query execution failed."}

    if not results:
        return {"error": "No matching data found."}

    print(f"INFO: Retrieved {len(results)} records.")
    return results

#Executes multiple queries
def execute_queries(filled_queries, asset_id):
    if not isinstance(filled_queries, list):
        return {"error": "Invalid query format"}

    results = []
    for query in filled_queries:
        query_results = execute_query(query, asset_id)  

        if query_results and "error" not in query_results:
            results.extend(query_results)
        else:
            print(f"INFO: No data found for query: {query}")

    return results
