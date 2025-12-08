"""
Scrape November 25-29, 2025 for all UIL classifications (A-AAAAAA)
"""

from datetime import datetime
from app import app
from box_score_scraper import BoxScoreCollector
from update_rankings_with_records import update_rankings_with_records
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_complete_range():
    """Scrape Nov 25-29, 2025 for complete game coverage"""

    # All dates from Nov 25-29
    dates_to_scrape = [
        "11/25/2025",
        "11/26/2025",
        "11/27/2025",
        "11/28/2025",
        "11/29/2025"
    ]

    logger.info("="*70)
    logger.info("SCRAPING COMPLETE DATE RANGE: Nov 25-29, 2025")
    logger.info("="*70)
    logger.info("")
    logger.info("Scraping all UIL classifications (A through AAAAAA)")
    logger.info("This will find any games from Thanksgiving week")
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

    # Update records in rankings.json
    logger.info("Updating rankings with complete game records...")
    update_rankings_with_records()
    logger.info("✓ Rankings updated with all available games!")

    logger.info("="*70)
    logger.info("COMPLETE SCRAPE FINISHED")
    logger.info("="*70)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Check rankings.json to verify records are updated")
    logger.info("2. Commit and push rankings.json to update website")
    logger.info("3. Rankings will be recalculated on Monday at 1 PM CST")

if __name__ == '__main__':
    scrape_complete_range()
