"""
T1-05: Trend Analysis
Tier 1 Analytics Agent Test - Comparison/trend analysis
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, DEFAULT_PROPERTY_ID, logger


@pytest.mark.asyncio
async def test_trend_analysis():
    """Test trend analysis query."""
    result = await execute_query(
        "T1-05: Trend Analysis",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Calculate the average daily page views for the last 30 days and explain if traffic is stable."
        },
        expected_substring=None
    )
    assert result, "Test failed: Trend analysis query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_trend_analysis())
    sys.exit(0 if result else 1)
