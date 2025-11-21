#!/usr/bin/env python3
"""Check 1A district assignments"""

import json

# Load rankings
with open('data/rankings.json', 'r') as f:
    data = json.load(f)

# Check 1A schools we updated
target_schools = [
    'Wildorado', 'Water Valley', 'Benjamin',
    'Avery', 'Coolidge', 'Tilden McMullen County', 'McMullen County', 'Tilden'
]

print('1A (A) Schools - District Verification')
print('=' * 70)

teams_1a = data.get('uil', {}).get('A', [])
total_1a = len(teams_1a)
with_districts = 0
target_found = 0

for team in teams_1a[:25]:
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

# Show any missing districts
print('\nSchools MISSING districts:')
missing_count = 0
for team in teams_1a[:25]:
    if not team.get('district'):
        missing_count += 1
        print(f'  Rank {team.get("rank", "?"):2d} | {team["team_name"]:45s}')

if missing_count == 0:
    print('  (none)')

print('=' * 70)
print(f'1A District Coverage: {with_districts}/{min(25, total_1a)} teams ({100*with_districts/min(25, total_1a):.1f}%)')
print(f'Target schools found: {target_found}')
