"""
T2-02: Title Tag Length
Tier 2 SEO Agent Test - Title tag length analysis
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, logger


async def run_test():
    """Test title tag length analysis."""
    return await test_query(
        "T2-02: Title Tag Length",
        {
            "query": "Which URLs have title tags longer than 60 characters?"
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
