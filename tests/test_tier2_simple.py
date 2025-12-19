import requests
import json
import sys

def run_query(label, query_text):
    url = "http://localhost:8080/query"
    headers = {"Content-Type": "application/json"}
    payload = {"query": query_text}
    
    print(f"\n--- {label} ---")
    print(f"Query: {query_text}")
    
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

def test_tier2():
    # 1. Negative Test: Original query checking for non-secure pages with long titles
    # Expectation: "No URLs found..." because all pages with long titles likely use HTTPS
    run_query(
        "Test 1 (Negative Constraint)", 
        "Which URLs do not use HTTPS and have title tags longer than 60 characters?"
    )

    # 2. Positive Test: Checking for long titles regardless of protocol
    # Expectation: Should return a list of URLs (we verified via logs that titles > 60 exist)
    run_query(
        "Test 2 (Positive Data)", 
        "Which URLs have title tags longer than 60 characters?"
    )

    # 3. Indexability Overview
    run_query(
        "Indexability Overview",
        "Group all pages by indexability status and provide a count for each group with a brief explanation."
    )

    # 4. Calculated SEO Insight (LLM Reasoning)
    run_query(
        "Calculated SEO Insight",
        "Calculate the percentage of indexable pages on the site. Based on this number, assess whether the site’s technical SEO health is good, average, or poor."
    )

if __name__ == "__main__":
    test_tier2()
