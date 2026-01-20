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

    # ALWAYS restore from master file on startup to ensure latest rankings
    # This fixes Railway volume mount issues where old data persists
    if master_file.exists():
        print("🔄 Restoring rankings from gold master file (forced on startup)...")
        try:
            import shutil
            # Ensure data directory exists
            data_file.parent.mkdir(parents=True, exist_ok=True)
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
            print(f"   Last updated: {restored_data.get('last_updated', 'unknown')}")
            return True
        except Exception as e:
            print(f"❌ Failed to restore from gold master: {e}")

    # Fallback: check existing data
    needs_restore = False
    needs_update = False

    if not data_file.exists():
        print("⚠️  Rankings file does not exist")
        needs_restore = True
    else:
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)

            # Check if data is empty
            if not data.get('uil') and not data.get('private'):
                print("⚠️  Rankings file is empty")
                needs_restore = True
            else:
                # Verify data integrity - check UIL and TAPPS rankings
                uil_6a_teams = data.get('uil', {}).get('AAAAAA', [])
                ranked_6a = sum(1 for t in uil_6a_teams if t.get('rank') is not None and 1 <= t.get('rank') <= 25)

                tapps_6a_teams = data.get('private', {}).get('TAPPS_6A', [])
                ranked_tapps_6a = sum(1 for t in tapps_6a_teams if t.get('rank') is not None and 1 <= t.get('rank') <= 10)

                # Check if data is incomplete - require EXACTLY 25 for UIL and 10 for TAPPS
                if ranked_6a != 25:
                    print(f"⚠️  Rankings incomplete: UIL 6A has {ranked_6a}/25 ranked teams (need exactly 25)")
                    needs_restore = True
                elif ranked_tapps_6a != 10:
                    print(f"⚠️  Rankings incomplete: TAPPS 6A has {ranked_tapps_6a}/10 ranked teams (need exactly 10)")
                    needs_restore = True

                if not needs_restore:
                    # Check if master file is newer than current data file
                    if master_file.exists():
                        try:
                            with open(master_file, 'r') as f:
                                master_data = json.load(f)

                            master_updated = master_data.get('last_updated', '')
                            current_updated = data.get('last_updated', '')

                            if master_updated > current_updated:
                                print(f"🔄 Master file is newer ({master_updated} > {current_updated})")
                                needs_restore = True
                            else:
                                if 'last_updated' in data:
                                    last_update = datetime.fromisoformat(data['last_updated'])
                                    hours_old = (datetime.now() - last_update).total_seconds() / 3600
                                    print(f"✓ Rankings file OK: UIL 6A {ranked_6a}/25, TAPPS 6A {ranked_tapps_6a}/10 (last updated {hours_old:.1f} hours ago)")
                                else:
                                    print(f"✓ Rankings file OK: UIL 6A {ranked_6a}/25, TAPPS 6A {ranked_tapps_6a}/10")
                        except:
                            # If can't read master, just keep current data
                            if 'last_updated' in data:
                                last_update = datetime.fromisoformat(data['last_updated'])
                                hours_old = (datetime.now() - last_update).total_seconds() / 3600
                                print(f"✓ Rankings file OK: UIL 6A {ranked_6a}/25, TAPPS 6A {ranked_tapps_6a}/10 (last updated {hours_old:.1f} hours ago)")
                            else:
                                print(f"✓ Rankings file OK: UIL 6A {ranked_6a}/25, TAPPS 6A {ranked_tapps_6a}/10")
                    else:
                        if 'last_updated' in data:
                            last_update = datetime.fromisoformat(data['last_updated'])
                            hours_old = (datetime.now() - last_update).total_seconds() / 3600
                            print(f"✓ Rankings file OK: UIL 6A {ranked_6a}/25, TAPPS 6A {ranked_tapps_6a}/10 (last updated {hours_old:.1f} hours ago)")
                        else:
                            print(f"✓ Rankings file OK: UIL 6A {ranked_6a}/25, TAPPS 6A {ranked_tapps_6a}/10")

        except Exception as e:
            print(f"⚠️  Error reading rankings file: {e}")
            needs_restore = True

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
