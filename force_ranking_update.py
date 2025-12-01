"""
Force a ranking update manually
This can be run to immediately update rankings with latest data
"""

from app import app
from scheduler import update_rankings

print("=" * 80)
print("FORCING IMMEDIATE RANKING UPDATE")
print("=" * 80)
print()

with app.app_context():
    print("Triggering ranking update with all sources...")
    update_rankings()
    print()
    print("=" * 80)
    print("✓ RANKING UPDATE COMPLETE")
    print("=" * 80)
    print()
    print("Rankings have been updated with:")
    print("  - Latest game data from database")
    print("  - Calculated efficiency ratings")
    print("  - TABC rankings")
    print("  - MaxPreps rankings")
    print("  - GASO rankings")
    print()
    print("Check data/rankings.json for updated rankings")
