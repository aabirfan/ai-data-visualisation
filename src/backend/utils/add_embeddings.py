from models.embeddings import get_embedding, generate_bson_vector, vector_collection

# EMBED AND ADD QUERY TO VECTOR DB
def embed_query():
    queries = [
    [
        "Show me the OBJECT 1 and OBJECT 2 values on X",
        {
            "timestamp": {
                "$gte": "X TIME_OF_DAY START",
                "$lte": "X TIME_OF_DAY END"
            },
            "metadata.name": {
                "$in": ["OBJECT 1", "OBJECT 2"]
            }
        }
    ]
]

    # Extract natural queries
    natural_queries = [query[0] for query in queries]
    
    # Get embeddings for the natural queries
    float32_embeddings = get_embedding(natural_queries, precision="float32")

    # Generate BSON vector embeddings
    bson_float32_embeddings = [generate_bson_vector(f32_emb) for f32_emb in float32_embeddings]

    # Create documents with the embedding and MongoDB query
    docs = []
    for (bson_f32_emb, query) in zip(bson_float32_embeddings, queries):
        doc = {
            "natural_query": query[0],  # The natural query text
            "mongo_query": query[1],    # The MongoDB query as an object
            "BSON-Float32-Embedding": bson_f32_emb,  # The BSON vector
        }
        docs.append(doc)
    
    # Insert documents into the vector collection
    vector_collection.insert_many(docs)  
    
    print("Query stored.")

if __name__ == "__main__":
    embed_query()
