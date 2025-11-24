"""
Remove duplicate teams from rankings, keeping the best version of each
"""

import json
from collections import defaultdict
from school_name_normalizer import SchoolNameNormalizer

# Load rankings
with open('data/rankings.json') as f:
    data = json.load(f)

normalizer = SchoolNameNormalizer()

print("Removing duplicates from rankings...")
print()

duplicates_removed = 0

# Process UIL
uil_classes = ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']
for class_code in uil_classes:
    if class_code in data['uil']:
        teams = data['uil'][class_code]

        # Group by normalized name
        name_groups = defaultdict(list)
        for i, team in enumerate(teams):
            normalized = normalizer.normalize(team['team_name']).lower()
            name_groups[normalized].append((i, team))

        # Find and resolve duplicates
        indices_to_remove = []
        for normalized, team_list in name_groups.items():
            if len(team_list) > 1:
                # Sort to pick best: ranked > unranked, with record > without, better record > worse
                def score_team(idx_team):
                    idx, team = idx_team
                    rank = team.get('rank')
                    wins = team.get('wins')
                    has_record = wins is not None

                    # Score: ranked (1000+), has_record (100+), wins count, negative index (prefer earlier)
                    score = 0
                    if rank is not None:
                        score += 1000 - rank  # Lower rank number = higher score
                    if has_record:
                        score += 100 + wins
                    score -= idx * 0.01  # Slight preference for earlier entries
                    return score

                team_list_sorted = sorted(team_list, key=score_team, reverse=True)
                best_idx, best_team = team_list_sorted[0]

                print(f"UIL {class_code} - Keeping: {best_team['team_name']}")

                # Mark others for removal
                for idx, team in team_list_sorted[1:]:
                    print(f"  Removing duplicate: {team['team_name']}")
                    indices_to_remove.append(idx)
                    duplicates_removed += 1

        # Remove duplicates (in reverse order to preserve indices)
        for idx in sorted(indices_to_remove, reverse=True):
            del data['uil'][class_code][idx]

# Process TAPPS
tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
for class_code in tapps_classes:
    if class_code in data['private']:
        teams = data['private'][class_code]

        # Group by normalized name
        name_groups = defaultdict(list)
        for i, team in enumerate(teams):
            normalized = normalizer.normalize(team['team_name']).lower()
            name_groups[normalized].append((i, team))

        # Find and resolve duplicates
        indices_to_remove = []
        for normalized, team_list in name_groups.items():
            if len(team_list) > 1:
                # Sort to pick best
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

                print(f"{class_code} - Keeping: {best_team['team_name']}")

                # Mark others for removal
                for idx, team in team_list_sorted[1:]:
                    print(f"  Removing duplicate: {team['team_name']}")
                    indices_to_remove.append(idx)
                    duplicates_removed += 1

        # Remove duplicates
        for idx in sorted(indices_to_remove, reverse=True):
            del data['private'][class_code][idx]

# Save cleaned rankings
with open('data/rankings.json', 'w') as f:
    json.dump(data, f, indent=2)

print()
print(f"✓ Removed {duplicates_removed} duplicate teams")
print("✓ Rankings saved to data/rankings.json")
