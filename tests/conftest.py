"""
Shared test utilities and configuration for Spike AI tests.
"""

import asyncio
import aiohttp
import time
import logging
import sys

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8080/query"

# Default property ID for GA4 tests
DEFAULT_PROPERTY_ID = "516747840"


async def test_query(name: str, payload: dict, expected_substring: str = None) -> bool:
    """
    Execute a test query against the API.
    
    Args:
        name: Name of the test case
        payload: Request payload with query and optional propertyId
        expected_substring: Optional substring to check in response
        
    Returns:
        True if test passed, False otherwise
    """
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


def run_single_test(test_func):
    """Helper to run a single async test function."""
    return asyncio.run(test_func())
