"""
T3-02: High Traffic Missing Meta
Tier 3 Multi-Agent Test - High traffic + SEO risk
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, DEFAULT_PROPERTY_ID, logger


@pytest.mark.asyncio
async def test_high_traffic_meta():
    """Test high traffic pages with missing meta descriptions."""
    result = await execute_query(
        "T3-02: High Traffic Missing Meta",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Which pages are in the top 20% by views but have missing or duplicate meta descriptions? Explain the SEO risk."
        },
        expected_substring=None
    )
    assert result, "Test failed: High traffic missing meta query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_high_traffic_meta())
    sys.exit(0 if result else 1)
