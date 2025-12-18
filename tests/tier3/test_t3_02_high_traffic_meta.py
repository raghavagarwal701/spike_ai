"""
T3-02: High Traffic Missing Meta
Tier 3 Multi-Agent Test - High traffic + SEO risk
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, DEFAULT_PROPERTY_ID, logger


async def run_test():
    """Test high traffic pages with missing meta descriptions."""
    return await test_query(
        "T3-02: High Traffic Missing Meta",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Which pages are in the top 20% by views but have missing or duplicate meta descriptions? Explain the SEO risk."
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
