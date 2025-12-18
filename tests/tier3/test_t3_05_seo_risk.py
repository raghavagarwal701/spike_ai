"""
T3-05: SEO Risk Assessment
Tier 3 Multi-Agent Test - SEO risk assessment for top pages
"""

import asyncio
import sys
import os

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import execute_query, DEFAULT_PROPERTY_ID, logger


@pytest.mark.asyncio
async def test_seo_risk():
    """Test SEO risk assessment for top traffic pages."""
    result = await execute_query(
        "T3-05: SEO Risk Assessment",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Identify potential SEO risks for the top 10 pages by traffic. Check for missing titles, long titles, or missing meta descriptions."
        },
        expected_substring=None
    )
    assert result, "Test failed: SEO risk assessment query did not succeed"


if __name__ == "__main__":
    result = asyncio.run(test_seo_risk())
    sys.exit(0 if result else 1)
