from .embeddings import vector_search, extract_variables, fill_query, execute_mongo_query

test_query = "Can you show me the flow in total counter values on 27/09/2022 and 28/09/2022?"

retrieved_mongo_query, _ = vector_search(test_query)  

object_name, dates, error = extract_variables(test_query)

if error:
    print(f"Error extracting variables: {error}")
else:
    final_queries = fill_query(retrieved_mongo_query, object_name, dates)

    if final_queries:
        result = execute_mongo_query(final_queries)
        print("\nQuery Execution Result:")
        print(result)
    else:
        print("\nQuery filling failed.")
