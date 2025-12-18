"""
T2-04: Missing Meta Descriptions
Tier 2 SEO Agent Test - Meta description analysis
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, logger


async def run_test():
    """Test missing meta descriptions detection."""
    return await test_query(
        "T2-04: Missing Meta Descriptions",
        {
            "query": "How many pages have missing or empty meta descriptions?"
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
