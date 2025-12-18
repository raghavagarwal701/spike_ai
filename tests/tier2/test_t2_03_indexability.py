"""
T2-03: Indexability Status
Tier 2 SEO Agent Test - Indexability grouping
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, logger


@pytest.mark.asyncio
async def test_indexability():
    """Test indexability status grouping."""
    result = await execute_query(
        "T2-03: Indexability Status",
        {
            "query": "Group all pages by indexability status and provide a count for each group."
        },
        expected_substring=None
    )
    assert result, "Test failed: Indexability status grouping did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_indexability())
    sys.exit(0 if result else 1)
