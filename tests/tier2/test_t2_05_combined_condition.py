"""
T2-05: Combined Condition Query
Tier 2 SEO Agent Test - Combined condition query
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, logger


async def run_test():
    """Test combined condition query (non-HTTPS + long titles)."""
    return await test_query(
        "T2-05: Combined Condition Query",
        {
            "query": "Which URLs do not use HTTPS and have title tags longer than 60 characters?"
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
