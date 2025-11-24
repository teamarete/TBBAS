"""
Complete TAPPS rankings to ensure exactly 10 teams per classification
Falls back to TABC rankings when we don't have enough data
"""

import json
from scraper import TABCScraper

print("=" * 80)
print("COMPLETING TAPPS RANKINGS TO TOP 10 PER CLASSIFICATION")
print("=" * 80)
print()
print("Using TABC rankings as fallback for missing teams...")
print()

# Load current rankings
with open('data/rankings.json') as f:
    data = json.load(f)

# Scrape latest TABC rankings
tabc_scraper = TABCScraper()
tabc_data = tabc_scraper.scrape_all()

tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
tapps_display = ['TAPPS 6A', 'TAPPS 5A', 'TAPPS 4A', 'TAPPS 3A', 'TAPPS 2A', 'TAPPS 1A']

total_added = 0

for class_code, class_display in zip(tapps_classes, tapps_display):
    current_teams = data['private'].get(class_code, [])
    current_count = len(current_teams)

    if current_count >= 10:
        print(f"✓ {class_display}: {current_count}/10 (complete)")
        continue

    needed = 10 - current_count
    print(f"⚠ {class_display}: {current_count}/10 (need {needed} more)")

    # Get TABC teams for this classification
    tabc_teams = tabc_data['private'].get(class_code, [])

    if not tabc_teams:
        print(f"  ⚠ No TABC rankings available for {class_display}")
        continue

    # Get existing team names (normalized for comparison)
    existing_names = {t['team_name'].lower().strip() for t in current_teams}

    # Add teams from TABC until we reach 10
    added = 0
    for tabc_team in tabc_teams:
        if len(current_teams) >= 10:
            break

        team_name = tabc_team['team_name']

        # Check if team already exists (case-insensitive)
        if team_name.lower().strip() in existing_names:
            continue

        # Add team from TABC
        new_team = {
            'team_name': team_name,
            'district': tabc_team.get('district'),
            'rank': len(current_teams) + 1,  # Assign next rank
            'wins': None,
            'losses': None,
            'games': None,
            'ppg': None,
            'opp_ppg': None
        }

        current_teams.append(new_team)
        existing_names.add(team_name.lower().strip())
        added += 1
        total_added += 1
        print(f"  + Added rank {new_team['rank']}: {team_name} (from TABC)")

    # Re-rank all teams 1-10
    ranked_teams = [t for t in current_teams if t.get('rank')]
    ranked_teams.sort(key=lambda x: x.get('rank', 999))

    for i, team in enumerate(ranked_teams[:10], start=1):
        team['rank'] = i

    # Update data
    data['private'][class_code] = current_teams

    if added > 0:
        print(f"  ✓ Now has {len(current_teams)}/10 teams")
    print()

# Save updated rankings
with open('data/rankings.json', 'w') as f:
    json.dump(data, f, indent=2)

print("=" * 80)
print(f"✓ Added {total_added} teams from TABC to complete TAPPS rankings")
print("✓ Rankings saved to data/rankings.json")
print("=" * 80)

# Show final counts
print()
print("FINAL TAPPS RANKINGS COUNT:")
print("-" * 80)
for class_code, class_display in zip(tapps_classes, tapps_display):
    teams = data['private'].get(class_code, [])
    ranked = sum(1 for t in teams if t.get('rank') and 1 <= t['rank'] <= 10)
    status = "✓" if ranked == 10 else "⚠"
    print(f"{status} {class_display}: {ranked}/10 teams")
