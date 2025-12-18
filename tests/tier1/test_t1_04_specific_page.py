"""
T1-04: Specific Page Analysis
Tier 1 Analytics Agent Test - Page-specific query
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, DEFAULT_PROPERTY_ID, logger


async def run_test():
    """Test specific page analysis query."""
    return await test_query(
        "T1-04: Specific Page Analysis",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "How many page views did the homepage get in the last 14 days?"
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
