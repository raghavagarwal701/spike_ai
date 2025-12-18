"""
T1-03: Traffic Source Analysis
Tier 1 Analytics Agent Test - Traffic source analysis
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, DEFAULT_PROPERTY_ID, logger


async def run_test():
    """Test traffic source analysis query."""
    return await test_query(
        "T1-03: Traffic Source Analysis",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "What are the top 5 traffic sources driving users in the last 30 days?"
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
