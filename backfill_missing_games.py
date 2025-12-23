"""
Backfill Missing Games
Scrapes MaxPreps box scores for dates that were missed by the daily scheduler
"""
from datetime import datetime, timedelta
from scrape_maxpreps_daily import scrape_date_range

def backfill_missing_games():
    """
    Backfill games from December 2, 2025 to today
    The last scrape was December 1, 2025
    """
    print("=" * 80)
    print("BACKFILLING MISSING GAMES")
    print("=" * 80)

    # Last successful scrape was December 1, 2025
    # Start from December 2
    start_date = datetime(2025, 12, 2)

    # End with yesterday (don't scrape today's games yet - they may not be complete)
    end_date = datetime.now() - timedelta(days=1)

    # Calculate days to backfill
    days_to_backfill = (end_date - start_date).days + 1

    print(f"Start date: {start_date.strftime('%B %d, %Y')}")
    print(f"End date: {end_date.strftime('%B %d, %Y')}")
    print(f"Days to backfill: {days_to_backfill}")
    print()
    print("This will scrape MaxPreps for each missing date...")
    print("Note: This may take a while (Selenium scraping is slow)")
    print("=" * 80)
    print()

    # Run the backfill
    total_imported = scrape_date_range(start_date, end_date)

    print()
    print("=" * 80)
    print("BACKFILL COMPLETE")
    print("=" * 80)
    print(f"Total new games imported: {total_imported}")
    print()
    print("Next steps:")
    print("1. Run update_weekly_rankings.py to recalculate rankings with new data")
    print("2. Verify that teams now have more games in the database")
    print("=" * 80)

if __name__ == '__main__':
    backfill_missing_games()
