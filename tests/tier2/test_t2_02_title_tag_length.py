"""
T2-02: Title Tag Length
Tier 2 SEO Agent Test - Title tag length analysis
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, logger


@pytest.mark.asyncio
async def test_title_tag_length():
    """Test title tag length analysis."""
    result = await execute_query(
        "T2-02: Title Tag Length",
        {
            "query": "Which URLs have title tags longer than 60 characters?"
        },
        expected_substring=None
    )
    assert result, "Test failed: Title tag length analysis did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_title_tag_length())
    sys.exit(0 if result else 1)
