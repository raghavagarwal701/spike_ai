"""
T1-05: Trend Analysis
Tier 1 Analytics Agent Test - Comparison/trend analysis
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, DEFAULT_PROPERTY_ID, logger


async def run_test():
    """Test trend analysis query."""
    return await test_query(
        "T1-05: Trend Analysis",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Calculate the average daily page views for the last 30 days and explain if traffic is stable."
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
