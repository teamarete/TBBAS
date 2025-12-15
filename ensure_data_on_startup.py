"""
Ensure rankings data exists on Railway startup
If rankings.json is missing or empty, trigger immediate update
"""

import os
from pathlib import Path
import json
from datetime import datetime

def check_and_update_rankings():
    """Check if rankings exist, if not restore from gold master or trigger update"""
    data_file = Path(__file__).parent / 'data' / 'rankings.json'
    # Master file is in root directory, not data/ (to avoid Railway volume mount issues)
    master_file = Path(__file__).parent / 'rankings.json.master'

    # ALWAYS restore from git version on startup to prevent stale volume data
    # This ensures Railway deployments always use the latest rankings from git
    print("🔄 Force-restoring rankings from git version of gold master...")

    # Check if file exists and has data
    needs_restore = True  # Always restore from master on startup
    needs_update = False

    # Skip the validation checks - we ALWAYS restore from git master on startup
    # This prevents stale Railway volume data from persisting across deployments

    # Try to restore from master file if needed
    if needs_restore and master_file.exists():
        print(f"\n🔄 Restoring rankings from gold master file...")
        try:
            import shutil
            shutil.copy(master_file, data_file)
            print("✓ Rankings restored successfully from gold master!")

            # Verify the restored data
            with open(data_file, 'r') as f:
                restored_data = json.load(f)
            uil_6a = restored_data.get('uil', {}).get('AAAAAA', [])
            tapps_6a = restored_data.get('private', {}).get('TAPPS_6A', [])
            ranked_uil = sum(1 for t in uil_6a if t.get('rank') and 1 <= t['rank'] <= 25)
            ranked_tapps = sum(1 for t in tapps_6a if t.get('rank') and 1 <= t['rank'] <= 10)
            print(f"   Restored: UIL 6A {ranked_uil}/25 teams, TAPPS 6A {ranked_tapps}/10 teams")

            return True
        except Exception as e:
            print(f"❌ Failed to restore from gold master: {e}")
            needs_update = True
    elif needs_restore:
        print("⚠️  Gold master file not found - will trigger update")
        needs_update = True

    # Only trigger automatic update if restore failed and file doesn't exist
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

    return not needs_update and not needs_restore

if __name__ == "__main__":
    check_and_update_rankings()
