"""
Thoroughly find all duplicates using school_abbreviations variations
"""

import json
from collections import defaultdict
from school_abbreviations import get_search_variations

data = json.load(open('data/rankings.json'))

print('Checking all classifications for semantic duplicates...')
print('=' * 100)
print()

all_duplicate_groups = []

# Check UIL
uil_classes = [('AAAAAA', '6A'), ('AAAAA', '5A'), ('AAAA', '4A'), ('AAA', '3A'), ('AA', '2A'), ('A', '1A')]
for class_code, class_name in uil_classes:
    teams = data['uil'][class_code]

    # Build variation map
    variation_to_teams = defaultdict(list)
    for team in teams:
        name = team['team_name']
        variations = get_search_variations(name)
        for var in variations:
            variation_to_teams[var.lower()].append(team)

    # Find duplicates
    for var, team_list in variation_to_teams.items():
        if len(team_list) > 1:
            unique_names = set(t['team_name'] for t in team_list)
            if len(unique_names) > 1:
                print(f'UIL {class_name} - DUPLICATE GROUP:')
                for t in team_list:
                    rank = t.get('rank', '?')
                    wins = t.get('wins')
                    losses = t.get('losses')
                    record = f'{wins}-{losses}' if wins is not None else 'no record'
                    print(f'  Rank {rank:>2}: {t["team_name"]:<40} ({record})')
                all_duplicate_groups.append((class_code, class_name, team_list))
                print()

# Check TAPPS
tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
tapps_display = ['TAPPS 6A', 'TAPPS 5A', 'TAPPS 4A', 'TAPPS 3A', 'TAPPS 2A', 'TAPPS 1A']
for class_code, class_display in zip(tapps_classes, tapps_display):
    teams = data['private'][class_code]

    # Build variation map
    variation_to_teams = defaultdict(list)
    for team in teams:
        name = team['team_name']
        variations = get_search_variations(name)
        for var in variations:
            variation_to_teams[var.lower()].append(team)

    # Find duplicates
    for var, team_list in variation_to_teams.items():
        if len(team_list) > 1:
            unique_names = set(t['team_name'] for t in team_list)
            if len(unique_names) > 1:
                print(f'{class_display} - DUPLICATE GROUP:')
                for t in team_list:
                    rank = t.get('rank', '?')
                    wins = t.get('wins')
                    losses = t.get('losses')
                    record = f'{wins}-{losses}' if wins is not None else 'no record'
                    print(f'  Rank {rank:>2}: {t["team_name"]:<40} ({record})')
                all_duplicate_groups.append((class_code, class_display, team_list))
                print()

print('=' * 100)
print(f'Total duplicate groups found: {len(all_duplicate_groups)}')
