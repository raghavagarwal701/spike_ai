"""
T1-02: Daily Breakdown (Multiple Metrics)
Tier 1 Analytics Agent Test - Multi-metric breakdown
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, DEFAULT_PROPERTY_ID, logger


async def run_test():
    """Test multi-metric daily breakdown query."""
    return await test_query(
        "T1-02: Daily Breakdown (Multiple Metrics)",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Give me a daily breakdown of page views, users, and sessions for the last 7 days."
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
