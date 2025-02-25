from models.general_queries import fetch_embedded_queries
 
test_query = "Show me the pH in values 27 September 2022"
result = fetch_embedded_queries(test_query)

print("Test Result:", result)
