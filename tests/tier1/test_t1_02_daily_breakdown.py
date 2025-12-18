"""
T1-02: Daily Breakdown (Multiple Metrics)
Tier 1 Analytics Agent Test - Multi-metric breakdown
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, DEFAULT_PROPERTY_ID, logger


@pytest.mark.asyncio
async def test_daily_breakdown():
    """Test multi-metric daily breakdown query."""
    result = await execute_query(
        "T1-02: Daily Breakdown (Multiple Metrics)",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Give me a daily breakdown of page views, users, and sessions for the last 7 days."
        },
        expected_substring=None
    )
    assert result, "Test failed: Daily breakdown query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_daily_breakdown())
    sys.exit(0 if result else 1)
