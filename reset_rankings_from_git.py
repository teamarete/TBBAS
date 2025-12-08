"""
Force reset of rankings.json to the version committed in git
This fixes issues where Railway has outdated/incomplete rankings data
"""

import shutil
from pathlib import Path

# Paths
data_file = Path(__file__).parent / 'data' / 'rankings.json'
backup_file = Path(__file__).parent / 'data' / 'rankings.json.backup'

print("=" * 80)
print("RESETTING RANKINGS TO GIT VERSION")
print("=" * 80)

# Check if rankings exists
if data_file.exists():
    # Backup current rankings
    shutil.copy(data_file, backup_file)
    print(f"✓ Backed up current rankings to {backup_file}")

    # Delete current rankings
    data_file.unlink()
    print(f"✓ Deleted current rankings file")
else:
    print("⚠️  No existing rankings file found")

print("\nRankings file has been reset. On next startup, the app will use")
print("the rankings.json committed in git, which has all 25 UIL teams and 10 TAPPS teams.")
print("\nDeploy this change to Railway to apply the fix.")
print("=" * 80)
