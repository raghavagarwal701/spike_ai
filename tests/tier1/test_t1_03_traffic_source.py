"""
T1-03: Traffic Source Analysis
Tier 1 Analytics Agent Test - Traffic source analysis
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, DEFAULT_PROPERTY_ID, logger


@pytest.mark.asyncio
async def test_traffic_source():
    """Test traffic source analysis query."""
    result = await execute_query(
        "T1-03: Traffic Source Analysis",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "What are the top 5 traffic sources driving users in the last 30 days?"
        },
        expected_substring=None
    )
    assert result, "Test failed: Traffic source analysis query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_traffic_source())
    sys.exit(0 if result else 1)
