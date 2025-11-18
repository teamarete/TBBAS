"""
One-time script to ensure rankings have game statistics
This runs once when the app starts to merge game records into rankings
"""

import json
from pathlib import Path

def ensure_rankings_have_stats():
    """Check if rankings need game stats and update them

    This should be called AFTER scheduler initialization to ensure
    that any scheduler updates have game statistics merged in.
    """
    # Import here to avoid circular dependency
    import time
    time.sleep(2)  # Wait 2 seconds for scheduler to initialize

    data_dir = Path(__file__).parent / 'data'
    rankings_file = data_dir / 'rankings.json'

    if not rankings_file.exists():
        print("Rankings file doesn't exist yet - will be created by scheduler")
        return

    # Check if rankings already have game stats
    with open(rankings_file, 'r') as f:
        data = json.load(f)

    # Check multiple teams to ensure stats are present
    teams_with_stats = 0
    total_teams_checked = 0

    if data.get('uil', {}).get('AAAAAA'):
        for team in data['uil']['AAAAAA'][:10]:  # Check first 10 teams
            total_teams_checked += 1
            if team.get('ppg') is not None:
                teams_with_stats += 1

    # If more than half have stats, consider it already updated
    if total_teams_checked > 0 and teams_with_stats > total_teams_checked / 2:
        print(f"Rankings already have game statistics ({teams_with_stats}/{total_teams_checked} teams)")
        return

    # Rankings need stats - run the update
    print("Rankings missing game statistics - updating now...")
    try:
        from app import app
        from update_rankings_with_records import update_rankings_with_records

        with app.app_context():
            update_rankings_with_records()
            print("✓ Rankings updated with game statistics")
    except Exception as e:
        print(f"Error updating rankings with stats: {e}")

if __name__ == "__main__":
    ensure_rankings_have_stats()
