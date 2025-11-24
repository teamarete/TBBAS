"""Find database names for teams without records"""
import json
from app import app
import sqlite3

# Load rankings
with open('data/rankings.json') as f:
    data = json.load(f)

# Collect all teams without records
missing_teams = []

# UIL
uil_classes = [('AAAAAA', '6A'), ('AAAAA', '5A'), ('AAAA', '4A'), ('AAA', '3A'), ('AA', '2A'), ('A', '1A')]
for class_code, class_name in uil_classes:
    if class_code in data['uil']:
        teams = data['uil'][class_code]
        for t in teams:
            if t.get('rank') and t.get('wins') is None:
                missing_teams.append({
                    'type': 'UIL',
                    'classification': f'UIL {class_name}',
                    'rank': t.get('rank'),
                    'team': t.get('team_name')
                })

# TAPPS
tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
tapps_display = ['TAPPS 6A', 'TAPPS 5A', 'TAPPS 4A', 'TAPPS 3A', 'TAPPS 2A', 'TAPPS 1A']
for class_code, class_display in zip(tapps_classes, tapps_display):
    if class_code in data['private']:
        teams = data['private'][class_code]
        for t in teams:
            if t.get('rank') and t.get('wins') is None:
                missing_teams.append({
                    'type': 'TAPPS',
                    'classification': class_display,
                    'rank': t.get('rank'),
                    'team': t.get('team_name')
                })

print(f"Searching database for {len(missing_teams)} teams without records...")
print("=" * 100)

# Connect to database
with app.app_context():
    conn = sqlite3.connect('instance/tbbas.db')
    cursor = conn.cursor()

    found_mappings = []
    not_found = []

    for team_info in missing_teams:
        team_name = team_info['team']

        # Try searching for partial matches
        search_terms = []

        # Add the full name
        search_terms.append(team_name)

        # Try last word (school name)
        parts = team_name.split()
        if len(parts) > 1:
            search_terms.append(parts[-1])
            search_terms.append(' '.join(parts[-2:]))  # Last two words

        # Try without city prefix for common patterns
        for prefix in ['Dallas ', 'Houston ', 'San Antonio ', 'Fort Worth ', 'Austin ', 'Waco ', 'Denton ', 'Lubbock ']:
            if team_name.startswith(prefix):
                search_terms.append(team_name.replace(prefix, ''))

        found = False
        for term in search_terms:
            if len(term) < 4:  # Skip very short terms
                continue

            cursor.execute(f"""
                SELECT DISTINCT team1_name, COUNT(*) as count
                FROM box_score
                WHERE team1_name LIKE '%{term}%'
                GROUP BY team1_name
                UNION
                SELECT DISTINCT team2_name, COUNT(*) as count
                FROM box_score
                WHERE team2_name LIKE '%{term}%'
                GROUP BY team2_name
                ORDER BY count DESC
                LIMIT 3
            """)

            matches = cursor.fetchall()
            if matches:
                # Get total games for this team
                db_name = matches[0][0]
                cursor.execute(f"""
                    SELECT COUNT(*) FROM box_score
                    WHERE team1_name = ? OR team2_name = ?
                """, (db_name, db_name))
                game_count = cursor.fetchone()[0]

                if game_count > 0:
                    found_mappings.append({
                        'ranking_name': team_name,
                        'db_name': db_name,
                        'games': game_count,
                        'classification': team_info['classification'],
                        'rank': team_info['rank']
                    })
                    found = True
                    break

        if not found:
            not_found.append(team_info)

    conn.close()

# Print results
print(f"\n✓ FOUND IN DATABASE: {len(found_mappings)} teams")
print("=" * 100)
for mapping in found_mappings:
    print(f"{mapping['classification']:<12} Rank {mapping['rank']:>2}: {mapping['ranking_name']:<45} → {mapping['db_name']:<30} ({mapping['games']} games)")

print(f"\n✗ NOT FOUND IN DATABASE: {len(not_found)} teams")
print("=" * 100)
for team_info in not_found:
    print(f"{team_info['classification']:<12} Rank {team_info['rank']:>2}: {team_info['team']}")

# Generate special cases for school_abbreviations.py
if found_mappings:
    print("\n" + "=" * 100)
    print("ADD TO school_abbreviations.py SPECIAL_CASES:")
    print("=" * 100)
    for mapping in found_mappings:
        print(f"    '{mapping['ranking_name']}': '{mapping['db_name']}',  # {mapping['games']} games")
