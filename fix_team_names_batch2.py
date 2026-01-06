"""
Fix team name errors in source data - Batch 2

Corrections:
1. Liberty Eylau -> Liberty-Eylau (TABC has no hyphen, MaxPreps has hyphen) - UIL 3A
2. LaMarque -> La Marque (TABC has one word, MaxPreps has two words) - UIL 4A
3. Centerville: Move from UIL 1A to UIL 2A in MaxPreps (classification error)
   Note: Groveton Centerville stays in 1A - these are different schools
"""

import json
from pathlib import Path

def fix_team_names_batch2():
    """Apply team name corrections to weekly rankings data"""

    weekly_file = Path('data/weekly_rankings_20260105.json')

    with open(weekly_file, 'r') as f:
        data = json.load(f)

    corrections_made = []

    # Fix 1: Liberty Eylau -> Liberty-Eylau in TABC UIL 3A
    tabc_3a = data.get('tabc', {}).get('uil', {}).get('3A', [])
    for team in tabc_3a:
        if team.get('team_name') == 'Liberty Eylau':
            team['team_name'] = 'Liberty-Eylau'
            corrections_made.append("TABC UIL 3A: Liberty Eylau -> Liberty-Eylau")

    # Fix 2: LaMarque -> La Marque in TABC UIL 4A
    tabc_4a = data.get('tabc', {}).get('uil', {}).get('4A', [])
    for team in tabc_4a:
        if team.get('team_name') == 'LaMarque':
            team['team_name'] = 'La Marque'
            corrections_made.append("TABC UIL 4A: LaMarque -> La Marque")

    # Fix 3: Move Centerville from 1A to 2A in MaxPreps (classification error)
    # Groveton Centerville is different and stays in 1A
    maxpreps_1a = data.get('maxpreps', {}).get('uil', {}).get('1A', [])
    centerville_team = None
    for i, team in enumerate(maxpreps_1a):
        # Only move plain "Centerville", NOT "Groveton Centerville"
        if team.get('team_name') == 'Centerville':
            centerville_team = team.copy()
            maxpreps_1a.pop(i)
            corrections_made.append("MaxPreps UIL 1A: Removed Centerville (moved to 2A)")
            break

    if centerville_team:
        maxpreps_2a = data.get('maxpreps', {}).get('uil', {}).get('2A', [])
        maxpreps_2a.append(centerville_team)
        corrections_made.append("MaxPreps UIL 2A: Added Centerville")

    # Save corrected data
    with open(weekly_file, 'w') as f:
        json.dump(data, f, indent=2)

    print("Team Name Corrections Applied - Batch 2:")
    print("=" * 80)
    for correction in corrections_made:
        print(f"  ✓ {correction}")

    if not corrections_made:
        print("  No corrections needed - all team names correct")

    return len(corrections_made)

if __name__ == '__main__':
    count = fix_team_names_batch2()
    print(f"\nTotal corrections: {count}")
