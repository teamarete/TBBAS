"""
Script to manually import scores from specific dates
Run this to populate the database with MaxPreps scores
"""

import sys
from datetime import datetime
from app import app
from box_score_scraper import BoxScoreCollector

def import_scores_for_dates(dates):
    """Import scores for specific dates"""
    print("="*60)
    print("MaxPreps Score Import")
    print("="*60)

    with app.app_context():
        collector = BoxScoreCollector(app=app)

        print(f"\nImporting scores for dates: {', '.join(dates)}")
        print("-"*60)

        games = collector.collect_daily_box_scores(target_dates=dates)

        print("\n" + "="*60)
        print("IMPORT COMPLETE")
        print("="*60)
        print(f"Total games collected: {len(games)}")

        # Show breakdown by source
        sources = {}
        for game in games:
            source = game.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1

        print("\nGames by source:")
        for source, count in sources.items():
            print(f"  {source}: {count}")

        return len(games)

if __name__ == "__main__":
    # Import for 11/14/2025 and 11/15/2025
    dates = ["11/14/2025", "11/15/2025"]

    try:
        total = import_scores_for_dates(dates)
        print(f"\n✓ Successfully imported {total} games")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
