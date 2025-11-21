#!/usr/bin/env python3
"""Check 3A district assignments"""

import json

# Load rankings
with open('data/rankings.json', 'r') as f:
    data = json.load(f)

# Check 3A schools we updated
target_schools = [
    'Wichita Falls City View', 'City View', 'Tuscola Jim Ned', 'Jim Ned',
    'Jefferson', 'Hooks', 'Texarkana Liberty-Eylau', 'Liberty-Eylau',
    'Tatum', 'Poth', 'Crystal City', 'Lytle',
    'Aransas Pass', 'Corpus Christi London', 'San Antonio Cole'
]

print('3A (AAA) Schools - District Verification')
print('=' * 70)

teams_3a = data.get('uil', {}).get('AAA', [])
total_3a = len(teams_3a)
with_districts = 0
target_found = 0

for team in teams_3a[:25]:
    team_name = team['team_name']
    district = team.get('district', 'MISSING')
    rank = team.get('rank', '?')

    # Check if this is one of our target schools
    is_target = any(target in team_name for target in target_schools)
    marker = '✓' if is_target else ' '

    if district != 'MISSING':
        with_districts += 1

    if is_target:
        target_found += 1
        print(f'{marker} Rank {rank:2d} | {team_name:45s} | District {district}')

# Show any missing districts too
print('\nSchools MISSING districts:')
missing_count = 0
for team in teams_3a[:25]:
    if not team.get('district'):
        missing_count += 1
        print(f'  Rank {team.get("rank", "?"):2d} | {team["team_name"]:45s}')

if missing_count == 0:
    print('  (none)')

print('=' * 70)
print(f'3A District Coverage: {with_districts}/{min(25, total_3a)} teams ({100*with_districts/min(25, total_3a):.1f}%)')
print(f'Target schools found: {target_found}')
