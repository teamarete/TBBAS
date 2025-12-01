"""
One-time fix to restore ranks for Strake Jesuit and Mesquite Horn
These teams have rank data in git but it gets lost during deployment
"""

import json
from pathlib import Path

data_file = Path(__file__).parent / 'data' / 'rankings.json'

# Load rankings
with open(data_file, 'r') as f:
    data = json.load(f)

# Fix Strake Jesuit and Mesquite Horn ranks
fixes_applied = 0
for team in data['uil']['AAAAAA']:
    if team['team_name'] == 'Strake Jesuit' and team.get('rank') is None:
        team['rank'] = 18
        fixes_applied += 1
        print(f"✓ Fixed Strake Jesuit rank: 18")
    elif team['team_name'] == 'Mesquite Horn' and team.get('rank') is None:
        team['rank'] = 25
        fixes_applied += 1
        print(f"✓ Fixed Mesquite Horn rank: 25")

if fixes_applied > 0:
    # Save updated rankings
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n✓ Applied {fixes_applied} rank fixes to rankings.json")
else:
    print("✓ No rank fixes needed - all teams already have ranks")
