"""
Add Groveton Centerville to MaxPreps UIL 1A rankings at position #22
This was verified from live MaxPreps but missing from our Jan 5 scrape
"""

import json
from pathlib import Path

def add_centerville_to_maxpreps():
    """Add Groveton Centerville to MaxPreps rankings"""

    weekly_file = Path('data/weekly_rankings_20260105.json')

    with open(weekly_file, 'r') as f:
        data = json.load(f)

    # Add to MaxPreps UIL 1A
    maxpreps_1a = data['maxpreps']['uil']['1A']

    # Check if already exists
    existing = [t for t in maxpreps_1a if 'Centerville' in t.get('team_name', '')]
    if existing:
        print("Groveton Centerville already in MaxPreps UIL 1A")
        return 0

    # Add Groveton Centerville at rank #22
    centerville_entry = {
        'rank': 22,
        'team_name': 'Groveton Centerville',
        'wins': 12,
        'losses': 6,
        'record': '12-6'
    }

    maxpreps_1a.append(centerville_entry)

    # Re-sort by rank to maintain order
    maxpreps_1a.sort(key=lambda x: x['rank'])

    # Save updated data
    with open(weekly_file, 'w') as f:
        json.dump(data, f, indent=2)

    print("MaxPreps UIL 1A Update:")
    print("=" * 80)
    print(f"  ✓ Added: #22 Groveton Centerville (12-6)")

    return 1

if __name__ == '__main__':
    count = add_centerville_to_maxpreps()
    print(f"\nTotal additions: {count}")
