"""
T2-03: Indexability Status
Tier 2 SEO Agent Test - Indexability grouping
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, logger


async def run_test():
    """Test indexability status grouping."""
    return await test_query(
        "T2-03: Indexability Status",
        {
            "query": "Group all pages by indexability status and provide a count for each group."
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
