"""
T3-04: Non-Indexable High Traffic
Tier 3 Multi-Agent Test - Non-indexable high traffic pages
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, DEFAULT_PROPERTY_ID, logger


@pytest.mark.asyncio
async def test_non_indexable_traffic():
    """Test non-indexable pages with high traffic."""
    result = await execute_query(
        "T3-04: Non-Indexable High Traffic",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Which non-indexable pages have the most page views in the last 14 days?"
        },
        expected_substring=None
    )
    assert result, "Test failed: Non-indexable high traffic query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_non_indexable_traffic())
    sys.exit(0 if result else 1)
