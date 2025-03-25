from .database import chart_archive_collection as collection
import json
from pymongo.errors import PyMongoError
from fastapi.responses import JSONResponse


def addArchivedChart(chart_data: str):
    try:
        chart_dict = json.loads(chart_data)
        
        result = collection.insert_one(chart_dict)
        print(f"Chart archived successfully with ID: {result.inserted_id}")
    
    except json.JSONDecodeError:
        print("Failed to decode JSON. Please check the format of chart_data.")
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_chart_data(asset_id):
    try:
        charts = collection.find({"asset_id": asset_id})  
        charts_list = list(charts)  
        
        for chart in charts_list:
            chart["_id"] = str(chart["_id"])
        
        return charts_list 
        
    except Exception as e:
        return {"error": str(e)} 

def remove_saved_data(timestamp):
    try:
        result = collection.delete_one({"date": timestamp})
        
        if result.deleted_count > 0:
            print(f"Successfully removed {result.deleted_count} chart(s) with the timestamp {timestamp}")
        else:
            print(f"No chart found with the timestamp {timestamp}")
    
    except PyMongoError as e:
        print(f"MongoDB error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")