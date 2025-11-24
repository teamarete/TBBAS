"""
Clean rankings to only keep top 25 (UIL) or top 10 (TAPPS) per classification
"""

import json

# Load rankings
with open('data/rankings.json') as f:
    data = json.load(f)

print("Cleaning rankings to keep only top 25 UIL / top 10 TAPPS per classification...")
print()

total_removed = 0

# Process UIL - keep only top 25 ranked teams per class
uil_classes = ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']
for class_code in uil_classes:
    if class_code in data['uil']:
        teams = data['uil'][class_code]
        original_count = len(teams)

        # Keep only teams with rank 1-25
        teams_to_keep = [t for t in teams if t.get('rank') and 1 <= t.get('rank') <= 25]

        # Sort by rank
        teams_to_keep.sort(key=lambda x: x.get('rank', 999))

        removed_count = original_count - len(teams_to_keep)
        if removed_count > 0:
            print(f"UIL {class_code}: {original_count} -> {len(teams_to_keep)} teams (removed {removed_count})")
            total_removed += removed_count

        data['uil'][class_code] = teams_to_keep

# Process TAPPS - keep only top 10 ranked teams per class
tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
for class_code in tapps_classes:
    if class_code in data['private']:
        teams = data['private'][class_code]
        original_count = len(teams)

        # Keep only teams with rank 1-10
        teams_to_keep = [t for t in teams if t.get('rank') and 1 <= t.get('rank') <= 10]

        # Sort by rank
        teams_to_keep.sort(key=lambda x: x.get('rank', 999))

        removed_count = original_count - len(teams_to_keep)
        if removed_count > 0:
            print(f"{class_code}: {original_count} -> {len(teams_to_keep)} teams (removed {removed_count})")
            total_removed += removed_count

        data['private'][class_code] = teams_to_keep

# Save cleaned rankings
with open('data/rankings.json', 'w') as f:
    json.dump(data, f, indent=2)

print()
print(f"✓ Removed {total_removed} teams outside top 25/10")
print("✓ Rankings saved to data/rankings.json")
