"""
ONE-TIME: Force Railway to reload rankings.json from git
Deletes the persisted rankings file so it gets copied fresh from git on next request
"""

from pathlib import Path
import os

data_file = Path(__file__).parent / 'data' / 'rankings.json'

if data_file.exists():
    # Delete the persisted file
    data_file.unlink()
    print("✓ Deleted persisted rankings.json - will reload from git on next request")
else:
    print("  Rankings file doesn't exist - nothing to delete")

# Also delete backup if it exists
backup_file = Path(__file__).parent / 'data' / 'rankings.json.backup'
if backup_file.exists():
    backup_file.unlink()
    print("✓ Deleted backup file")
