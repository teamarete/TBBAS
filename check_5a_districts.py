#!/usr/bin/env python3
"""Check 5A district assignments"""

import json

# Load rankings
with open('data/rankings.json', 'r') as f:
    data = json.load(f)

# Check 5A schools we updated
target_schools = [
    'Frisco Heritage', 'Frisco Memorial', 'Dallas Highland Park',
    'Killeen Ellison', 'Beaumont United', 'Beaumont West Brook',
    'Port Arthur Memorial', 'San Antonio Alamo Heights', 'San Antonio Wagner',
    'Northside Jay', 'Corpus Christi Veterans Memorial'
]

print('5A (AAAAA) Schools - District Verification')
print('=' * 70)

teams_5a = data.get('uil', {}).get('AAAAA', [])
total_5a = len(teams_5a)
with_districts = 0
target_found = 0

for team in teams_5a[:25]:
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
for team in teams_5a[:25]:
    if not team.get('district'):
        print(f'  Rank {team.get("rank", "?"):2d} | {team["team_name"]:45s}')

print('=' * 70)
print(f'5A District Coverage: {with_districts}/{min(25, total_5a)} teams ({100*with_districts/min(25, total_5a):.1f}%)')
print(f'Target schools found: {target_found}/{len(target_schools)}')
