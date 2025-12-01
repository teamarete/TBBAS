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

            # Check if data is empty or very old
            if not data.get('uil') and not data.get('private'):
                print("⚠️  Rankings file is empty - triggering immediate update")
                needs_update = True
            elif 'last_updated' in data:
                last_update = datetime.fromisoformat(data['last_updated'])
                hours_old = (datetime.now() - last_update).total_seconds() / 3600
                print(f"✓ Rankings file exists (last updated {hours_old:.1f} hours ago)")

                # Force update if more than 2 hours old (catches deployment issues)
                if hours_old > 2:
                    print(f"⚠️  Rankings are {hours_old:.1f} hours old - triggering update")
                    needs_update = True
            else:
                print("✓ Rankings file exists")

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
