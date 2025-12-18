"""
T3-03: JSON Format Output
Tier 3 Multi-Agent Test - JSON format output
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, DEFAULT_PROPERTY_ID, logger


@pytest.mark.asyncio
async def test_json_format():
    """Test JSON format output for multi-agent query."""
    result = await execute_query(
        "T3-03: JSON Format Output",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Return the top 5 pages by views along with their title tags and indexability status in JSON format."
        },
        expected_substring=None
    )
    assert result, "Test failed: JSON format output query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_json_format())
    sys.exit(0 if result else 1)
