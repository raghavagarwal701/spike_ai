"""
T1-01: Daily Active Users
Tier 1 Analytics Agent Test - Basic daily metrics
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, DEFAULT_PROPERTY_ID, logger


async def run_test():
    """Test basic daily active users query."""
    return await test_query(
        "T1-01: Daily Active Users",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "How many active users were there yesterday?"
        },
        expected_substring=None  # Accept any response (may be no data)
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
