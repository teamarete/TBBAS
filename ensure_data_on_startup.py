"""
Ensure rankings data exists on Railway startup
If rankings.json is missing or empty, trigger immediate update
"""

import os
from pathlib import Path
import json
from datetime import datetime

def check_and_update_rankings():
    """Check if rankings exist, if not trigger immediate update"""
    data_file = Path(__file__).parent / 'data' / 'rankings.json'

    # Check if file exists and has data
    needs_update = False

    if not data_file.exists():
        print("⚠️  Rankings file does not exist - triggering immediate update")
        needs_update = True
    else:
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)

            # Check if data is empty
            if not data.get('uil') and not data.get('private'):
                print("⚠️  Rankings file is empty - copying from git")
                needs_update = True
            else:
                # Verify data integrity - check if UIL 6A has 25 ranked teams
                uil_6a_teams = data.get('uil', {}).get('AAAAAA', [])
                ranked_6a = sum(1 for t in uil_6a_teams if t.get('rank') is not None and 1 <= t.get('rank') <= 25)

                if ranked_6a < 25:
                    print(f"⚠️  Rankings incomplete: UIL 6A has only {ranked_6a}/25 ranked teams")
                    print("   Deleting corrupted file to force git version reload...")
                    data_file.unlink()
                    print("   ✓ File deleted - will use git version on next check")
                    return False  # Don't update, just let it reload from git

                if 'last_updated' in data:
                    last_update = datetime.fromisoformat(data['last_updated'])
                    hours_old = (datetime.now() - last_update).total_seconds() / 3600
                    print(f"✓ Rankings file exists with {ranked_6a}/25 UIL 6A teams (last updated {hours_old:.1f} hours ago)")
                else:
                    print(f"✓ Rankings file exists with {ranked_6a}/25 UIL 6A teams")

        except Exception as e:
            print(f"⚠️  Error reading rankings file: {e}")
            needs_update = True

    if needs_update:
        print("\n🔄 Triggering immediate ranking update...")
        try:
            from scheduler import update_rankings
            update_rankings()
            print("✓ Rankings updated successfully!")
        except Exception as e:
            print(f"❌ Failed to update rankings: {e}")
            import traceback
            traceback.print_exc()

    return not needs_update

if __name__ == "__main__":
    check_and_update_rankings()
