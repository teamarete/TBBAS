"""
TBBAS Automatic Rankings Updater
Runs scraper on a schedule to keep rankings fresh
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from scraper import TABCScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Schedule configuration
START_DATE = datetime(2025, 11, 11)  # November 11, 2025
END_DATE = datetime(2026, 3, 9)      # March 9, 2026
UPDATE_TIME = "06:00"                # 6:00 AM
INTERVAL_WEEKS = 2                   # Every 2 weeks


def update_rankings():
    """Run the scraper to update rankings"""
    now = datetime.now()

    # Check if we're within the update period
    if now < START_DATE:
        logger.info(f"Too early - updates start on {START_DATE.strftime('%B %d, %Y')}")
        return

    if now > END_DATE:
        logger.info(f"Season ended - no more updates after {END_DATE.strftime('%B %d, %Y')}")
        return

    logger.info(f"Starting scheduled rankings update at {now.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        scraper = TABCScraper()
        data = scraper.scrape_all()

        if data:
            scraper.save_to_file(data)
            logger.info(f"Rankings updated successfully at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            logger.error("Failed to fetch rankings")
    except Exception as e:
        logger.error(f"Error updating rankings: {e}")


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
    logger.info("TBBAS Scheduler started")
    logger.info(f"Schedule: Every 2 weeks on Mondays at {UPDATE_TIME}")
    logger.info(f"Period: {START_DATE.strftime('%B %d, %Y')} to {END_DATE.strftime('%B %d, %Y')}")

    # Log all scheduled update dates
    update_dates = calculate_update_dates()
    logger.info(f"Scheduled update dates ({len(update_dates)} total):")
    for date in update_dates:
        logger.info(f"  - {date.strftime('%A, %B %d, %Y at {UPDATE_TIME}')}")

    # Schedule the job for every Monday at 6:00 AM
    schedule.every().monday.at(UPDATE_TIME).do(lambda: update_rankings() if is_update_day() else None)

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


def start_scheduler():
    """Start the scheduler in a background thread"""
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
