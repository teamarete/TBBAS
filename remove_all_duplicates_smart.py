"""
Remove duplicate teams using school_abbreviations variations
Keeps the best version: ranked > unranked, with record > without, better record > worse
"""

import json
from collections import defaultdict
from school_abbreviations import get_search_variations

# Load rankings
with open('data/rankings.json') as f:
    data = json.load(f)

print("=" * 100)
print("REMOVING ALL DUPLICATES FROM RANKINGS")
print("=" * 100)
print()

duplicates_removed = 0

# Process UIL
uil_classes = [('AAAAAA', '6A'), ('AAAAA', '5A'), ('AAAA', '4A'), ('AAA', '3A'), ('AA', '2A'), ('A', '1A')]
for class_code, class_name in uil_classes:
    if class_code not in data['uil']:
        continue

    teams = data['uil'][class_code]

    # Build variation groups
    variation_groups = defaultdict(list)
    for i, team in enumerate(teams):
        name = team['team_name']
        variations = get_search_variations(name)
        # Use shortest variation as group key
        key = min(variations, key=len).lower()
        variation_groups[key].append((i, team))

    # Find and resolve duplicates
    indices_to_remove = []
    for key, team_list in variation_groups.items():
        # Get unique team names
        unique_names = set(t[1]['team_name'] for t in team_list)

        if len(unique_names) > 1:  # Multiple different names map to same variation
            # Score each team to find the best one
            def score_team(idx_team):
                idx, team = idx_team
                rank = team.get('rank')
                wins = team.get('wins')
                has_record = wins is not None

                # Score: ranked (1000+), has_record (100+), wins count, negative index
                score = 0
                if rank is not None:
                    score += 1000 - rank  # Lower rank number = higher score
                if has_record:
                    score += 100 + wins
                score -= idx * 0.01  # Slight preference for earlier entries
                return score

            team_list_sorted = sorted(team_list, key=score_team, reverse=True)
            best_idx, best_team = team_list_sorted[0]

            print(f"UIL {class_name} - Keeping: {best_team['team_name']}")

            # Mark others for removal
            for idx, team in team_list_sorted[1:]:
                print(f"  Removing duplicate: {team['team_name']}")
                indices_to_remove.append(idx)
                duplicates_removed += 1

    # Remove duplicates (in reverse order to preserve indices)
    for idx in sorted(indices_to_remove, reverse=True):
        del data['uil'][class_code][idx]

    # Re-rank remaining teams 1-25
    if indices_to_remove:
        ranked_teams = [t for t in data['uil'][class_code] if t.get('rank')]
        ranked_teams.sort(key=lambda x: x['rank'])
        for i, team in enumerate(ranked_teams[:25], start=1):
            team['rank'] = i

# Process TAPPS
tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
tapps_display = ['TAPPS 6A', 'TAPPS 5A', 'TAPPS 4A', 'TAPPS 3A', 'TAPPS 2A', 'TAPPS 1A']
for class_code, class_display in zip(tapps_classes, tapps_display):
    if class_code not in data['private']:
        continue

    teams = data['private'][class_code]

    # Build variation groups
    variation_groups = defaultdict(list)
    for i, team in enumerate(teams):
        name = team['team_name']
        variations = get_search_variations(name)
        # Use shortest variation as group key
        key = min(variations, key=len).lower()
        variation_groups[key].append((i, team))

    # Find and resolve duplicates
    indices_to_remove = []
    for key, team_list in variation_groups.items():
        # Get unique team names
        unique_names = set(t[1]['team_name'] for t in team_list)

        if len(unique_names) > 1:
            # Score each team
            def score_team(idx_team):
                idx, team = idx_team
                rank = team.get('rank')
                wins = team.get('wins')
                has_record = wins is not None

                score = 0
                if rank is not None:
                    score += 1000 - rank
                if has_record:
                    score += 100 + wins
                score -= idx * 0.01
                return score

            team_list_sorted = sorted(team_list, key=score_team, reverse=True)
            best_idx, best_team = team_list_sorted[0]

            print(f"{class_display} - Keeping: {best_team['team_name']}")

            # Mark others for removal
            for idx, team in team_list_sorted[1:]:
                print(f"  Removing duplicate: {team['team_name']}")
                indices_to_remove.append(idx)
                duplicates_removed += 1

    # Remove duplicates
    for idx in sorted(indices_to_remove, reverse=True):
        del data['private'][class_code][idx]

    # Re-rank remaining teams 1-10
    if indices_to_remove:
        ranked_teams = [t for t in data['private'][class_code] if t.get('rank')]
        ranked_teams.sort(key=lambda x: x['rank'])
        for i, team in enumerate(ranked_teams[:10], start=1):
            team['rank'] = i

# Save cleaned rankings
with open('data/rankings.json', 'w') as f:
    json.dump(data, f, indent=2)

print()
print("=" * 100)
print(f"✓ Removed {duplicates_removed} duplicate teams")
print("✓ Rankings saved to data/rankings.json")
print("=" * 100)
