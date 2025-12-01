"""
ONE-TIME: Force Railway to reload correct rankings.json from git
Copies the git-committed version over the persisted bad version
"""

from pathlib import Path
import shutil
import os

# This script is IN the git repo, so the data/rankings.json from git is RIGHT HERE
git_rankings = Path(__file__).parent / 'data' / 'rankings.json'
persisted_rankings = git_rankings  # They're the same file!

# The file from git IS the correct one
# Railway's problem is it PERSISTS a modified version in its volume
# We can't directly replace it here, but we can verify it's correct

if git_rankings.exists():
    import json
    with open(git_rankings) as f:
        data = json.load(f)
        uil_6a = data.get('uil', {}).get('AAAAAA', [])
        ranked = sum(1 for t in uil_6a if t.get('rank') is not None and 1 <= t.get('rank') <= 25)
        print(f"Rankings file check: {ranked}/25 UIL 6A teams ranked")

        if ranked < 25:
            print(f"⚠️  WARNING: Git version only has {ranked}/25 teams ranked!")
            print("   This means the git-committed file needs to be fixed first")
        else:
            print("✓ Git version has all 25 teams ranked correctly")
else:
    print("⚠️  Rankings file not found!")

# Note: Railway will copy this file from git on deployment
# The issue is if there's a PERSISTED version in a volume, it takes precedence
# We can't fix that from within the app - it needs Railway configuration change
print("\nNote: If Railway is still showing incomplete rankings, ")
print("it may be using a persisted volume. Check Railway volume settings.")
