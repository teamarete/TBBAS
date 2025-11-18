"""
Test script for MaxPreps scraper
Tests scraping specific dates with the updated Selenium-based scraper
"""

import sys
import logging
from datetime import datetime
from box_score_scraper import MaxPrepsBoxScoreScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_scraper():
    """Test MaxPreps scraper with specific dates"""

    # Initialize scraper
    logger.info("Initializing MaxPreps scraper...")
    scraper = MaxPrepsBoxScoreScraper(use_selenium=True)

    # Test dates from user (note: these dates are in 2024, not 2025)
    test_dates = [
        datetime(2024, 11, 14),  # November 14, 2024
        datetime(2024, 11, 15),  # November 15, 2024
    ]

    all_games = []

    for test_date in test_dates:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing date: {test_date.strftime('%m/%d/%Y')}")
        logger.info(f"{'='*60}")

        games = scraper.scrape_daily_scores(test_date)

        logger.info(f"\nResults for {test_date.strftime('%m/%d/%Y')}:")
        logger.info(f"  Total games found: {len(games)}")

        if games:
            logger.info(f"\n  Sample games:")
            for i, game in enumerate(games[:5]):  # Show first 5 games
                logger.info(f"    {i+1}. {game['team1_name']} {game['team1_score']} vs "
                           f"{game['team2_name']} {game['team2_score']}")

            if len(games) > 5:
                logger.info(f"    ... and {len(games) - 5} more games")
        else:
            logger.warning(f"  No games found for {test_date.strftime('%m/%d/%Y')}")

        all_games.extend(games)

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total dates tested: {len(test_dates)}")
    logger.info(f"Total games found: {len(all_games)}")

    if all_games:
        logger.info(f"\nSuccess! The scraper is working correctly.")
        return 0
    else:
        logger.error(f"\nWarning: No games found. Please check:")
        logger.error(f"  1. The dates have games scheduled on MaxPreps")
        logger.error(f"  2. Your internet connection")
        logger.error(f"  3. Chrome/ChromeDriver is properly installed")
        return 1

if __name__ == "__main__":
    try:
        exit_code = test_scraper()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nTest failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
