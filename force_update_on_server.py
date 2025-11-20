#!/usr/bin/env python3
"""
Force update rankings on the Railway server
This script can be run via Railway's CLI or as a one-time task
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from update_rankings_with_records import update_rankings_with_records
from models import BoxScore

print("=" * 80)
print("FORCE UPDATE RANKINGS ON SERVER")
print("=" * 80)

with app.app_context():
    # Check database
    game_count = BoxScore.query.count()
    print(f"\n📊 Database Status:")
    print(f"   Games in database: {game_count}")

    if game_count == 0:
        print("\n⚠️  WARNING: No games in database!")
        print("   The database file may not have been deployed to Railway.")
        print("   You'll need to re-import games on the server.")
    else:
        print(f"\n✅ Database has {game_count} games")

        # Run update
        print("\n🔄 Running rankings update...")
        result = update_rankings_with_records()

        print("\n✅ UPDATE COMPLETE")
        print(f"   Teams with records: {result.get('games_analyzed', 0)}")
        print(f"   Last updated: {result.get('last_updated', 'unknown')}")

print("\n" + "=" * 80)
