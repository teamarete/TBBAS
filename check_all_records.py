"""Check record coverage for all classifications"""
import json

with open('data/rankings.json') as f:
    data = json.load(f)

print("=" * 80)
print("RECORD COVERAGE BY CLASSIFICATION")
print("=" * 80)

# UIL Classifications
print("\nUIL CLASSIFICATIONS:")
print("-" * 80)
uil_classes = ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']
uil_names = ['6A', '5A', '4A', '3A', '2A', '1A']

uil_total_ranked = 0
uil_total_with_records = 0
uil_missing = []

for class_code, class_name in zip(uil_classes, uil_names):
    if class_code in data['uil']:
        teams = data['uil'][class_code]
        ranked_teams = [t for t in teams if t.get('rank')]
        teams_with_records = [t for t in ranked_teams if t.get('wins') is not None]

        uil_total_ranked += len(ranked_teams)
        uil_total_with_records += len(teams_with_records)

        status = "✓" if len(teams_with_records) == len(ranked_teams) else "✗"
        print(f"  {status} UIL {class_name}: {len(teams_with_records)}/{len(ranked_teams)} ranked teams have records")

        # Track missing teams
        for t in ranked_teams:
            if t.get('wins') is None:
                uil_missing.append({
                    'classification': f'UIL {class_name}',
                    'rank': t.get('rank'),
                    'team': t.get('team_name')
                })

# TAPPS Classifications
print("\nTAPPS CLASSIFICATIONS:")
print("-" * 80)
tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
tapps_display_names = ['TAPPS 6A', 'TAPPS 5A', 'TAPPS 4A', 'TAPPS 3A', 'TAPPS 2A', 'TAPPS 1A']

tapps_total_ranked = 0
tapps_total_with_records = 0
tapps_missing = []

for class_name, display_name in zip(tapps_classes, tapps_display_names):
    if class_name in data['private']:
        teams = data['private'][class_name]
        ranked_teams = [t for t in teams if t.get('rank')]
        teams_with_records = [t for t in ranked_teams if t.get('wins') is not None]

        tapps_total_ranked += len(ranked_teams)
        tapps_total_with_records += len(teams_with_records)

        status = "✓" if len(teams_with_records) == len(ranked_teams) else "✗"
        print(f"  {status} {display_name}: {len(teams_with_records)}/{len(ranked_teams)} ranked teams have records")

        # Track missing teams
        for t in ranked_teams:
            if t.get('wins') is None:
                tapps_missing.append({
                    'classification': display_name,
                    'rank': t.get('rank'),
                    'team': t.get('team_name')
                })

# Overall summary
print("\n" + "=" * 80)
print("OVERALL SUMMARY:")
print("=" * 80)
if uil_total_ranked > 0:
    print(f"UIL:   {uil_total_with_records}/{uil_total_ranked} ranked teams have records ({100*uil_total_with_records/uil_total_ranked:.1f}%)")
if tapps_total_ranked > 0:
    print(f"TAPPS: {tapps_total_with_records}/{tapps_total_ranked} ranked teams have records ({100*tapps_total_with_records/tapps_total_ranked:.1f}%)")
else:
    print(f"TAPPS: No ranked teams found in data")
total = uil_total_ranked + tapps_total_ranked
if total > 0:
    print(f"TOTAL: {uil_total_with_records + tapps_total_with_records}/{total} ranked teams have records ({100*(uil_total_with_records + tapps_total_with_records)/total:.1f}%)")

# List missing teams
if uil_missing or tapps_missing:
    print("\n" + "=" * 80)
    print("TEAMS WITHOUT RECORDS:")
    print("=" * 80)

    if uil_missing:
        print("\nUIL Teams Missing Records:")
        for item in uil_missing:
            print(f"  {item['classification']} - Rank {item['rank']}: {item['team']}")

    if tapps_missing:
        print("\nTAPPS Teams Missing Records:")
        for item in tapps_missing:
            print(f"  {item['classification']} - Rank {item['rank']}: {item['team']}")
else:
    print("\n✓ All ranked teams have complete game records!")
