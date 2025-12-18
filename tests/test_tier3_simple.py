import requests
import json

def test_tier3():
    url = "http://localhost:8080/query"
    headers = {"Content-Type": "application/json"}
    
    # Multi-agent query (Tier 3)
    # Using the example query from the problem statement
    payload = {
        "query": "What are the top 10 pages by views in the last 14 days, and what are their corresponding title tags?"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_tier3()
