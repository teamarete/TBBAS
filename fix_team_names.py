"""
Fix team name errors in source data before merging rankings

Corrections:
1. DHanis -> D'Hanis (TABC has wrong apostrophe format)
2. Bullard The Brook Hill School -> Tyler Brook Hill School (wrong city)
3. Midland Cristian -> Midland Christian (typo)
"""

import json
from pathlib import Path

def fix_team_names():
    """Apply team name corrections to weekly rankings data"""

    weekly_file = Path('data/weekly_rankings_20260105.json')

    with open(weekly_file, 'r') as f:
        data = json.load(f)

    corrections_made = []

    # Fix 1: DHanis -> D'Hanis in TABC UIL 1A
    tabc_1a = data.get('tabc', {}).get('uil', {}).get('1A', [])
    for team in tabc_1a:
        if team.get('team_name') == 'DHanis':
            team['team_name'] = "D'Hanis"
            corrections_made.append("TABC UIL 1A: DHanis -> D'Hanis")

    # Fix 2: Bullard The Brook Hill School -> Tyler Brook Hill School in TABC TAPPS 5A
    tabc_tapps_5a = data.get('tabc', {}).get('private', {}).get('TAPPS_5A', [])
    for team in tabc_tapps_5a:
        if 'Bullard The Brook Hill' in team.get('team_name', ''):
            team['team_name'] = 'Tyler Brook Hill School'
            corrections_made.append("TABC TAPPS 5A: Bullard The Brook Hill School -> Tyler Brook Hill School")

    # Fix 3: Midland Cristian -> Midland Christian in TABC TAPPS 5A
    for team in tabc_tapps_5a:
        if team.get('team_name') == 'Midland Cristian':
            team['team_name'] = 'Midland Christian'
            corrections_made.append("TABC TAPPS 5A: Midland Cristian -> Midland Christian")

    # Save corrected data
    with open(weekly_file, 'w') as f:
        json.dump(data, f, indent=2)

    print("Team Name Corrections Applied:")
    print("=" * 80)
    for correction in corrections_made:
        print(f"  ✓ {correction}")

    if not corrections_made:
        print("  No corrections needed - all team names correct")

    return len(corrections_made)

if __name__ == '__main__':
    count = fix_team_names()
    print(f"\nTotal corrections: {count}")
