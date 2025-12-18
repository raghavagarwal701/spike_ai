"""
T1-04: Specific Page Analysis
Tier 1 Analytics Agent Test - Page-specific query
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, DEFAULT_PROPERTY_ID, logger


@pytest.mark.asyncio
async def test_specific_page():
    """Test specific page analysis query."""
    result = await execute_query(
        "T1-04: Specific Page Analysis",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "How many page views did the homepage get in the last 14 days?"
        },
        expected_substring=None
    )
    assert result, "Test failed: Specific page analysis query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_specific_page())
    sys.exit(0 if result else 1)
