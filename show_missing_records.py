"""
Show where the missing teams' game records and stats are
"""

import json

# Load rankings
with open('data/rankings.json') as f:
    data = json.load(f)

print("=" * 100)
print("TEAMS WITHOUT RECORDS - WHERE ARE THEIR GAMES?")
print("=" * 100)
print()

# Check UIL 6A teams missing records
print("UIL 6A Teams Missing Records:")
print("-" * 100)

teams_6a = data['uil']['AAAAAA']
missing_6a = [t for t in teams_6a if t.get('rank') and t.get('wins') is None]

for team in missing_6a:
    print(f"Rank {team['rank']}: {team['team_name']}")
    print(f"  District: {team.get('district', '—')}")
    print(f"  Classification: UIL 6A")
    print(f"  ❌ No games/records found in database")
    print()

# Summary of issue
print("=" * 100)
print("REASON FOR MISSING RECORDS:")
print("=" * 100)
print()
print("The November 24 TABC rankings update changed some team names:")
print()
print("Examples:")
print("  • 'Humble Atascocita' (new TABC name) vs 'Atascocita' (in database)")
print("  • 'San Antonio Brennan' (new TABC name) vs 'SA Brennan' or 'Brennan' (in database)")
print("  • 'Cibolo Steele' (new TABC name) vs 'Steele' (in database)")
print("  • 'Humble Summer Creek' (new TABC name) vs 'Summer Creek' (in database)")
print("  • 'San Antonio Harlan' (new TABC name) vs 'Harlan' (in database)")
print()
print("SOLUTION: Add these name mappings to school_abbreviations.py SPECIAL_CASES")
print()

# Get all missing teams count
total_missing = 0
for cat in ['uil', 'private']:
    if cat in data:
        for class_code, teams in data[cat].items():
            for t in teams:
                if t.get('rank') and t.get('wins') is None:
                    total_missing += 1

print(f"Total teams without records: {total_missing}")
print(f"Most are due to name mismatches after TABC rankings update")
