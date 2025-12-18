"""
T3-01: Top Pages + Title Tags
Tier 3 Multi-Agent Test - Basic cross-agent fusion
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, DEFAULT_PROPERTY_ID, logger


async def run_test():
    """Test top pages with corresponding title tags (cross-agent)."""
    return await test_query(
        "T3-01: Top Pages + Title Tags",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "What are the top 10 pages by page views in the last 14 days, and what are their corresponding title tags?"
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
