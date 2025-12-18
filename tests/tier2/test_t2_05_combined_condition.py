"""
T2-05: Combined Condition Query
Tier 2 SEO Agent Test - Combined condition query
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, logger


@pytest.mark.asyncio
async def test_combined_condition():
    """Test combined condition query (non-HTTPS + long titles)."""
    result = await execute_query(
        "T2-05: Combined Condition Query",
        {
            "query": "Which URLs do not use HTTPS and have title tags longer than 60 characters?"
        },
        expected_substring=None
    )
    assert result, "Test failed: Combined condition query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_combined_condition())
    sys.exit(0 if result else 1)
