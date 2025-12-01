"""
One-time fix to restore proper ranking order for UIL 6A
Ensures teams are ranked 1-25 in the correct order with no duplicates or gaps
"""

import json
from pathlib import Path

data_file = Path(__file__).parent / 'data' / 'rankings.json'

# Define the correct ranking order from git (teams ranked 1-25)
correct_order = [
    'San Antonio Brennan',      # 1
    'Katy Seven Lakes',          # 2
    'Duncanville',              # 3
    'Atascocita',               # 4
    'North Crowley',            # 5
    'Plano',                    # 6
    'Austin Westlake',          # 7
    'Cibolo Steele',            # 8
    'Little Elm',               # 9
    'Allen',                    # 10
    'Desoto',                   # 11
    'Katy Jordan',              # 12
    'Cypress Falls',            # 13
    'Humble Summer Creek',      # 14
    'Lancaster',                # 15
    'San Antonio Harlan',       # 16
    'Pearland',                 # 17
    'Strake Jesuit',            # 18
    'Converse Judson',          # 19
    'Conroe Grand Oaks',        # 20
    'Grand Prairie',            # 21
    'Mans Lake Ridge',          # 22
    'South Grand Prairie',      # 23
    'Dickinson',                # 24
    'Mesquite Horn'             # 25
]

# Load rankings
with open(data_file, 'r') as f:
    data = json.load(f)

# Get current UIL 6A teams
current_teams = data['uil']['AAAAAA']

# Create a map of team names to their data
team_map = {team['team_name']: team for team in current_teams}

# Reorder teams and assign sequential ranks 1-25
reordered_teams = []
fixes_applied = 0

for rank, team_name in enumerate(correct_order, start=1):
    if team_name in team_map:
        team = team_map[team_name]
        old_rank = team.get('rank')
        if old_rank != rank:
            fixes_applied += 1
            print(f"✓ Fixed {team_name}: rank {old_rank} -> {rank}")
        team['rank'] = rank
        reordered_teams.append(team)
    else:
        # Team not found - create placeholder
        fixes_applied += 1
        print(f"✓ Added missing team {team_name} at rank {rank}")
        reordered_teams.append({
            'team_name': team_name,
            'rank': rank,
            'wins': None,
            'losses': None,
            'district': None
        })

# Add any remaining teams not in the correct_order list as unranked
for team_name, team_data in team_map.items():
    if team_name not in correct_order:
        team_data['rank'] = None
        reordered_teams.append(team_data)
        print(f"  Note: {team_name} marked as unranked (not in top 25)")

if fixes_applied > 0:
    # Replace UIL 6A data
    data['uil']['AAAAAA'] = reordered_teams

    # Save updated rankings
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n✓ Applied {fixes_applied} ranking fixes - all teams now properly ranked 1-25")
else:
    print("✓ No rank fixes needed - all teams already have correct ranks")
