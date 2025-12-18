"""
T1-01: Daily Active Users
Tier 1 Analytics Agent Test - Basic daily metrics
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, DEFAULT_PROPERTY_ID, logger
import pytest


@pytest.mark.asyncio
async def test_daily_active_users():
    """Test basic daily active users query."""
    result = await execute_query(
        "T1-01: Daily Active Users",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "How many active users were there yesterday?"
        },
        expected_substring=None  # Accept any response (may be no data)
    )
    assert result, "Test failed: Daily active users query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_daily_active_users())
    sys.exit(0 if result else 1)
