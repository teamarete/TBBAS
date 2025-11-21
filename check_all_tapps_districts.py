#!/usr/bin/env python3
"""Check TAPPS district assignments across all classifications"""

import json

# Load rankings
with open('data/rankings.json', 'r') as f:
    data = json.load(f)

print('TAPPS District Coverage Summary')
print('=' * 80)

# Check each TAPPS classification
classifications = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']

total_teams = 0
total_with_districts = 0

for classification in classifications:
    teams = data.get('private', {}).get(classification, [])
    teams_count = len(teams)
    with_districts = sum(1 for team in teams if team.get('district'))

    total_teams += teams_count
    total_with_districts += with_districts

    coverage = (100 * with_districts / teams_count) if teams_count > 0 else 0
    status = '✓' if coverage == 100 else '⚠'

    print(f'{status} {classification:12s}: {with_districts:3d}/{teams_count:3d} teams ({coverage:5.1f}%)')

    # Show missing districts if any
    missing = [team for team in teams if not team.get('district')]
    if missing:
        print(f'   Missing districts:')
        for team in missing[:10]:  # Show first 10
            print(f'     - Rank {team.get("rank", "?"):2d}: {team["team_name"]}')
        if len(missing) > 10:
            print(f'     ... and {len(missing) - 10} more')

print('=' * 80)
total_coverage = (100 * total_with_districts / total_teams) if total_teams > 0 else 0
print(f'Overall TAPPS Coverage: {total_with_districts}/{total_teams} teams ({total_coverage:.1f}%)')
