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
from email_notifier import EmailNotifier
from gaso_scraper import GASOScraper
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize email notifier
email_notifier = EmailNotifier()

# Schedule configuration
START_DATE = datetime(2025, 11, 11)  # November 11, 2025
END_DATE = datetime(2026, 3, 9)      # March 9, 2026
UPDATE_TIME = "06:00"                # 6:00 AM
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

    errors = []
    games_collected = 0
    sources_summary = {}

    try:
        collector = BoxScoreCollector(app=_app)

        # Use configured dates if specified, otherwise collect yesterday's games
        target_dates = SCRAPE_DATES if SCRAPE_DATES else None
        if target_dates:
            logger.info(f"Using configured dates: {', '.join(target_dates)}")

        games = collector.collect_daily_box_scores(target_dates=target_dates)
        games_collected = len(games)

        # Build sources summary
        for game in games:
            source = game.get('source', 'Unknown')
            sources_summary[source] = sources_summary.get(source, 0) + 1

        logger.info(f"Box score collection complete: {games_collected} games processed")

        # Check rankings from all sources daily
        logger.info("Checking rankings from all sources...")
        try:
            from scraper import TABCScraper
            scraper = TABCScraper()

            # Scrape TABC rankings (UIL and Private)
            logger.info("  - Checking TABC UIL rankings...")
            tabc_uil = scraper.scrape_uil_rankings()

            logger.info("  - Checking TABC Private rankings...")
            tabc_private = scraper.scrape_private_rankings()

            logger.info("  - Checking GASO rankings...")
            # GASO is already checked in box_score_scraper as part of collector

            logger.info("  - Checking HoopInsider rankings...")
            # HoopInsider check can be added if needed

            logger.info("Rankings check complete")
        except Exception as e:
            logger.error(f"Error checking rankings: {e}")

        # Update rankings with records from collected games (including coach submissions)
        logger.info("Updating rankings with game records (including coach submissions)...")
        try:
            from update_rankings_with_records import update_rankings_with_records
            update_rankings_with_records()
            logger.info("Rankings updated with all game records")
        except Exception as e:
            logger.error(f"Error updating rankings with records: {e}")

        # Send success notification
        email_notifier.notify_daily_collection(
            games_collected=games_collected,
            sources_summary=sources_summary,
            errors=None
        )

    except Exception as e:
        error_msg = f"Error collecting box scores: {e}"
        logger.error(error_msg)
        tb = traceback.format_exc()
        logger.error(tb)

        # Send error notification
        email_notifier.notify_error(
            error_type="Daily Box Score Collection",
            error_message=str(e),
            traceback_info=tb
        )


