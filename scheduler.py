"""
TBBAS Automatic Rankings Updater
- Daily: Scrape box scores from MaxPreps, newspapers, etc.
- Weekly: Calculate rankings from box score data and update TABC rankings
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from scraper import TABCScraper
from box_score_scraper import BoxScoreCollector
from ranking_calculator import RankingCalculator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Schedule configuration
START_DATE = datetime(2025, 11, 11)  # November 11, 2025
END_DATE = datetime(2026, 3, 9)      # March 9, 2026
UPDATE_TIME = "06:00"                # 6:00 AM
INTERVAL_WEEKS = 2                   # Every 2 weeks


_app = None  # Flask app instance for database access


def set_app(app):
    """Set Flask app for scheduler"""
    global _app
    _app = app


def collect_box_scores():
    """Collect box scores from various sources daily"""
    now = datetime.now()

    # Check if we're within the season
    if now < START_DATE:
        logger.info(f"Too early - season starts on {START_DATE.strftime('%B %d, %Y')}")
        return

    if now > END_DATE:
        logger.info(f"Season ended - no more collection after {END_DATE.strftime('%B %d, %Y')}")
        return

    logger.info(f"Starting daily box score collection at {now.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        collector = BoxScoreCollector(app=_app)
        games = collector.collect_daily_box_scores()
        logger.info(f"Box score collection complete: {len(games)} games processed")
    except Exception as e:
        logger.error(f"Error collecting box scores: {e}")
        import traceback
        traceback.print_exc()


def update_rankings():
    """
    Update rankings on Mondays:
    1. Scrape TABC rankings
    2. Calculate rankings from box score data
    3. Merge both sources
    """
    now = datetime.now()

    # Check if we're within the update period
    if now < START_DATE:
        logger.info(f"Too early - updates start on {START_DATE.strftime('%B %d, %Y')}")
        return

    if now > END_DATE:
        logger.info(f"Season ended - no more updates after {END_DATE.strftime('%B %d, %Y')}")
        return

    logger.info(f"Starting weekly rankings update at {now.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. Scrape TABC rankings (for teams without enough box score data)
        logger.info("Scraping TABC rankings...")
        tabc_scraper = TABCScraper()
        tabc_data = tabc_scraper.scrape_all()

        # 2. Calculate rankings from box scores
        logger.info("Calculating rankings from box score data...")
        calculator = RankingCalculator(app=_app)
        calculated_rankings = calculator.calculate_all_rankings()

        # 3. Merge the rankings (prioritize calculated data, use TABC as fallback)
        merged_data = merge_rankings(tabc_data, calculated_rankings)

        # 4. Save merged rankings
        if merged_data:
            tabc_scraper.save_to_file(merged_data)
            logger.info(f"Rankings updated successfully at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            logger.error("Failed to generate rankings")

    except Exception as e:
        logger.error(f"Error updating rankings: {e}")
        import traceback
        traceback.print_exc()


def merge_rankings(tabc_data, calculated_data):
    """
    Merge TABC rankings with calculated rankings
    Use calculated data where available, fall back to TABC
    """
    merged = {
        'last_updated': datetime.now().isoformat(),
        'uil': {},
        'private': {}
    }

    # Merge UIL
    for classification in ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']:
        calculated_teams = calculated_data.get('uil', {}).get(classification, [])
        tabc_teams = tabc_data.get('uil', {}).get(classification, [])

        if calculated_teams and len(calculated_teams) >= 10:
            # Use calculated rankings if we have enough data
            merged['uil'][classification] = calculated_teams
            logger.info(f"{classification}: Using calculated rankings ({len(calculated_teams)} teams)")
        else:
            # Fall back to TABC
            merged['uil'][classification] = tabc_teams
            logger.info(f"{classification}: Using TABC rankings ({len(tabc_teams)} teams)")

    # Merge Private/TAPPS
    for classification in ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']:
        calculated_teams = calculated_data.get('private', {}).get(classification, [])
        tabc_teams = tabc_data.get('private', {}).get(classification, [])

        if calculated_teams and len(calculated_teams) >= 5:
            merged['private'][classification] = calculated_teams
            logger.info(f"{classification}: Using calculated rankings ({len(calculated_teams)} teams)")
        else:
            merged['private'][classification] = tabc_teams
            logger.info(f"{classification}: Using TABC rankings ({len(tabc_teams)} teams)")

    return merged


def calculate_update_dates():
    """Calculate all update dates from start to end"""
    update_dates = []
    current_date = START_DATE

    # Find the first Monday on or after START_DATE
    days_until_monday = (7 - current_date.weekday()) % 7
    if days_until_monday == 0 and current_date.weekday() != 0:
        days_until_monday = 7
    current_date = current_date + timedelta(days=days_until_monday)

    while current_date <= END_DATE:
        update_dates.append(current_date)
        current_date += timedelta(weeks=INTERVAL_WEEKS)

    return update_dates


def is_update_day():
    """Check if today is a scheduled update day"""
    today = datetime.now().date()
    update_dates = calculate_update_dates()

    for update_date in update_dates:
        if update_date.date() == today:
            return True
    return False


def run_scheduler():
    """Run the scheduler in a background thread"""
    logger.info("="*50)
    logger.info("TBBAS Scheduler started")
    logger.info("="*50)
    logger.info(f"Period: {START_DATE.strftime('%B %d, %Y')} to {END_DATE.strftime('%B %d, %Y')}")
    logger.info("")

    # Daily box score collection
    logger.info("Daily Box Score Collection:")
    logger.info(f"  - Every day at {UPDATE_TIME}")
    logger.info(f"  - Sources: MaxPreps, Texas newspapers, coach submissions")
    schedule.every().day.at(UPDATE_TIME).do(collect_box_scores)
    logger.info("")

    # Weekly ranking updates
    update_dates = calculate_update_dates()
    logger.info(f"Weekly Ranking Updates ({len(update_dates)} total):")
    logger.info(f"  - Every 2 weeks on Mondays at {UPDATE_TIME}")
    for date in update_dates:
        logger.info(f"    • {date.strftime('%A, %B %d, %Y')}")

    # Schedule the job for every Monday at 6:00 AM
    schedule.every().monday.at(UPDATE_TIME).do(lambda: update_rankings() if is_update_day() else None)

    logger.info("")
    logger.info("Scheduler is now running...")
    logger.info("="*50)

    # Also check at startup if we need to update
    if is_update_day():
        current_time = datetime.now().strftime("%H:%M")
        if current_time >= UPDATE_TIME:
            logger.info("Update scheduled for today and time has passed - running now")
            update_rankings()

    # Run the schedule loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def start_scheduler(app=None):
    """Start the scheduler in a background thread"""
    if app:
        set_app(app)
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Scheduler thread started in background")


if __name__ == '__main__':
    # Test: show all scheduled dates
    print("TBBAS Rankings Update Schedule")
    print("=" * 50)
    print(f"Start Date: {START_DATE.strftime('%B %d, %Y')}")
    print(f"End Date: {END_DATE.strftime('%B %d, %Y')}")
    print(f"Update Time: {UPDATE_TIME}")
    print(f"Frequency: Every {INTERVAL_WEEKS} weeks on Mondays")
    print("\nScheduled Update Dates:")
    print("-" * 50)

    update_dates = calculate_update_dates()
    for i, date in enumerate(update_dates, 1):
        print(f"{i}. {date.strftime('%A, %B %d, %Y at {UPDATE_TIME}')}")

    print(f"\nTotal updates: {len(update_dates)}")
