"""
Find exact duplicate team names (case-insensitive) in rankings
More thorough than normalized duplicate checking
"""

import json
from collections import defaultdict

# Load rankings
with open('data/rankings.json') as f:
    data = json.load(f)

print("=" * 100)
print("CHECKING FOR EXACT DUPLICATE TEAM NAMES")
print("=" * 100)
print()

total_duplicates = 0

# Check UIL
uil_classes = [('AAAAAA', '6A'), ('AAAAA', '5A'), ('AAAA', '4A'), ('AAA', '3A'), ('AA', '2A'), ('A', '1A')]
for class_code, class_name in uil_classes:
    if class_code in data['uil']:
        teams = data['uil'][class_code]

        # Group by lowercase name
        name_groups = defaultdict(list)
        for i, team in enumerate(teams):
            name_lower = team['team_name'].lower().strip()
            name_groups[name_lower].append((i, team))

        # Find duplicates
        for name_lower, team_list in name_groups.items():
            if len(team_list) > 1:
                print(f"UIL {class_name} - EXACT DUPLICATE FOUND:")
                for idx, team in team_list:
                    rank = team.get('rank', '—')
                    wins = team.get('wins', '—')
                    losses = team.get('losses', '—')
                    record = f"{wins}-{losses}" if wins is not None else "—"
                    print(f"  Rank {rank}: {team['team_name']} ({record})")
                print()
                total_duplicates += len(team_list) - 1

# Check TAPPS
tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
tapps_display = ['TAPPS 6A', 'TAPPS 5A', 'TAPPS 4A', 'TAPPS 3A', 'TAPPS 2A', 'TAPPS 1A']
for class_code, class_display in zip(tapps_classes, tapps_display):
    if class_code in data['private']:
        teams = data['private'][class_code]

        # Group by lowercase name
        name_groups = defaultdict(list)
        for i, team in enumerate(teams):
            name_lower = team['team_name'].lower().strip()
            name_groups[name_lower].append((i, team))

        # Find duplicates
        for name_lower, team_list in name_groups.items():
            if len(team_list) > 1:
                print(f"{class_display} - EXACT DUPLICATE FOUND:")
                for idx, team in team_list:
                    rank = team.get('rank', '—')
                    wins = team.get('wins', '—')
                    losses = team.get('losses', '—')
                    record = f"{wins}-{losses}" if wins is not None else "—"
                    print(f"  Rank {rank}: {team['team_name']} ({record})")
                print()
                total_duplicates += len(team_list) - 1

print("=" * 100)
if total_duplicates == 0:
    print("✓ No exact duplicates found!")
else:
    print(f"TOTAL EXACT DUPLICATES FOUND: {total_duplicates}")
print("=" * 100)