def update_rankings():
    """
    Update rankings on Mondays:
    1. Scrape TABC rankings
    2. Scrape MaxPreps rankings
    3. Scrape GASO rankings
    4. Calculate rankings from box score data
    5. Merge all sources (priority: calculated > TABC > MaxPreps > GASO)
    """
    now = datetime.now()

    # Check if we're within the update period
    if now < START_DATE:
        logger.info(f"Too early - updates start on {START_DATE.strftime('%B %d, %Y')}")
        return

    if now > END_DATE:
        logger.info(f"Season ended - no more updates after {END_DATE.strftime('%B %d, %Y')}")
        return

    logger.info("="*50)
    logger.info(f"Starting weekly rankings update at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*50)

    errors = []
    rankings_summary = {'uil': {}, 'private': {}}

    try:
        # 1. Scrape TABC rankings (FALLBACK 1)
        logger.info("1. Scraping TABC rankings (FALLBACK 1)...")
        tabc_scraper = TABCScraper()
        tabc_data = tabc_scraper.scrape_all()

        # 2. Scrape MaxPreps rankings (FALLBACK 2)
        logger.info("2. Scraping MaxPreps rankings (FALLBACK 2)...")
        from box_score_scraper import MaxPrepsBoxScoreScraper
        maxpreps_scraper = MaxPrepsBoxScoreScraper()

        maxpreps_data = {
            'last_updated': datetime.now().isoformat(),
            'uil': {},
            'private': {}
        }

        # Scrape UIL from MaxPreps
        try:
            uil_rankings = maxpreps_scraper.scrape_maxpreps_rankings('UIL')
            if uil_rankings:
                maxpreps_data['uil'] = uil_rankings
                logger.info(f"   MaxPreps UIL: Retrieved rankings")
        except Exception as e:
            error_msg = f"MaxPreps UIL scraping failed: {e}"
            logger.error(f"   {error_msg}")
            errors.append(error_msg)

        # Scrape TAPPS from MaxPreps
        try:
            tapps_rankings = maxpreps_scraper.scrape_maxpreps_rankings('TAPPS')
            if tapps_rankings:
                maxpreps_data['private'] = tapps_rankings
                logger.info(f"   MaxPreps TAPPS: Retrieved rankings")
        except Exception as e:
            error_msg = f"MaxPreps TAPPS scraping failed: {e}"
            logger.error(f"   {error_msg}")
            errors.append(error_msg)

        # 3. Scrape GASO rankings (FALLBACK 3)
        logger.info("3. Scraping GASO rankings (FALLBACK 3)...")
        gaso_scraper = GASOScraper()
        gaso_data = gaso_scraper.scrape_all()

        # 4. Calculate rankings from box score data (PRIMARY)
        logger.info("4. Calculating rankings from box score data (PRIMARY)...")
        calculator = RankingCalculator(app=_app)
        calculated_rankings = calculator.calculate_all_rankings()

        # 5. Merge all sources (priority: calculated > TABC > MaxPreps > GASO)
        logger.info("5. Merging rankings from all sources...")
        merged_data = merge_rankings(calculated_rankings, tabc_data, maxpreps_data, gaso_data)

        # Build rankings summary for email
        for classification, teams in merged_data.get('uil', {}).items():
            rankings_summary['uil'][classification] = len(teams)
        for classification, teams in merged_data.get('private', {}).items():
            rankings_summary['private'][classification] = len(teams)

        # 5. Save merged rankings
        if merged_data:
            tabc_scraper.save_to_file(merged_data)
            logger.info("="*50)
            logger.info(f"✓ Rankings updated successfully at {now.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*50)

            # 6. Update rankings with game records
            logger.info("Updating rankings with game records...")
            try:
                from update_rankings_with_records import update_rankings_with_records
                update_rankings_with_records()
                logger.info("Rankings updated with game records")
            except Exception as e:
                logger.error(f"Error updating rankings with records: {e}")

            # Send success notification
            email_notifier.notify_weekly_rankings_update(
                rankings_summary=rankings_summary,
                errors=errors if errors else None
            )
        else:
            error_msg = "Failed to generate rankings"
            logger.error(error_msg)
            errors.append(error_msg)

            # Send error notification
            email_notifier.notify_error(
                error_type="Weekly Rankings Update",
                error_message="Failed to generate merged rankings",
                traceback_info=None
            )

    except Exception as e:
        error_msg = f"Error updating rankings: {e}"
        logger.error(error_msg)
        tb = traceback.format_exc()
        logger.error(tb)

        # Send error notification
        email_notifier.notify_error(
            error_type="Weekly Rankings Update",
            error_message=str(e),
            traceback_info=tb
        )


def merge_rankings(calculated_data, tabc_data, maxpreps_data, gaso_data):
    """
    Merge rankings from all sources with priority:
    1. Calculated from box scores (PRIMARY)
    2. TABC rankings (FALLBACK 1)
    3. MaxPreps rankings (FALLBACK 2)
    4. GASO rankings (FALLBACK 3)

    IMPORTANT: Preserves ALL schools and game statistics from previous updates
    """
    import json
    from pathlib import Path

    # Load existing rankings to preserve game stats
    existing_stats = {}
    rankings_file = Path('data/rankings.json')
    if rankings_file.exists():
        try:
            with open(rankings_file, 'r') as f:
                existing_data = json.load(f)

            # Build a lookup of existing stats by team name and classification
            for category in ['uil', 'private']:
                if category in existing_data:
                    for classification, teams in existing_data[category].items():
                        for team in teams:
                            key = (category, classification, team.get('team_name'))
                            existing_stats[key] = {
                                'wins': team.get('wins'),
                                'losses': team.get('losses'),
                                'games': team.get('games'),
                                'ppg': team.get('ppg'),
                                'opp_ppg': team.get('opp_ppg'),
                                'district': team.get('district'),
                                'uil_verified': team.get('uil_verified'),
                                'uil_official_name': team.get('uil_official_name')
                            }
            logger.info(f"Loaded {len(existing_stats)} existing team stats to preserve")
        except Exception as e:
            logger.warning(f"Could not load existing stats: {e}")

    merged = {
        'last_updated': datetime.now().isoformat(),
        'uil': {},
        'private': {}
    }

    def preserve_stats(teams, category, classification):
        """Add existing game stats to teams"""
        for team in teams:
            key = (category, classification, team.get('team_name'))
            if key in existing_stats:
                stats = existing_stats[key]
                # Only preserve if not None (don't overwrite with None)
                for field in ['wins', 'losses', 'games', 'ppg', 'opp_ppg', 'district', 'uil_verified', 'uil_official_name']:
                    if stats.get(field) is not None:
                        team[field] = stats[field]
        return teams

    # Merge UIL
    for classification in ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']:
        # Get ALL existing teams (ranked + unranked)
        existing_teams = existing_data.get('uil', {}).get(classification, [])
        existing_by_name = {team['team_name']: team for team in existing_teams}

        # Get new ranking sources
        calculated_teams = calculated_data.get('uil', {}).get(classification, [])
        tabc_teams = tabc_data.get('uil', {}).get(classification, [])
        maxpreps_teams = maxpreps_data.get('uil', {}).get(classification, [])
        gaso_teams = gaso_data.get('uil', {}).get(classification, [])

        # ENSURE WE ALWAYS HAVE TOP 25 RANKINGS
        # First, update existing teams with ranks
        for team in existing_teams:
            team_name = team['team_name']

            # Try to find rank from calculated (highest priority)
            calc_team = next((t for t in calculated_teams if t.get('team_name') == team_name), None)
            if calc_team:
                team['rank'] = calc_team.get('rank')
                continue

            # Try TABC (fallback 1)
            tabc_team = next((t for t in tabc_teams if t.get('team_name') == team_name), None)
            if tabc_team:
                team['rank'] = tabc_team.get('rank')
                continue

            # Try MaxPreps (fallback 2)
            maxprep_team = next((t for t in maxpreps_teams if t.get('team_name') == team_name), None)
            if maxprep_team:
                team['rank'] = maxprep_team.get('rank')
                continue

            # Try GASO (fallback 3)
            gaso_team = next((t for t in gaso_teams if t.get('team_name') == team_name), None)
            if gaso_team:
                team['rank'] = gaso_team.get('rank')
                continue

            # Not ranked in any source - keep as unranked (rank = None)

        # GUARANTEE TOP 25: Add any TABC top 25 teams that aren't in existing_teams
        for tabc_team in tabc_teams[:25]:  # Ensure we get top 25 from TABC
            team_name = tabc_team.get('team_name')
            if team_name and team_name not in existing_by_name:
                # This team is in TABC top 25 but not in our existing data - add it
                existing_teams.append({
                    'team_name': team_name,
                    'rank': tabc_team.get('rank'),
                    'district': tabc_team.get('district'),
                    'wins': None,
                    'losses': None,
                    'games': None,
                    'ppg': None,
                    'opp_ppg': None
                })
                existing_by_name[team_name] = existing_teams[-1]

        # Preserve stats for all teams
        merged['uil'][classification] = preserve_stats(existing_teams, 'uil', classification)

        ranked_count = sum(1 for t in existing_teams if t.get('rank') is not None and t.get('rank') <= 25)
        logger.info(f"{classification}: {ranked_count} ranked (top 25) / {len(existing_teams)} total teams")

    # Merge Private/TAPPS
    for classification in ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']:
        # Get ALL existing teams (ranked + unranked)
        existing_teams = existing_data.get('private', {}).get(classification, [])
        existing_by_name = {team['team_name']: team for team in existing_teams}

        # Get new ranking sources
        calculated_teams = calculated_data.get('private', {}).get(classification, [])
        tabc_teams = tabc_data.get('private', {}).get(classification, [])
        maxpreps_teams = maxpreps_data.get('private', {}).get(classification, [])
        gaso_teams = gaso_data.get('private', {}).get(classification, [])

        # ENSURE WE ALWAYS HAVE TOP 10 RANKINGS
        # First, update existing teams with ranks
        for team in existing_teams:
            team_name = team['team_name']

            # Try to find rank from calculated (highest priority)
            calc_team = next((t for t in calculated_teams if t.get('team_name') == team_name), None)
            if calc_team:
                team['rank'] = calc_team.get('rank')
                continue

            # Try TABC (fallback 1)
            tabc_team = next((t for t in tabc_teams if t.get('team_name') == team_name), None)
            if tabc_team:
                team['rank'] = tabc_team.get('rank')
                continue

            # Try MaxPreps (fallback 2)
            maxprep_team = next((t for t in maxpreps_teams if t.get('team_name') == team_name), None)
            if maxprep_team:
                team['rank'] = maxprep_team.get('rank')
                continue

            # Try GASO (fallback 3)
            gaso_team = next((t for t in gaso_teams if t.get('team_name') == team_name), None)
            if gaso_team:
                team['rank'] = gaso_team.get('rank')
                continue

            # Not ranked in any source - keep as unranked (rank = None)

        # GUARANTEE TOP 10: Add any TABC top 10 teams that aren't in existing_teams
        for tabc_team in tabc_teams[:10]:  # Ensure we get top 10 from TABC
            team_name = tabc_team.get('team_name')
            if team_name and team_name not in existing_by_name:
                # This team is in TABC top 10 but not in our existing data - add it
                existing_teams.append({
                    'team_name': team_name,
                    'rank': tabc_team.get('rank'),
                    'district': tabc_team.get('district'),
                    'wins': None,
                    'losses': None,
                    'games': None,
                    'ppg': None,
                    'opp_ppg': None
                })
                existing_by_name[team_name] = existing_teams[-1]

        # Preserve stats for all teams
        merged['private'][classification] = preserve_stats(existing_teams, 'private', classification)

        ranked_count = sum(1 for t in existing_teams if t.get('rank') is not None and t.get('rank') <= 10)
        logger.info(f"{classification}: {ranked_count} ranked (top 10) / {len(existing_teams)} total teams")

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
    logger.info(f"  - Every Monday at {UPDATE_TIME}")
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
    print(f"Frequency: Every Monday (weekly)")
    print("\nScheduled Update Dates:")
    print("-" * 50)

    update_dates = calculate_update_dates()
    for i, date in enumerate(update_dates, 1):
        print(f"{i}. {date.strftime('%A, %B %d, %Y at {UPDATE_TIME}')}")

    print(f"\nTotal updates: {len(update_dates)}")
