"""
Check for team name inconsistencies between rankings and database
"""

from app import app, db
from models import BoxScore
from sqlalchemy import or_
import json
from pathlib import Path

# Load rankings to get expected team names
data_file = Path('data/rankings.json')
with open(data_file, 'r') as f:
    rankings = json.load(f)

# Get all ranked team names
ranked_teams = set()
for association in ['uil', 'private']:
    if association in rankings:
        for classification in rankings[association]:
            for team in rankings[association][classification]:
                ranked_teams.add(team['team_name'])

print(f'Found {len(ranked_teams)} ranked teams\n')

with app.app_context():
    # Get all unique team names from database
    team1_names = db.session.query(BoxScore.team1_name).distinct().all()
    team2_names = db.session.query(BoxScore.team2_name).distinct().all()

    all_db_teams = set()
    for (name,) in team1_names:
        all_db_teams.add(name)
    for (name,) in team2_names:
        all_db_teams.add(name)

    print(f'Found {len(all_db_teams)} unique team names in database\n')

    # Find potential mismatches - teams with similar names
    issues = []

    for ranked_team in ranked_teams:
        # Look for variations without city prefix
        base_name = ranked_team.split()[-1] if ' ' in ranked_team else ranked_team

        # Find similar teams in database
        similar = [t for t in all_db_teams if base_name in t and t != ranked_team]

        if similar:
            # Count games for each variation
            ranked_count = BoxScore.query.filter(
                or_(BoxScore.team1_name == ranked_team, BoxScore.team2_name == ranked_team)
            ).count()

            for similar_name in similar:
                similar_count = BoxScore.query.filter(
                    or_(BoxScore.team1_name == similar_name, BoxScore.team2_name == similar_name)
                ).count()

                if similar_count > 0:
                    issues.append({
                        'ranked_name': ranked_team,
                        'ranked_games': ranked_count,
                        'db_name': similar_name,
                        'db_games': similar_count
                    })

    # Sort by number of games affected
    issues.sort(key=lambda x: x['db_games'], reverse=True)

    print('🔍 Teams with potential name mismatches:')
    print('=' * 80)

    if not issues:
        print('✓ No name mismatches found!')
    else:
        for issue in issues[:30]:  # Show top 30
            print(f"Ranked: '{issue['ranked_name']}' ({issue['ranked_games']} games)")
            print(f"  DB:   '{issue['db_name']}' ({issue['db_games']} games)")
            print()

        if len(issues) > 30:
            print(f'... and {len(issues) - 30} more issues')

if __name__ == "__main__":
    pass
