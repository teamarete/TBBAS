"""
Complete UIL rankings to ensure exactly 25 teams per classification
Falls back to TABC rankings when we don't have enough data
"""

import json
from scraper import TABCScraper

print("=" * 80)
print("COMPLETING UIL RANKINGS TO TOP 25 PER CLASSIFICATION")
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

uil_classes = [('AAAAAA', '6A'), ('AAAAA', '5A'), ('AAAA', '4A'), ('AAA', '3A'), ('AA', '2A'), ('A', '1A')]

total_added = 0

for class_code, class_name in uil_classes:
    current_teams = data['uil'].get(class_code, [])
    current_count = len(current_teams)

    if current_count >= 25:
        print(f"✓ UIL {class_name}: {current_count}/25 (complete)")
        continue

    needed = 25 - current_count
    print(f"⚠ UIL {class_name}: {current_count}/25 (need {needed} more)")

    # Get TABC teams for this classification
    tabc_teams = tabc_data['uil'].get(class_code, [])

    if not tabc_teams:
        print(f"  ⚠ No TABC rankings available for UIL {class_name}")
        continue

    # Get existing team names (normalized for comparison)
    existing_names = {t['team_name'].lower().strip() for t in current_teams}

    # Add teams from TABC until we reach 25
    added = 0
    for tabc_team in tabc_teams:
        if len(current_teams) >= 25:
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

    # Re-rank all teams 1-25
    ranked_teams = [t for t in current_teams if t.get('rank')]
    ranked_teams.sort(key=lambda x: x.get('rank', 999))

    for i, team in enumerate(ranked_teams[:25], start=1):
        team['rank'] = i

    # Update data
    data['uil'][class_code] = current_teams

    if added > 0:
        print(f"  ✓ Now has {len(current_teams)}/25 teams")
    print()

# Save updated rankings
with open('data/rankings.json', 'w') as f:
    json.dump(data, f, indent=2)

print("=" * 80)
print(f"✓ Added {total_added} teams from TABC to complete UIL rankings")
print("✓ Rankings saved to data/rankings.json")
print("=" * 80)

# Show final counts
print()
print("FINAL UIL RANKINGS COUNT:")
print("-" * 80)
for class_code, class_name in uil_classes:
    teams = data['uil'].get(class_code, [])
    ranked = sum(1 for t in teams if t.get('rank') and 1 <= t['rank'] <= 25)
    status = "✓" if ranked == 25 else "⚠"
    print(f"{status} UIL {class_name}: {ranked}/25 teams")
