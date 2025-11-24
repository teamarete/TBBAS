"""
Re-scrape November 14-22, 2025 to ensure complete game coverage
"""

from datetime import datetime
from app import app
from box_score_scraper import BoxScoreCollector
from update_rankings_with_records import update_rankings_with_records
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_complete_range():
    """Re-scrape Nov 14-22, 2025 for complete game coverage"""

    # All dates from Nov 14-22
    dates_to_scrape = [
        "11/14/2025",
        "11/15/2025",
        "11/16/2025",
        "11/17/2025",
        "11/18/2025",
        "11/19/2025",
        "11/20/2025",
        "11/21/2025",
        "11/22/2025"
    ]

    logger.info("="*70)
    logger.info("RE-SCRAPING COMPLETE DATE RANGE: Nov 14-22, 2025")
    logger.info("="*70)
    logger.info("")
    logger.info("This will find any games we missed in previous scrapes")
    logger.info("Duplicate games will be automatically filtered out")
    logger.info("")

    collector = BoxScoreCollector(app=app)

    total_new_games = 0
    for date_str in dates_to_scrape:
        logger.info(f"Scraping MaxPreps for {date_str}...")
        try:
            games = collector.collect_daily_box_scores(target_dates=[date_str])
            logger.info(f"  ✓ Found {len(games)} games for {date_str} (new games only, duplicates filtered)")
            total_new_games += len(games)
        except Exception as e:
            logger.error(f"  ✗ Error scraping {date_str}: {e}")

    logger.info("")
    logger.info(f"Total NEW games added: {total_new_games}")
    logger.info("(Note: Database automatically filters duplicate games)")
    logger.info("")

    # Update records
    logger.info("Updating rankings with complete game records...")
    update_rankings_with_records()
    logger.info("✓ Rankings updated with all available games!")

    logger.info("="*70)
    logger.info("COMPLETE RE-SCRAPE FINISHED")
    logger.info("="*70)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Check rankings.json to verify all ranked teams have records")
    logger.info("2. View website to confirm records are displaying")
    logger.info("3. Any teams still without records likely haven't played yet")

if __name__ == '__main__':
    scrape_complete_range()
