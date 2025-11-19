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
    time.sleep(5)  # Wait 5 seconds for scheduler to initialize (increased from 2 for reliability)

    data_dir = Path(__file__).parent / 'data'
    rankings_file = data_dir / 'rankings.json'

    if not rankings_file.exists():
        print("Rankings file doesn't exist yet - will be created by scheduler")
        return

    # Check if rankings already have game stats
    with open(rankings_file, 'r') as f:
        data = json.load(f)

    # Check multiple teams to ensure stats AND districts are present
    teams_with_stats = 0
    teams_with_districts = 0
    total_teams_checked = 0

    if data.get('uil', {}).get('AAAAAA'):
        for team in data['uil']['AAAAAA'][:10]:  # Check first 10 teams
            total_teams_checked += 1
            if team.get('ppg') is not None:
                teams_with_stats += 1
            if team.get('district') is not None:
                teams_with_districts += 1

    print(f"Stats check: {teams_with_stats}/{total_teams_checked} teams have PPG")
    print(f"District check: {teams_with_districts}/{total_teams_checked} teams have districts")

    # Check if we have MOST districts (80% threshold)
    # More lenient than before to prevent unnecessary updates
    districts_threshold = total_teams_checked * 0.8

    if total_teams_checked > 0 and teams_with_districts >= districts_threshold:
        print(f"Rankings have sufficient districts ({teams_with_districts}/{total_teams_checked} >= {districts_threshold:.0f}) - skipping update")
        return

    # Rankings need stats/districts - run the update
    print("Rankings missing game statistics or districts - updating now...")
    try:
        from app import app
        from update_rankings_with_records import update_rankings_with_records

        with app.app_context():
            update_rankings_with_records()
            print("✓ Rankings updated with game statistics and districts")
    except Exception as e:
        print(f"Error updating rankings with stats: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ensure_rankings_have_stats()
