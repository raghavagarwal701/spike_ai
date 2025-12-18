"""
T3-04: Non-Indexable High Traffic
Tier 3 Multi-Agent Test - Non-indexable high traffic pages
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, DEFAULT_PROPERTY_ID, logger


async def run_test():
    """Test non-indexable pages with high traffic."""
    return await test_query(
        "T3-04: Non-Indexable High Traffic",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Which non-indexable pages have the most page views in the last 14 days?"
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
