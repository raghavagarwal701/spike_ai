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

def test_tier1():
    # Common property ID
    property_id = "516747840"

    test_cases = [
        {
            "label": "Daily Metrics Breakdown",
            "query": "Give me a daily breakdown of page views, users, and sessions for the /pricing page over the last 14 days. Summarize any noticeable trends."
        },
        {
            "label": "Traffic Source Analysis",
            "query": "What are the top 5 traffic sources driving users to the pricing page in the last 30 days?"
        },
        {
            "label": "Calculated Insight (LLM Reasoning)",
            "query": "Calculate the average daily page views for the homepage over the last 30 days. Compare it to the previous 30-day period and explain whether traffic is increasing or decreasing."
        }
    ]

    for case in test_cases:
        payload = {
            "propertyId": property_id,
            "query": case["query"]
        }
        run_query(case["label"], payload)

if __name__ == "__main__":
    test_tier1()
