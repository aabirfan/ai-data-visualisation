from sentence_transformers import SentenceTransformer
from bson.binary import Binary
from bson.binary import BinaryVectorDtype

from .database import vector_collection as collection


model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

def get_embedding(data, precision="float32"):
    return model.encode(data, precision=precision)

def generate_bson_vector(vector, vector_dtype):
    return Binary.from_vector(vector, vector_dtype) 

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

def embed_query():
    queries = [
        [
          "Show me the pH values 28 september 2022",
          "db.logs.find({'temperature': {'$gt': 50}}).sort('timestamp', -1).limit(5)"
        ]
    ]

    natural_queries = [query[0] for query in queries]
    float32_embeddings = get_embedding(natural_queries, "float32")

    bson_float32_embeddings = []
    
    for f32_emb in float32_embeddings:  
        bson_float32_embeddings.append(generate_bson_vector(f32_emb, BinaryVectorDtype.FLOAT32))

    for idx, query in enumerate(queries):  
        print(f"\nQuery: {query}")
        print(f"Float32 BSON: {bson_float32_embeddings[idx]}")

    docs = create_docs_with_bson_vector_embeddings(bson_float32_embeddings, queries)
    collection.insert_many(docs)  

######### SEARCHING

def vector_search(query):
    query_text = query

    query_float32_embeddings = get_embedding(query_text, precision="float32")
    query_bson_float32_embeddings = generate_bson_vector(query_float32_embeddings, BinaryVectorDtype.FLOAT32)

    pipelines = []
    for query_embedding, path in zip(
        [query_bson_float32_embeddings],
        ["BSON-Float32-Embedding"]
    ):
        pipeline = [
        {
            "$vectorSearch": {
                    "index": "vector_search",  
                    "queryVector": query_embedding,
                    "path": path,
                    "exact": True,
                    "limit": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "natural_query": 1,
                "mongo_query": 1,
                "score": {
                    "$meta": "vectorSearchScore"
                }
            }
        }
        ]
        pipelines.append(pipeline)

    for pipeline in pipelines:
        print(f"\nResults for {pipeline[0]['$vectorSearch']['path']}:")

        # Run the aggregation query, ensuring the pipeline is properly formatted
        try:
            results = collection.aggregate(pipeline)

            # Convert cursor to list to access results
            results_list = list(results)

            # Print all results for debugging
            for i in results_list:
                print(i)
        except Exception as e:
            print(f"Error during aggregation: {e}")
            return None

    # If results are found, return the mongo_query field of the first result
    if results_list:
        print(results_list[0].get("mongo_query"))
        return results_list[0].get("mongo_query")

    return None






