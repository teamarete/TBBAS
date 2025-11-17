"""
One-time script to ensure rankings have game statistics
This runs once when the app starts to merge game records into rankings
"""

import json
from pathlib import Path

def ensure_rankings_have_stats():
    """Check if rankings need game stats and update them"""
    data_dir = Path(__file__).parent / 'data'
    rankings_file = data_dir / 'rankings.json'

    if not rankings_file.exists():
        print("Rankings file doesn't exist yet - will be created by scheduler")
        return

    # Check if rankings already have game stats
    with open(rankings_file, 'r') as f:
        data = json.load(f)

    # Check a sample team to see if it has ppg data
    sample_has_stats = False
    if data.get('uil', {}).get('AAAAAA'):
        for team in data['uil']['AAAAAA']:
            if team.get('ppg') is not None:
                sample_has_stats = True
                break

    if sample_has_stats:
        print("Rankings already have game statistics")
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
