#!/usr/bin/env python3
"""
Fix corrupted team names in rankings.json
- Remove duplicate city names ("Humble Humble" -> "Humble")
- Fix merged city names ("De Soto Duncanville" -> "Duncanville")
- Clean up overly long school names
"""

import json
import re
from datetime import datetime

def fix_team_name(name):
    """Fix common team name issues"""
    original = name

    # Fix duplicate words
    words = name.split()
    fixed_words = []
    prev_word = None
    for word in words:
        if word.lower() != (prev_word or '').lower():
            fixed_words.append(word)
        prev_word = word
    name = ' '.join(fixed_words)

    # Known fixes for specific teams
    fixes = {
        'De Soto Duncanville': 'Duncanville',
        'Humble Humble Atascocita': 'Humble Atascocita',
        'Lipan Poolville Santo': 'Lipan',
        'Poolville Santo': 'Poolville',
        # Add more as needed
    }

    for bad, good in fixes.items():
        if name == bad:
            name = good
            break

    if name != original:
        print(f"  Fixed: '{original}' -> '{name}'")

    return name

def fix_rankings():
    """Fix all team names in rankings.json"""

    print("=" * 80)
    print("FIXING TEAM NAMES IN RANKINGS.JSON")
    print("=" * 80)

    # Load rankings
    with open('data/rankings.json', 'r') as f:
        rankings = json.load(f)

    # Backup
    import shutil
    backup_file = f'data/rankings_backup_before_name_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    shutil.copy('data/rankings.json', backup_file)
    print(f"\n✅ Created backup: {backup_file}")

    # Fix team names
    print("\n🔧 Fixing team names...")
    fixed_count = 0

    for category in ['uil', 'private']:
        for classification, teams in rankings[category].items():
            for team in teams:
                old_name = team['team_name']
                new_name = fix_team_name(old_name)
                if old_name != new_name:
                    team['team_name'] = new_name
                    fixed_count += 1

    # Update timestamp
    rankings['last_updated'] = datetime.now().isoformat()
    rankings['name_fix_applied'] = True

    # Save
    with open('data/rankings.json', 'w') as f:
        json.dump(rankings, f, indent=2)

    print(f"\n✅ Fixed {fixed_count} team names")
    print(f"✅ Saved to data/rankings.json")

    # Now run the update to match records
    print("\n🔄 Running update_rankings_with_records to match games...")
    from update_rankings_with_records import update_rankings_with_records
    result = update_rankings_with_records()

    print("\n" + "=" * 80)
    print("✅ FIX COMPLETE")
    print("=" * 80)
    print(f"  Team names fixed: {fixed_count}")
    print(f"  Teams with records: {result.get('games_analyzed', 0)}")
    print(f"  Last updated: {result.get('last_updated', 'unknown')}")
    print("=" * 80)

if __name__ == '__main__':
    fix_rankings()
