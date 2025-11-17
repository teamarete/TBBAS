"""
Run the score import immediately
This will scrape and import scores from configured dates
"""

import sys
import os

# Make sure we can import from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app import app
from box_score_scraper import BoxScoreCollector

def main():
    print("="*70)
    print("IMMEDIATE MAXPREPS SCORE IMPORT")
    print("="*70)

    # Import for 11/14/2025 and 11/15/2025
    target_dates = ["11/14/2025", "11/15/2025"]

    print(f"\nTarget dates: {', '.join(target_dates)}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*70)

    try:
        with app.app_context():
            collector = BoxScoreCollector(app=app)

            print("\nStarting collection...")
            games = collector.collect_daily_box_scores(target_dates=target_dates)

            print("\n" + "="*70)
            print("IMPORT COMPLETE!")
            print("="*70)
            print(f"Total games collected: {len(games)}")

            # Show breakdown by source
            sources = {}
            for game in games:
                source = game.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1

            if sources:
                print("\nBreakdown by source:")
                for source, count in sources.items():
                    print(f"  {source}: {count}")

            # Show some sample games
            if games:
                print(f"\nSample games (first 5):")
                for i, game in enumerate(games[:5], 1):
                    print(f"  {i}. {game['team1_name']} {game['team1_score']} vs "
                          f"{game['team2_name']} {game['team2_score']} ({game['date']})")

            print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n✓ SUCCESS - Scores have been imported to the database")

            return 0

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\nImport failed. Please check the error above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
