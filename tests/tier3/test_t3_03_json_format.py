"""
T3-03: JSON Format Output
Tier 3 Multi-Agent Test - JSON format output
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, DEFAULT_PROPERTY_ID, logger


async def run_test():
    """Test JSON format output for multi-agent query."""
    return await test_query(
        "T3-03: JSON Format Output",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Return the top 5 pages by views along with their title tags and indexability status in JSON format."
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
