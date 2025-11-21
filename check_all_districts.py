#!/usr/bin/env python3
"""Check district assignments across all UIL and TAPPS classifications"""

import json

# Load rankings
with open('data/rankings.json', 'r') as f:
    data = json.load(f)

print('=' * 80)
print('COMPLETE DISTRICT COVERAGE REPORT')
print('=' * 80)

# UIL Classifications
print('\nUIL SCHOOLS:')
print('-' * 80)
uil_classifications = ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']
uil_names = ['6A', '5A', '4A', '3A', '2A', '1A']

uil_total = 0
uil_with_districts = 0

for classification, name in zip(uil_classifications, uil_names):
    teams = data.get('uil', {}).get(classification, [])
    teams_count = len(teams)
    with_districts = sum(1 for team in teams if team.get('district'))

    uil_total += teams_count
    uil_with_districts += with_districts

    coverage = (100 * with_districts / teams_count) if teams_count > 0 else 0
    status = '✓' if coverage == 100 else '⚠'

    print(f'{status} UIL {name:3s}: {with_districts:3d}/{teams_count:3d} teams ({coverage:5.1f}%)')

    # Show missing districts if any
    missing = [team for team in teams if not team.get('district')]
    if missing and len(missing) <= 5:
        for team in missing:
            print(f'     - {team["team_name"]}')

print('-' * 80)
uil_coverage = (100 * uil_with_districts / uil_total) if uil_total > 0 else 0
print(f'UIL Total: {uil_with_districts}/{uil_total} teams ({uil_coverage:.1f}%)')

# TAPPS Classifications
print('\nTAPPS/SPC SCHOOLS:')
print('-' * 80)
tapps_classifications = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']

tapps_total = 0
tapps_with_districts = 0

for classification in tapps_classifications:
    teams = data.get('private', {}).get(classification, [])
    teams_count = len(teams)
    with_districts = sum(1 for team in teams if team.get('district'))

    tapps_total += teams_count
    tapps_with_districts += with_districts

    coverage = (100 * with_districts / teams_count) if teams_count > 0 else 0
    status = '✓' if coverage == 100 else '⚠'

    print(f'{status} {classification:10s}: {with_districts:3d}/{teams_count:3d} teams ({coverage:5.1f}%)')

    # Show missing districts if any
    missing = [team for team in teams if not team.get('district')]
    if missing and len(missing) <= 5:
        for team in missing:
            print(f'     - {team["team_name"]}')

print('-' * 80)
tapps_coverage = (100 * tapps_with_districts / tapps_total) if tapps_total > 0 else 0
print(f'TAPPS Total: {tapps_with_districts}/{tapps_total} teams ({tapps_coverage:.1f}%)')

# Overall Summary
print('\n' + '=' * 80)
print('OVERALL SUMMARY:')
print('=' * 80)
grand_total = uil_total + tapps_total
grand_with_districts = uil_with_districts + tapps_with_districts
grand_coverage = (100 * grand_with_districts / grand_total) if grand_total > 0 else 0

print(f'UIL Teams:   {uil_with_districts:3d}/{uil_total:3d} ({uil_coverage:5.1f}%)')
print(f'TAPPS Teams: {tapps_with_districts:3d}/{tapps_total:3d} ({tapps_coverage:5.1f}%)')
print('-' * 80)
print(f'TOTAL:       {grand_with_districts:3d}/{grand_total:3d} ({grand_coverage:5.1f}%)')
print('=' * 80)

if grand_coverage == 100:
    print('\n✓ COMPLETE DISTRICT COVERAGE ACHIEVED!')
    print('All ranked teams have district assignments.')
else:
    missing_count = grand_total - grand_with_districts
    print(f'\n⚠ {missing_count} teams still need district assignments.')
