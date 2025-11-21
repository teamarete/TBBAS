#!/usr/bin/env python3
"""Check 2A district assignments"""

import json

# Load rankings
with open('data/rankings.json', 'r') as f:
    data = json.load(f)

print('2A (AA) Schools - District Verification')
print('=' * 70)

teams_2a = data.get('uil', {}).get('AA', [])
total_2a = len(teams_2a)
with_districts = 0

for team in teams_2a[:25]:
    team_name = team['team_name']
    district = team.get('district', 'MISSING')
    rank = team.get('rank', '?')

    if district != 'MISSING':
        with_districts += 1

    # Show Thorndale specifically
    if 'Thorndale' in team_name:
        print(f'✓ Rank {rank:2d} | {team_name:45s} | District {district}')

# Show any missing districts
print('\nSchools MISSING districts:')
missing_count = 0
for team in teams_2a[:25]:
    if not team.get('district'):
        missing_count += 1
        print(f'  Rank {team.get("rank", "?"):2d} | {team["team_name"]:45s}')

if missing_count == 0:
    print('  (none)')

print('=' * 70)
print(f'2A District Coverage: {with_districts}/{min(25, total_2a)} teams ({100*with_districts/min(25, total_2a):.1f}%)')
