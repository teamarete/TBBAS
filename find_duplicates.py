"""
Find duplicate teams in rankings (same team with different name variations)
"""

import json
from collections import defaultdict
from school_name_normalizer import SchoolNameNormalizer

# Load rankings
with open('data/rankings.json') as f:
    data = json.load(f)

normalizer = SchoolNameNormalizer()

print("=" * 100)
print("CHECKING FOR DUPLICATE TEAMS IN RANKINGS")
print("=" * 100)
print()

all_duplicates = []

# Check UIL
uil_classes = [('AAAAAA', '6A'), ('AAAAA', '5A'), ('AAAA', '4A'), ('AAA', '3A'), ('AA', '2A'), ('A', '1A')]
for class_code, class_name in uil_classes:
    if class_code in data['uil']:
        teams = data['uil'][class_code]

        # Group by normalized name
        name_groups = defaultdict(list)
        for team in teams:
            normalized = normalizer.normalize(team['team_name']).lower()
            name_groups[normalized].append(team)

        # Find duplicates
        for normalized, team_list in name_groups.items():
            if len(team_list) > 1:
                print(f"UIL {class_name} - DUPLICATE FOUND:")
                for team in team_list:
                    rank = team.get('rank', 'unranked')
                    record = f"{team.get('wins')}-{team.get('losses')}" if team.get('wins') is not None else '—'
                    print(f"  Rank {rank}: {team['team_name']} ({record})")
                print()
                all_duplicates.append({
                    'classification': f'UIL {class_name}',
                    'teams': team_list
                })

# Check TAPPS
tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
tapps_display = ['TAPPS 6A', 'TAPPS 5A', 'TAPPS 4A', 'TAPPS 3A', 'TAPPS 2A', 'TAPPS 1A']
for class_code, class_display in zip(tapps_classes, tapps_display):
    if class_code in data['private']:
        teams = data['private'][class_code]

        # Group by normalized name
        name_groups = defaultdict(list)
        for team in teams:
            normalized = normalizer.normalize(team['team_name']).lower()
            name_groups[normalized].append(team)

        # Find duplicates
        for normalized, team_list in name_groups.items():
            if len(team_list) > 1:
                print(f"{class_display} - DUPLICATE FOUND:")
                for team in team_list:
                    rank = team.get('rank', 'unranked')
                    record = f"{team.get('wins')}-{team.get('losses')}" if team.get('wins') is not None else '—'
                    print(f"  Rank {rank}: {team['team_name']} ({record})")
                print()
                all_duplicates.append({
                    'classification': class_display,
                    'teams': team_list
                })

if all_duplicates:
    print("=" * 100)
    print(f"TOTAL DUPLICATES FOUND: {len(all_duplicates)}")
    print("=" * 100)
    print()
    print("RECOMMENDED ACTION:")
    print("For each duplicate group, keep the team with:")
    print("  1. The better record (if both have records)")
    print("  2. The ranked position (if one is ranked and one isn't)")
    print("  3. The more complete name (e.g., 'Beaumont Memorial' over 'Bmt Memorial')")
else:
    print("✓ No duplicates found!")
