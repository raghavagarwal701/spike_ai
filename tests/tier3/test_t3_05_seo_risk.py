"""
T3-05: SEO Risk Assessment
Tier 3 Multi-Agent Test - SEO risk assessment for top pages
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import test_query, DEFAULT_PROPERTY_ID, logger


async def run_test():
    """Test SEO risk assessment for top traffic pages."""
    return await test_query(
        "T3-05: SEO Risk Assessment",
        {
            "propertyId": DEFAULT_PROPERTY_ID,
            "query": "Identify potential SEO risks for the top 10 pages by traffic. Check for missing titles, long titles, or missing meta descriptions."
        },
        expected_substring=None
    )


if __name__ == "__main__":
    result = asyncio.run(run_test())
    sys.exit(0 if result else 1)
