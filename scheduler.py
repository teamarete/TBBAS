"""
TBBAS Automatic Rankings Updater - New Workflow
- Daily (6 AM CST): Scrape box scores from MaxPreps
- Monday (2 PM CST): Scrape TABC and MaxPreps rankings
- Monday (4 PM CST): Calculate and publish rankings using 33/33/33 weighted average
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from email_notifier import EmailNotifier
import logging
import traceback
import subprocess
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize email notifier
email_notifier = EmailNotifier()

# Schedule configuration
START_DATE = datetime(2025, 11, 11)  # November 11, 2025
END_DATE = datetime(2026, 3, 9)      # March 9, 2026

# New schedule times (UTC)
DAILY_BOX_SCORE_TIME = "12:00"       # 12:00 PM UTC = 6:00 AM CST (daily MaxPreps box scores)
WEEKLY_SCRAPE_TIME = "20:00"         # 20:00 PM UTC = 2:00 PM CST (Monday TABC + MaxPreps rankings scrape)
WEEKLY_UPDATE_TIME = "22:00"         # 22:00 PM UTC = 4:00 PM CST (Monday rankings calculation)
INTERVAL_WEEKS = 1                   # Every week (every Monday)

# MaxPreps scraping configuration
# Scrape scores from yesterday by default, but can specify additional dates
# Format: list of date strings in MM/DD/YYYY format
# Example: ["11/14/2024", "11/15/2024"] to scrape specific dates
# Leave empty [] to scrape yesterday's games automatically
SCRAPE_DATES = []  # Empty = scrape yesterday's games daily


_app = None  # Flask app instance for database access


def set_app(app):
    """Set Flask app for scheduler"""
    global _app
    _app = app


def collect_daily_box_scores():
    """
    Daily task: Scrape box scores from MaxPreps (6 AM CST)
    Runs scrape_maxpreps_daily.py to collect yesterday's games
    """
    now = datetime.now()

    # Check if we're within the season
    if now < START_DATE:
        logger.info(f"Too early - season starts on {START_DATE.strftime('%B %d, %Y')}")
        return

    if now > END_DATE:
        logger.info(f"Season ended - no more collection after {END_DATE.strftime('%B %d, %Y')}")
        return

    logger.info("=" * 80)
    logger.info(f"DAILY BOX SCORE COLLECTION - {now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    try:
        # Run scrape_maxpreps_daily.py
        logger.info("Running MaxPreps daily box score scraper...")
        result = subprocess.run(
            [sys.executable, 'scrape_maxpreps_daily.py'],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        # Log output
        if result.stdout:
            logger.info(result.stdout)

        if result.stderr:
            logger.error(result.stderr)

        if result.returncode == 0:
            logger.info("✓ Daily box score collection completed successfully")

            # Send success notification
            email_notifier.notify_daily_collection(
                games_collected=0,  # Parse from output if needed
                sources_summary={'MaxPreps': 'Auto-scraped'},
                errors=None
            )
        else:
            logger.error(f"Daily scraper failed with return code {result.returncode}")

            # Send error notification
            email_notifier.notify_error(
                error_type="Daily Box Score Collection",
                error_message=f"Scraper returned code {result.returncode}",
                traceback_info=result.stderr
            )

    except subprocess.TimeoutExpired:
        error_msg = "Daily box score scraper timed out after 10 minutes"
        logger.error(error_msg)

        email_notifier.notify_error(
            error_type="Daily Box Score Collection",
            error_message=error_msg,
            traceback_info="Timeout after 600 seconds"
        )

    except Exception as e:
        error_msg = f"Error running daily box score scraper: {e}"
        logger.error(error_msg)
        tb = traceback.format_exc()
        logger.error(tb)

        email_notifier.notify_error(
            error_type="Daily Box Score Collection",
            error_message=str(e),
            traceback_info=tb
        )

    logger.info("=" * 80)


def scrape_weekly_rankings():
    """
    Monday 2 PM CST task: Scrape TABC and MaxPreps rankings
    Runs scrape_weekly_rankings.py to collect all ranking data
    """
    now = datetime.now()

    # Check if we're within the update period
    if now < START_DATE:
        logger.info(f"Too early - updates start on {START_DATE.strftime('%B %d, %Y')}")
        return

    if now > END_DATE:
        logger.info(f"Season ended - no more updates after {END_DATE.strftime('%B %d, %Y')}")
        return

    logger.info("=" * 80)
    logger.info(f"WEEKLY RANKINGS SCRAPE - {now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    try:
        # Run scrape_weekly_rankings.py
        logger.info("Running weekly rankings scraper (TABC + MaxPreps)...")
        result = subprocess.run(
            [sys.executable, 'scrape_weekly_rankings.py'],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout (Selenium takes time)
        )

        # Log output
        if result.stdout:
            logger.info(result.stdout)

        if result.stderr:
            logger.error(result.stderr)

        if result.returncode == 0:
            logger.info("✓ Weekly rankings scrape completed successfully")
        else:
            logger.error(f"Weekly rankings scraper failed with return code {result.returncode}")

            email_notifier.notify_error(
                error_type="Weekly Rankings Scrape",
                error_message=f"Scraper returned code {result.returncode}",
                traceback_info=result.stderr
            )

    except subprocess.TimeoutExpired:
        error_msg = "Weekly rankings scraper timed out after 30 minutes"
        logger.error(error_msg)

        email_notifier.notify_error(
            error_type="Weekly Rankings Scrape",
            error_message=error_msg,
            traceback_info="Timeout after 1800 seconds"
        )

    except Exception as e:
        error_msg = f"Error running weekly rankings scraper: {e}"
        logger.error(error_msg)
        tb = traceback.format_exc()
        logger.error(tb)

        email_notifier.notify_error(
            error_type="Weekly Rankings Scrape",
            error_message=str(e),
            traceback_info=tb
        )

    logger.info("=" * 80)


def update_weekly_rankings():
    """
    Monday 4 PM CST task: Calculate and publish rankings
    Runs update_weekly_rankings.py to compute 33/33/33 weighted average
    """
    now = datetime.now()

    # Check if we're within the update period
    if now < START_DATE:
        logger.info(f"Too early - updates start on {START_DATE.strftime('%B %d, %Y')}")
        return

    if now > END_DATE:
        logger.info(f"Season ended - no more updates after {END_DATE.strftime('%B %d, %Y')}")
        return

    logger.info("=" * 80)
    logger.info(f"WEEKLY RANKINGS UPDATE - {now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    try:
        # Run update_weekly_rankings.py
        logger.info("Running weekly rankings calculator (33/33/33 weighted average)...")
        result = subprocess.run(
            [sys.executable, 'update_weekly_rankings.py'],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        # Log output
        if result.stdout:
            logger.info(result.stdout)

        if result.stderr:
            logger.error(result.stderr)

        if result.returncode == 0:
            logger.info("✓ Weekly rankings update completed successfully")

            # Send success notification
            email_notifier.notify_weekly_rankings_update(
                rankings_summary={'status': 'Updated with 33/33/33 formula'},
                errors=None
            )
        else:
            logger.error(f"Weekly rankings update failed with return code {result.returncode}")

            email_notifier.notify_error(
                error_type="Weekly Rankings Update",
                error_message=f"Update script returned code {result.returncode}",
                traceback_info=result.stderr
            )

    except subprocess.TimeoutExpired:
        error_msg = "Weekly rankings update timed out after 10 minutes"
        logger.error(error_msg)

        email_notifier.notify_error(
            error_type="Weekly Rankings Update",
            error_message=error_msg,
            traceback_info="Timeout after 600 seconds"
        )

    except Exception as e:
        error_msg = f"Error running weekly rankings update: {e}"
        logger.error(error_msg)
        tb = traceback.format_exc()
        logger.error(tb)

        email_notifier.notify_error(
            error_type="Weekly Rankings Update",
            error_message=str(e),
            traceback_info=tb
        )

    logger.info("=" * 80)


# OLD MERGE FUNCTION REMOVED - Now handled by update_weekly_rankings.py
# The new workflow uses 33/33/33 weighted average (Calculated + TABC + MaxPreps)
# GASO has been removed from the ranking sources


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
    logger.info("=" * 80)
    logger.info("TBBAS SCHEDULER - NEW AUTOMATION WORKFLOW")
    logger.info("=" * 80)
    logger.info(f"Season Period: {START_DATE.strftime('%B %d, %Y')} to {END_DATE.strftime('%B %d, %Y')}")
    logger.info("")

    # Daily box score collection (6 AM CST)
    logger.info("Daily Box Score Collection:")
    logger.info(f"  - Every day at {DAILY_BOX_SCORE_TIME} UTC (6:00 AM CST)")
    logger.info(f"  - Script: scrape_maxpreps_daily.py")
    logger.info(f"  - Action: Scrape previous day's games from MaxPreps")
    schedule.every().day.at(DAILY_BOX_SCORE_TIME).do(collect_daily_box_scores)
    logger.info("")

    # Weekly rankings scrape (Monday 2 PM CST) - DISABLED (manual updates only)
    # logger.info("Weekly Rankings Scrape:")
    # logger.info(f"  - Every Monday at {WEEKLY_SCRAPE_TIME} UTC (2:00 PM CST)")
    # logger.info(f"  - Script: scrape_weekly_rankings.py")
    # logger.info(f"  - Action: Scrape TABC + MaxPreps rankings")
    # schedule.every().monday.at(WEEKLY_SCRAPE_TIME).do(lambda: scrape_weekly_rankings() if is_update_day() else None)
    # logger.info("")

    # Weekly rankings update (Monday 4 PM CST) - DISABLED (manual updates only)
    # logger.info("Weekly Rankings Update:")
    # logger.info(f"  - Every Monday at {WEEKLY_UPDATE_TIME} UTC (4:00 PM CST)")
    # logger.info(f"  - Script: update_weekly_rankings.py")
    # logger.info(f"  - Action: Calculate 33/33/33 weighted average and publish")
    # schedule.every().monday.at(WEEKLY_UPDATE_TIME).do(lambda: update_weekly_rankings() if is_update_day() else None)
    # logger.info("")

    logger.info("Automatic Ranking Updates: DISABLED")
    logger.info("  - Rankings will be updated manually only")
    logger.info("  - To re-enable: uncomment scrape_weekly_rankings and update_weekly_rankings jobs")
    logger.info("  - Manual scripts: scrape_weekly_rankings.py, update_weekly_rankings.py")

    logger.info("")
    logger.info("Scheduler is now running...")
    logger.info("=" * 80)

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
    print("TBBAS Schedule - New Automation Workflow")
    print("=" * 50)
    print(f"Season: {START_DATE.strftime('%B %d, %Y')} to {END_DATE.strftime('%B %d, %Y')}")
    print()
    print("Daily Box Score Collection:")
    print(f"  Time: {DAILY_BOX_SCORE_TIME} UTC (6:00 AM CST)")
    print(f"  Frequency: Every day")
    print(f"  Script: scrape_maxpreps_daily.py")
    print()
    print("Weekly Ranking Updates (DISABLED - manual only):")
    print(f"  Scrape Time: {WEEKLY_SCRAPE_TIME} UTC (2:00 PM CST)")
    print(f"  Update Time: {WEEKLY_UPDATE_TIME} UTC (4:00 PM CST)")
    print(f"  Frequency: Every Monday")
    print(f"  Scripts: scrape_weekly_rankings.py, update_weekly_rankings.py")
    print("\nScheduled Monday Update Dates:")
    print("-" * 50)

    update_dates = calculate_update_dates()
    for i, date in enumerate(update_dates, 1):
        print(f"{i}. {date.strftime('%A, %B %d, %Y')}")
        print(f"    2:00 PM CST: Scrape TABC + MaxPreps rankings")
        print(f"    4:00 PM CST: Calculate and publish rankings (33/33/33)")

    print(f"\nTotal Monday updates: {len(update_dates)}")
