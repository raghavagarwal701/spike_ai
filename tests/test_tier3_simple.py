import requests
import json

def run_query(label, payload):
    url = "http://localhost:8080/query"
    
    print(f"\n--- {label} ---")
    print(f"Query: {payload['query']}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response Body:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

def test_tier3():
    # Common property ID
    property_id = "516747840"

    test_cases = [
        {
            "label": "Analytics + SEO Fusion",
            # using 30 days as K
            "query": "What are the top 10 pages by page views in the last 30 days, and what are their corresponding title tags?"
        },
        {
            "label": "High Traffic, High Risk Pages",
            "query": "Which pages are in the top 20% by views but have missing or duplicate meta descriptions? Explain the SEO risk."
        },
        {
            "label": "Cross-Agent JSON Output",
            "query": "Return the top 5 pages by views along with their title tags and indexability status in JSON format."
        }
    ]

    for case in test_cases:
        payload = {
            "propertyId": property_id,
            "query": case["query"]
        }
        run_query(case["label"], payload)

if __name__ == "__main__":
    test_tier3()
