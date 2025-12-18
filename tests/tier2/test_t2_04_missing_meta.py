"""
T2-04: Missing Meta Descriptions
Tier 2 SEO Agent Test - Meta description analysis
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, logger


@pytest.mark.asyncio
async def test_missing_meta():
    """Test missing meta descriptions detection."""
    result = await execute_query(
        "T2-04: Missing Meta Descriptions",
        {
            "query": "How many pages have missing or empty meta descriptions?"
        },
        expected_substring=None
    )
    assert result, "Test failed: Missing meta descriptions detection did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_missing_meta())
    sys.exit(0 if result else 1)
