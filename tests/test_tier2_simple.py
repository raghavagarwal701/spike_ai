import requests
import json

def test_tier2():
    url = "http://localhost:8080/query"
    headers = {"Content-Type": "application/json"}
    
    # SEO query (Tier 2) - typically does not require propertyId, but API builds might require logic checks
    # Using the example query from the problem statement
    payload = {
        "query": "Which URLs do not use HTTPS and have title tags longer than 60 characters?"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_tier2()
