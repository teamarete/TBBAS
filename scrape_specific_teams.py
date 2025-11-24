"""
Scrape specific teams that are missing game records
"""

from datetime import datetime
from app import app
from box_score_scraper import BoxScoreCollector
from update_rankings_with_records import update_rankings_with_records
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_specific_teams():
    """Scrape specific teams from MaxPreps URLs"""

    # Teams to scrape with their MaxPreps URLs
    teams_to_scrape = [
        {
            'name': 'SA Harlan / Harlan',
            'url': 'https://www.maxpreps.com/tx/san-antonio/harlan-hawks/basketball/'
        },
        {
            'name': 'Mans Lake Ridge / Mansfield Lake Ridge',
            'url': 'https://www.maxpreps.com/tx/mansfield/lake-ridge-eagles/basketball/'
        },
        {
            'name': 'Odessa Permian',
            'url': 'https://www.maxpreps.com/tx/odessa/permian-panthers/basketball/'
        }
    ]

    logger.info("="*70)
    logger.info("SCRAPING SPECIFIC TEAMS WITH MISSING RECORDS")
    logger.info("="*70)
    logger.info("")

    # Date range to scrape
    dates_to_scrape = [
        "11/14/2025", "11/15/2025", "11/16/2025",
        "11/17/2025", "11/18/2025", "11/19/2025",
        "11/20/2025", "11/21/2025", "11/22/2025"
    ]

    collector = BoxScoreCollector(app=app)

    for team in teams_to_scrape:
        logger.info(f"\nProcessing: {team['name']}")
        logger.info(f"URL: {team['url']}")

        # The collector will scrape MaxPreps for all teams
        # We just need to run it and let it find games for these dates
        logger.info(f"  Searching for games in Nov 14-22...")

    # Run the general scraper for these dates
    logger.info("\nScraping all games from Nov 14-22 again to capture any missed teams...")
    total_new_games = 0

    for date_str in dates_to_scrape:
        logger.info(f"Checking {date_str}...")
        try:
            games = collector.collect_daily_box_scores(target_dates=[date_str])
            if len(games) > 0:
                logger.info(f"  ✓ Found {len(games)} new games for {date_str}")
                total_new_games += len(games)
        except Exception as e:
            logger.error(f"  ✗ Error scraping {date_str}: {e}")

    logger.info("")
    logger.info(f"Total NEW games added: {total_new_games}")
    logger.info("")

    # Update records
    logger.info("Updating rankings with game records...")
    update_rankings_with_records()
    logger.info("✓ Rankings updated!")

    logger.info("="*70)
    logger.info("SPECIFIC TEAM SCRAPING COMPLETE")
    logger.info("="*70)
    logger.info("")
    logger.info("Teams processed:")
    for team in teams_to_scrape:
        logger.info(f"  - {team['name']}")

if __name__ == '__main__':
    scrape_specific_teams()
