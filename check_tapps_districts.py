#!/usr/bin/env python3
"""Check TAPPS/SPC district assignments"""

import json

# Load rankings
with open('data/rankings.json', 'r') as f:
    data = json.load(f)

# Check TAPPS 6A schools we updated
target_schools = [
    'Dallas Parish Episcopal', 'Addison Greenhill', 'Dallas St. Mark',
    'Houston Christian', 'TMI Episcopal', 'St. Michael', 'Antonian Prep',
    'John Paul II', 'Bishop Lynch', 'Kinkaid'
]

print('TAPPS 6A / SPC 4A Schools - District Verification')
print('=' * 70)

teams_tapps = data.get('private', {}).get('TAPPS_6A', [])
total_tapps = len(teams_tapps)
with_districts = 0
target_found = 0

for team in teams_tapps:
    team_name = team['team_name']
    district = team.get('district', 'MISSING')
    rank = team.get('rank', '?')

    # Check if this is one of our target schools
    is_target = any(target in team_name for target in target_schools)
    marker = '✓' if is_target else ' '

    if district != 'MISSING' and district is not None:
        with_districts += 1

    if is_target:
        target_found += 1
        print(f'{marker} Rank {rank:2d} | {team_name:45s} | District {district}')

# Show any missing districts
print('\nSchools MISSING districts:')
missing_count = 0
for team in teams_tapps:
    if not team.get('district'):
        missing_count += 1
        print(f'  Rank {team.get("rank", "?"):2d} | {team["team_name"]:45s}')

if missing_count == 0:
    print('  (none)')

print('=' * 70)
print(f'TAPPS 6A District Coverage: {with_districts}/{total_tapps} teams ({100*with_districts/total_tapps:.1f}%)')
print(f'Target schools found: {target_found}')
