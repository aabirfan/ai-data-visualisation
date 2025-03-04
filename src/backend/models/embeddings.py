from sentence_transformers import SentenceTransformer, util
from bson.binary import Binary, BinaryVectorDtype
from datetime import datetime, timezone
import re

from .database import vector_collection  
from .database import collection as Telemetry
from models.llm_chart import generate_llm_chart_config, fill_llm_chart_data
from utils.data_calculations import calc_pipeline

model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)
nlp_model = SentenceTransformer("all-MiniLM-L6-v2")

######### EMBEDDINGS

def get_embedding(data, precision="float32"):
    return model.encode(data, precision=precision)

def generate_bson_vector(vector):
    return Binary.from_vector(vector, BinaryVectorDtype.FLOAT32)

def create_docs_with_bson_vector_embeddings(bson_float32, data):
    docs = []
    for i, (bson_f32_emb, query) in enumerate(zip(bson_float32, data)): 
        doc = {
            "_id": i,  
            "natural_query": query[0],  
            "mongo_query": query[1],    
            "BSON-Float32-Embedding": bson_f32_emb,
        }
        docs.append(doc)
    return docs

######### STORING TEMPLATE QUERY

def embed_query():
    queries = [
        [
          "Give me OBJECT values for dates X and Y",
          {
              "timestamp": "X",
              "metadata.name": "OBJECT"
          }
        ]
    ]

    natural_queries = [query[0] for query in queries]
    float32_embeddings = get_embedding(natural_queries, "float32")

    bson_float32_embeddings = [generate_bson_vector(f32_emb) for f32_emb in float32_embeddings]

    docs = create_docs_with_bson_vector_embeddings(bson_float32_embeddings, queries)
    vector_collection.insert_many(docs)  
    print("Query stored.")

######### SEARCHING QUERY TEMPLATE

def vector_search(user_query):
    query_embedding = get_embedding(user_query, precision="float32")
    bson_query_embedding = generate_bson_vector(query_embedding)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_search",
                "queryVector": bson_query_embedding,
                "path": "BSON-Float32-Embedding",
                "numCandidates": 10,
                "exact": False,
                "limit": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "natural_query": 1,
                "mongo_query": 1,
                "score": { "$meta": "vectorSearchScore" }
            }
        }
    ]

    results = list(vector_collection.aggregate(pipeline))

    if results:
        print(f"Matched Query: {results[0]['natural_query']}")
        return results[0]["mongo_query"], results[0]['natural_query']

    print("No match.")
    return None, None

######### EXTRACT VARIABLES 
#Fetch exisiting sensor names to perform a match
def get_existing_sensor_names():
    return Telemetry.distinct("metadata.name")

def extract_variables(user_query):
    
    # Date extraction
    date_pattern = r"\b\d{1,2}/\d{1,2}/\d{4}\b"
    dates = re.findall(date_pattern, user_query)

    if not dates:
        print("Could not extract valid dates.")
        return None, None, "Could not extract valid dates."

    # Convert dates
    mongo_dates = [
        datetime.strptime(date, "%d/%m/%Y").replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        for date in dates
    ]

    # Fetch sensor name
    sensor_names = get_existing_sensor_names()
    if not sensor_names:
        print("No sensor names found in database.")
        return None, None, "No sensor names found in database."

    # Find sensor match using text embeddings
    query_embedding = nlp_model.encode(user_query)
    sensor_embeddings = nlp_model.encode(sensor_names)

    similarity_scores = util.pytorch_cos_sim(query_embedding, sensor_embeddings)[0].tolist()
    
    #Best matching sensor through similarity scores
    best_match_index = similarity_scores.index(max(similarity_scores))
    best_match = sensor_names[best_match_index]

    print(f"Best Matched Sensor: {best_match}")

    return best_match, mongo_dates, None


######### FILL MONGO QUERY TEMPLATE

def fill_query(template_query, object_name, dates):
    if not template_query:
        print("No template query found")
        return None

    if not isinstance(template_query, dict):
        print(f"Template query is not a dictionary! It is: {type(template_query)}")
        return None

    filled_queries = []

    for date in dates:
        query_filled = template_query.copy()

        try:
            query_filled["timestamp"] = {
                "$gte": date.replace(hour=0, minute=0, second=0, tzinfo=timezone.utc),
                "$lt": date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            }
            query_filled["metadata.name"] = object_name
            filled_queries.append(query_filled)
        except KeyError:
            print(f"Template query is fields for date {date}!")
            return None

    return filled_queries  

######### QUERY EXECUTION

def execute_mongo_query(final_queries):
    results = []
    for query in final_queries:
        if not isinstance(query, dict):
            print(f" Query is NOT a dictionary! It is: {type(query)}")
            continue

        print(f"\nMongoDB Query:\n{query}")

        query_results = list(Telemetry.find(query, {"_id": 0}))

        if query_results:
            print("\nResults:")
            for doc in query_results:
                print(doc)
            results.extend(query_results)
        else:
            print(f"No data found for {query['timestamp']}.")
            results.append({"error": f"No data found for {query['timestamp']}."})

    return results

######### FULL RUN FOR SCRIPT

def process_user_query(user_query):
    query_template, matched_query = vector_search(user_query)

    if not query_template:
        return {"error": "No matching query template found."}

    object_name, dates, error = extract_variables(user_query)

    if error:
        return {"error": error}

    final_queries = fill_query(query_template, object_name, dates)

    if not final_queries:
        return {"error": "Query filling failed."}

    raw_results = execute_mongo_query(final_queries)

    if any("error" in res for res in raw_results):
        return {"error": raw_results[0]["error"]}

    sensor_data = [(doc["timestamp"], doc["value"]) for doc in raw_results]

    data_summary = calc_pipeline([val for _, val in sensor_data])
    print(f"DEBUG: data_summary: {data_summary}")
    print(f"DEBUG: data_summary.length: {getattr(data_summary, 'length', 'MISSING')}")

    
    llm_chart_config = generate_llm_chart_config(object_name, data_summary.length)


    final_chart = fill_llm_chart_data(llm_chart_config, sensor_data)

    return {"message": final_chart}


if __name__ == "__main__":
    embed_query()
