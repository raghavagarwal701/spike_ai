import requests
import json

def test_tier1():
    url = "http://localhost:8080/query"
    headers = {"Content-Type": "application/json"}
    
    # Replace with a valid property ID if known, otherwise this might fail or mock response
    # Using the example property ID from the problem statement
    payload = {
        "propertyId": "516747840", 
        "query": "What are the total active users over the last 30 days?"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_tier1()
