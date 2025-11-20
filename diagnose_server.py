#!/usr/bin/env python3
"""
Diagnostic script to check server status
Run this on Railway to see what's deployed
"""

import json
import os
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("TBBAS SERVER DIAGNOSTIC")
print("=" * 80)
print(f"Run time: {datetime.now()}")
print(f"Working directory: {os.getcwd()}")

# Check rankings file
rankings_file = Path(__file__).parent / 'data' / 'rankings.json'
print(f"\n📁 Rankings File:")
print(f"   Path: {rankings_file}")
print(f"   Exists: {rankings_file.exists()}")

if rankings_file.exists():
    size = rankings_file.stat().st_size
    print(f"   Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
    print(f"   Modified: {datetime.fromtimestamp(rankings_file.stat().st_mtime)}")

    with open(rankings_file) as f:
        data = json.load(f)

    print(f"\n📊 Rankings Data:")
    print(f"   Last updated: {data.get('last_updated', 'unknown')}")

    total_teams = sum(len(teams) for teams in data['uil'].values()) + sum(len(teams) for teams in data['private'].values())
    print(f"   Total teams: {total_teams}")

    # Check sample team with records
    teams_with_records = 0
    sample_teams = []
    for classification in data['uil'].values():
        for team in classification:
            if team.get('wins') is not None:
                teams_with_records += 1
                if len(sample_teams) < 3:
                    sample_teams.append(f"{team['team_name']} ({team.get('wins', 0)}-{team.get('losses', 0)})")

    print(f"   Teams with records: {teams_with_records}")
    if sample_teams:
        print(f"   Sample teams: {', '.join(sample_teams)}")

# Check database
db_file = Path(__file__).parent / 'instance' / 'tbbas.db'
print(f"\n💾 Database File:")
print(f"   Path: {db_file}")
print(f"   Exists: {db_file.exists()}")

if db_file.exists():
    size = db_file.stat().st_size
    print(f"   Size: {size:,} bytes ({size/1024:.2f} KB)")
    print(f"   Modified: {datetime.fromtimestamp(db_file.stat().st_mtime)}")

    # Try to query database
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from app import app
        from models import BoxScore

        with app.app_context():
            game_count = BoxScore.query.count()
            print(f"   Games in database: {game_count}")

            if game_count > 0:
                latest = BoxScore.query.order_by(BoxScore.game_date.desc()).first()
                print(f"   Latest game: {latest.game_date} - {latest.team1_name} vs {latest.team2_name}")
    except Exception as e:
        print(f"   ⚠️  Error querying database: {e}")

# Check app.py for the fix
app_file = Path(__file__).parent / 'app.py'
print(f"\n🔧 App Configuration:")
print(f"   Path: {app_file}")
print(f"   Exists: {app_file.exists()}")

if app_file.exists():
    with open(app_file) as f:
        content = f.read()

    has_fix = 'update_rankings_with_records()' in content
    print(f"   Has form submission fix: {'✅ YES' if has_fix else '❌ NO'}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
print("\nIf you see this output, the script is running on the server.")
print("Compare the 'Last updated' timestamp to verify you have the latest data.")
print("Expected: 2025-11-20T10:17:39.225557")
