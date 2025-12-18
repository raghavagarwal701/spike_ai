import asyncio
import aiohttp
import json
import sys
import logging
import time

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8080/query"

async def test_query(name, payload, expected_substring=None):
    logger.info(f"\n--- Testing: {name} ---")
    logger.info(f"Query: {payload['query']}")
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(BASE_URL, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                elapsed_time = time.time() - start_time
                
                if response.status != 200:
                    logger.error(f"FAILED: HTTP {response.status} (took {elapsed_time:.2f}s)")
                    text = await response.text()
                    logger.error(f"Response: {text}")
                    return False
                
                data = await response.json()
                answer = data.get("answer", "")
                logger.info(f"Answer: {answer[:500]}...")  # Truncate for readability
                
                if expected_substring:
                    if expected_substring.lower() in answer.lower():
                        logger.info(f"PASSED: Expected content found. (took {elapsed_time:.2f}s)")
                        return True
                    else:
                        logger.error(f"FAILED: Expected '{expected_substring}' not found. (took {elapsed_time:.2f}s)")
                        return False
                else:
                    logger.info(f"PASSED: Response received. (took {elapsed_time:.2f}s)")
                    return True

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"ERROR: {e} (took {elapsed_time:.2f}s)")
            return False

# ============================================================================
# TIER 1: ANALYTICS AGENT TEST CASES (5 total)
# ============================================================================

async def run_tier1_tests():
    """Run all Tier 1 (Analytics Agent / GA4) tests."""
    results = []
    
    # Test 1: Basic daily metrics
    results.append(await test_query(
        "T1-01: Daily Active Users",
        {
            "propertyId": "516747840",
            "query": "How many active users were there yesterday?"
        },
        expected_substring=None  # Accept any response (may be no data)
    ))

    # Test 2: Multi-metric breakdown
    results.append(await test_query(
        "T1-02: Daily Breakdown (Multiple Metrics)",
        {
            "propertyId": "516747840",
            "query": "Give me a daily breakdown of page views, users, and sessions for the last 7 days."
        },
        expected_substring=None
    ))

    # Test 3: Traffic source analysis
    results.append(await test_query(
        "T1-03: Traffic Source Analysis",
        {
            "propertyId": "516747840",
            "query": "What are the top 5 traffic sources driving users in the last 30 days?"
        },
        expected_substring=None
    ))

    # Test 4: Page-specific query
    results.append(await test_query(
        "T1-04: Specific Page Analysis",
        {
            "propertyId": "516747840",
            "query": "How many page views did the homepage get in the last 14 days?"
        },
        expected_substring=None
    ))

    # Test 5: Comparison/trend analysis
    results.append(await test_query(
        "T1-05: Trend Analysis",
        {
            "propertyId": "516747840",
            "query": "Calculate the average daily page views for the last 30 days and explain if traffic is stable."
        },
        expected_substring=None
    ))

    return results

# ============================================================================
# TIER 2: SEO AGENT TEST CASES (5 total)
# ============================================================================

async def run_tier2_tests():
    """Run all Tier 2 (SEO Agent / Screaming Frog) tests."""
    results = []

    # Test 1: HTTPS filtering
    results.append(await test_query(
        "T2-01: Non-HTTPS URLs",
        {
            "query": "List 3 URLs that do not use HTTPS."
        },
        expected_substring="http"
    ))

    # Test 2: Title tag length
    results.append(await test_query(
        "T2-02: Title Tag Length",
        {
            "query": "Which URLs have title tags longer than 60 characters?"
        },
        expected_substring=None
    ))

    # Test 3: Indexability grouping
    results.append(await test_query(
        "T2-03: Indexability Status",
        {
            "query": "Group all pages by indexability status and provide a count for each group."
        },
        expected_substring=None
    ))

    # Test 4: Meta description analysis
    results.append(await test_query(
        "T2-04: Missing Meta Descriptions",
        {
            "query": "How many pages have missing or empty meta descriptions?"
        },
        expected_substring=None
    ))

    # Test 5: Combined condition query
    results.append(await test_query(
        "T2-05: Combined Condition Query",
        {
            "query": "Which URLs do not use HTTPS and have title tags longer than 60 characters?"
        },
        expected_substring=None
    ))

    return results

