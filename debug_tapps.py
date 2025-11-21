#!/usr/bin/env python3
import json
from tapps_district_mappings import get_tapps_district

# Load rankings to get exact team names
with open('data/rankings.json', 'r') as f:
    data = json.load(f)

teams_tapps = data.get('private', {}).get('TAPPS_6A', [])

print("Testing get_tapps_district with exact team names from rankings:")
print("=" * 70)

for team in teams_tapps:
    team_name = team['team_name']
    classification = 'TAPPS_6A'
    current_district = team.get('district')
    lookup_district = get_tapps_district(team_name, classification)

    print(f"Team: {team_name}")
    print(f"  Current district in rankings: {current_district}")
    print(f"  Lookup result: {lookup_district}")
    print()
