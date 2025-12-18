"""
T2-01: Non-HTTPS URLs
Tier 2 SEO Agent Test - HTTPS filtering
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, logger


async def run_test():
    """Test non-HTTPS URL detection."""
    return await test_query(
        "T2-01: Non-HTTPS URLs",
        {
            "query": "List 3 URLs that do not use HTTPS."
        },
        expected_substring="http"
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