# ============================================================================
# TIER 3: MULTI-AGENT TEST CASES (5 total)
# ============================================================================

async def run_tier3_tests():
    """Run Tier 3 (Multi-Agent) tests."""
    results = []

    # Test 1: Basic cross-agent fusion
    results.append(await test_query(
        "T3-01: Top Pages + Title Tags",
        {
            "propertyId": "516747840",
            "query": "What are the top 10 pages by page views in the last 14 days, and what are their corresponding title tags?"
        },
        expected_substring=None
    ))

    # Test 2: High traffic + SEO risk
    results.append(await test_query(
        "T3-02: High Traffic Missing Meta",
        {
            "propertyId": "516747840",
            "query": "Which pages are in the top 20% by views but have missing or duplicate meta descriptions? Explain the SEO risk."
        },
        expected_substring=None
    ))

    # Test 3: JSON format output
    results.append(await test_query(
        "T3-03: JSON Format Output",
        {
            "propertyId": "516747840",
            "query": "Return the top 5 pages by views along with their title tags and indexability status in JSON format."
        },
        expected_substring=None
    ))

    # Test 4: Non-indexable high traffic pages
    results.append(await test_query(
        "T3-04: Non-Indexable High Traffic",
        {
            "propertyId": "516747840",
            "query": "Which non-indexable pages have the most page views in the last 14 days?"
        },
        expected_substring=None
    ))

    # Test 5: SEO risk assessment for top pages
    results.append(await test_query(
        "T3-05: SEO Risk Assessment",
        {
            "propertyId": "516747840",
            "query": "Identify potential SEO risks for the top 10 pages by traffic. Check for missing titles, long titles, or missing meta descriptions."
        },
        expected_substring=None
    ))

    return results

# ============================================================================
# MAIN
# ============================================================================

async def main():
    logger.info("=" * 60)
    logger.info("SPIKE AI - SYSTEM TEST SUITE")
    logger.info("=" * 60)

    # Run Tier 1 tests
    logger.info("\n" + "=" * 60)
    logger.info("TIER 1: ANALYTICS AGENT (GA4)")
    logger.info("=" * 60)
    tier1_results = await run_tier1_tests()
    tier1_passed = sum(tier1_results)
    tier1_total = len(tier1_results)

    # Run Tier 2 tests
    logger.info("\n" + "=" * 60)
    logger.info("TIER 2: SEO AGENT (SCREAMING FROG)")
    logger.info("=" * 60)
    tier2_results = await run_tier2_tests()
    tier2_passed = sum(tier2_results)
    tier2_total = len(tier2_results)

    # Run Tier 3 tests
    logger.info("\n" + "=" * 60)
    logger.info("TIER 3: MULTI-AGENT SYSTEM")
    logger.info("=" * 60)
    tier3_results = await run_tier3_tests()
    tier3_passed = sum(tier3_results)
    tier3_total = len(tier3_results)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tier 1 (Analytics):   {tier1_passed}/{tier1_total} passed")
    logger.info(f"Tier 2 (SEO):         {tier2_passed}/{tier2_total} passed")
    logger.info(f"Tier 3 (Multi-Agent): {tier3_passed}/{tier3_total} passed")
    
    total_passed = tier1_passed + tier2_passed + tier3_passed
    total_tests = tier1_total + tier2_total + tier3_total
    
    logger.info(f"\nOverall: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        logger.info("\nALL TESTS PASSED")
        sys.exit(0)
    else:
        logger.warning("\nSOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure aiohttp is installed for test runner
    try:
        import aiohttp
    except ImportError:
        logger.info("Installing aiohttp for test runner...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
        import aiohttp

    asyncio.run(main())
