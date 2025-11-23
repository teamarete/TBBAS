"""
Scrape missing game dates (Nov 19-22, 2025) and update records
"""

from datetime import datetime, timedelta
from app import app
from box_score_scraper import BoxScoreCollector
from update_rankings_with_records import update_rankings_with_records
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_missing_dates():
    """Scrape games from Nov 19-22, 2025"""

    # Dates to scrape
    dates_to_scrape = [
        "11/19/2025",
        "11/20/2025",
        "11/21/2025",
        "11/22/2025"
    ]

    logger.info("="*70)
    logger.info("SCRAPING MISSING DATES: Nov 19-22, 2025")
    logger.info("="*70)
    logger.info("")

    collector = BoxScoreCollector(app=app)

    total_games = 0
    for date_str in dates_to_scrape:
        logger.info(f"Scraping games for {date_str}...")
        try:
            games = collector.collect_daily_box_scores(target_dates=[date_str])
            logger.info(f"  ✓ Found {len(games)} games for {date_str}")
            total_games += len(games)
        except Exception as e:
            logger.error(f"  ✗ Error scraping {date_str}: {e}")

    logger.info("")
    logger.info(f"Total games scraped: {total_games}")
    logger.info("")

    # Update records
    if total_games > 0:
        logger.info("Updating rankings with new game records...")
        update_rankings_with_records()
        logger.info("✓ Rankings updated!")
    else:
        logger.info("No new games found to update")

    logger.info("="*70)
    logger.info("SCRAPING COMPLETE")
    logger.info("="*70)

if __name__ == '__main__':
    scrape_missing_dates()
