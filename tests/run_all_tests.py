"""
Main Test Runner - Spike AI System Test Suite

Runs all test cases across all tiers and provides a summary.
Can also run individual tiers or tests.

Usage:
    python tests/run_all_tests.py           # Run all tests
    python tests/run_all_tests.py tier1     # Run Tier 1 tests only
    python tests/run_all_tests.py tier2     # Run Tier 2 tests only
    python tests/run_all_tests.py tier3     # Run Tier 3 tests only
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import logger

# Import Tier 1 tests
from tests.tier1.test_t1_01_daily_active_users import test_daily_active_users as t1_01
from tests.tier1.test_t1_02_daily_breakdown import test_daily_breakdown as t1_02
from tests.tier1.test_t1_03_traffic_source import test_traffic_source as t1_03
from tests.tier1.test_t1_04_specific_page import test_specific_page as t1_04
from tests.tier1.test_t1_05_trend_analysis import test_trend_analysis as t1_05

# Import Tier 2 tests
from tests.tier2.test_t2_01_non_https import test_non_https as t2_01
from tests.tier2.test_t2_02_title_tag_length import test_title_tag_length as t2_02
from tests.tier2.test_t2_03_indexability import test_indexability as t2_03
from tests.tier2.test_t2_04_missing_meta import test_missing_meta as t2_04
from tests.tier2.test_t2_05_combined_condition import test_combined_condition as t2_05

# Import Tier 3 tests
from tests.tier3.test_t3_01_top_pages_titles import test_top_pages_titles as t3_01
from tests.tier3.test_t3_02_high_traffic_meta import test_high_traffic_meta as t3_02
from tests.tier3.test_t3_03_json_format import test_json_format as t3_03
from tests.tier3.test_t3_04_non_indexable_traffic import test_non_indexable_traffic as t3_04
from tests.tier3.test_t3_05_seo_risk import test_seo_risk as t3_05


async def run_test_safely(test_func, test_name):
    """Run a test and catch any assertion errors, returning pass/fail."""
    try:
        await test_func()
        return True
    except AssertionError as e:
        logger.error(f"Test {test_name} failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Test {test_name} errored: {e}")
        return False


async def run_tier1_tests():
    """Run all Tier 1 (Analytics Agent / GA4) tests."""
    results = []
    results.append(await run_test_safely(t1_01, "T1-01"))
    results.append(await run_test_safely(t1_02, "T1-02"))
    results.append(await run_test_safely(t1_03, "T1-03"))
    results.append(await run_test_safely(t1_04, "T1-04"))
    results.append(await run_test_safely(t1_05, "T1-05"))
    return results


async def run_tier2_tests():
    """Run all Tier 2 (SEO Agent / Screaming Frog) tests."""
    results = []
    results.append(await run_test_safely(t2_01, "T2-01"))
    results.append(await run_test_safely(t2_02, "T2-02"))
    results.append(await run_test_safely(t2_03, "T2-03"))
    results.append(await run_test_safely(t2_04, "T2-04"))
    results.append(await run_test_safely(t2_05, "T2-05"))
    return results


async def run_tier3_tests():
    """Run Tier 3 (Multi-Agent) tests."""
    results = []
    results.append(await run_test_safely(t3_01, "T3-01"))
    results.append(await run_test_safely(t3_02, "T3-02"))
    results.append(await run_test_safely(t3_03, "T3-03"))
    results.append(await run_test_safely(t3_04, "T3-04"))
    results.append(await run_test_safely(t3_05, "T3-05"))
    return results


async def main(tier_filter=None):
    """
    Run test suite.
    
    Args:
        tier_filter: Optional filter for specific tier ('tier1', 'tier2', 'tier3')
    """
    # Ensure aiohttp is installed
    try:
        import aiohttp
    except ImportError:
        logger.info("Installing aiohttp for test runner...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])

    logger.info("=" * 60)
    logger.info("SPIKE AI - SYSTEM TEST SUITE")
    logger.info("=" * 60)

    tier1_results = []
    tier2_results = []
    tier3_results = []

    # Run Tier 1 tests
    if tier_filter is None or tier_filter == 'tier1':
        logger.info("\n" + "=" * 60)
        logger.info("TIER 1: ANALYTICS AGENT (GA4)")
        logger.info("=" * 60)
        tier1_results = await run_tier1_tests()

    # Run Tier 2 tests
    if tier_filter is None or tier_filter == 'tier2':
        logger.info("\n" + "=" * 60)
        logger.info("TIER 2: SEO AGENT (SCREAMING FROG)")
        logger.info("=" * 60)
        tier2_results = await run_tier2_tests()

    # Run Tier 3 tests
    if tier_filter is None or tier_filter == 'tier3':
        logger.info("\n" + "=" * 60)
        logger.info("TIER 3: MULTI-AGENT SYSTEM")
        logger.info("=" * 60)
        tier3_results = await run_tier3_tests()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    tier1_passed = sum(tier1_results) if tier1_results else 0
    tier1_total = len(tier1_results) if tier1_results else 0
    tier2_passed = sum(tier2_results) if tier2_results else 0
    tier2_total = len(tier2_results) if tier2_results else 0
    tier3_passed = sum(tier3_results) if tier3_results else 0
    tier3_total = len(tier3_results) if tier3_results else 0
    
    if tier1_results:
        logger.info(f"Tier 1 (Analytics):   {tier1_passed}/{tier1_total} passed")
    if tier2_results:
        logger.info(f"Tier 2 (SEO):         {tier2_passed}/{tier2_total} passed")
    if tier3_results:
        logger.info(f"Tier 3 (Multi-Agent): {tier3_passed}/{tier3_total} passed")
    
    total_passed = tier1_passed + tier2_passed + tier3_passed
    total_tests = tier1_total + tier2_total + tier3_total
    
    logger.info(f"\nOverall: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        logger.info("\nALL TESTS PASSED")
        sys.exit(0)
    else:
        logger.warning("\nSOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    tier_filter = None
    if len(sys.argv) > 1:
        tier_filter = sys.argv[1].lower()
        if tier_filter not in ['tier1', 'tier2', 'tier3']:
            logger.error(f"Invalid tier filter: {tier_filter}")
            logger.error("Usage: python run_all_tests.py [tier1|tier2|tier3]")
            sys.exit(1)
    
    asyncio.run(main(tier_filter))
