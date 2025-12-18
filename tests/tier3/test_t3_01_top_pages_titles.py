"""
T3-01: Top Pages + Title Tags
Tier 3 Multi-Agent Test - Basic cross-agent fusion
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, DEFAULT_PROPERTY_ID, logger


@pytest.mark.asyncio
async def test_top_pages_titles():
    """Test top pages with corresponding title tags (cross-agent)."""
    result = await execute_query(
        "T3-01: Top Pages + Title Tags",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "What are the top 10 pages by page views in the last 14 days, and what are their corresponding title tags?"
        },
        expected_substring=None
    )
    assert result, "Test failed: Top pages with title tags query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_top_pages_titles())
    sys.exit(0 if result else 1)
