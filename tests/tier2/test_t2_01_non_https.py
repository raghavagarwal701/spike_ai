"""
T2-01: Non-HTTPS URLs
Tier 2 SEO Agent Test - HTTPS filtering
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, logger


@pytest.mark.asyncio
async def test_non_https():
    """Test non-HTTPS URL detection."""
    result = await execute_query(
        "T2-01: Non-HTTPS URLs",
        {
            "query": "List 3 URLs that do not use HTTPS."
        },
        expected_substring="http"
    )
    assert result, "Test failed: Non-HTTPS URL detection did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_non_https())
    sys.exit(0 if result else 1)
