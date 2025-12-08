"""
Add TAPPS 6A game results manually from MaxPreps
"""

from app import app, db
from models import BoxScore
from datetime import datetime

# Game data from MaxPreps
GAMES = [
    # Dallas St. Mark's (5-0)
    ('2025-11-14', 'TAPPS_6A', "Dallas St. Mark's School of Texas", 80, 'Liberty Christian', 47),
    ('2025-11-18', 'TAPPS_6A', "Dallas St. Mark's School of Texas", 61, 'Roosevelt', 43),
    ('2025-11-21', 'TAPPS_6A', "Dallas St. Mark's School of Texas", 57, 'Austin Prep Academy', 56),
    ('2025-11-24', 'TAPPS_6A', "Dallas St. Mark's School of Texas", 54, 'Concordia Lutheran', 29),
    ('2025-11-24', 'TAPPS_6A', "Dallas St. Mark's School of Texas", 64, 'Village', 57),

    # San Antonio Central Catholic (9-0)
    ('2025-11-03', 'TAPPS_6A', 'San Antonio Central Catholic', 67, "Saint Mary's Hall", 47),
    ('2025-11-07', 'TAPPS_6A', 'San Antonio Central Catholic', 48, 'St. Thomas Catholic', 30),
    ('2025-11-08', 'TAPPS_6A', 'San Antonio Central Catholic', 56, 'New Braunfels Christian Academy', 29),
    ('2025-11-08', 'TAPPS_6A', 'San Antonio Central Catholic', 67, 'Plano John Paul II', 60),
    ('2025-11-18', 'TAPPS_6A', 'San Antonio Central Catholic', 79, 'Southwest', 50),
    ('2025-11-20', 'TAPPS_6A', 'San Antonio Central Catholic', 69, 'Sharyland', 42),
    ('2025-11-21', 'TAPPS_6A', 'San Antonio Central Catholic', 64, 'Boerne-Champion', 49),
    ('2025-11-22', 'TAPPS_6A', 'San Antonio Central Catholic', 62, 'Alamo Heights', 58),
    ('2025-11-24', 'TAPPS_6A', 'San Antonio Central Catholic', 50, 'Jefferson', 15),

    # San Antonio Antonian Prep (6-1)
    ('2025-11-07', 'TAPPS_6A', 'San Antonio Antonian Prep', 66, 'Fort Bend Christian Academy', 50),
    ('2025-11-07', 'TAPPS_6A', 'San Antonio Antonian Prep', 62, 'Faith Academy', 44),
    ('2025-11-08', 'TAPPS_6A', 'San Antonio Antonian Prep', 74, 'St. Pius X', 33),
    ('2025-11-15', 'TAPPS_6A', 'Allen', 73, 'San Antonio Antonian Prep', 71),
    ('2025-11-15', 'TAPPS_6A', 'San Antonio Antonian Prep', 65, 'Prestonwood Christian', 40),
    ('2025-11-17', 'TAPPS_6A', 'San Antonio Antonian Prep', 95, 'San Antonio Patriots HomeSchool', 44),
    ('2025-11-20', 'TAPPS_6A', 'San Antonio Antonian Prep', 93, 'New Braunfels Christian Academy', 33),

    # San Antonio TMI Episcopal (5-3)
    ('2025-11-04', 'TAPPS_6A', 'San Antonio TMI Episcopal', 84, 'San Antonio Christian', 15),
    ('2025-11-07', 'TAPPS_6A', 'San Antonio TMI Episcopal', 78, 'Kingdom Collegiate Academy', 52),
    ('2025-11-14', 'TAPPS_6A', 'Oak Cliff Faith Family Academy', 65, 'San Antonio TMI Episcopal', 59),
    ('2025-11-15', 'TAPPS_6A', 'Legion Preparatory Academy', 58, 'San Antonio TMI Episcopal', 53),
    ('2025-11-20', 'TAPPS_6A', 'San Antonio TMI Episcopal', 61, 'New Braunfels', 38),
    ('2025-11-21', 'TAPPS_6A', 'San Antonio TMI Episcopal', 56, 'Judson', 54),
    ('2025-11-21', 'TAPPS_6A', "Austin St. Michael's", 59, 'San Antonio TMI Episcopal', 54),
    ('2025-11-22', 'TAPPS_6A', 'San Antonio TMI Episcopal', 60, 'Cypress Falls', 57),
]

def add_games():
    """Add games to database"""
    print("="*80)
    print("ADDING TAPPS 6A GAMES")
    print("="*80)

    with app.app_context():
        added = 0
        skipped = 0

        for game_data in GAMES:
            date_str, classification, team1, score1, team2, score2 = game_data
            game_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Check if exists
            existing = BoxScore.query.filter_by(
                game_date=game_date,
                team1_name=team1,
                team2_name=team2
            ).first()

            if not existing:
                game = BoxScore(
                    game_date=game_date,
                    classification=classification,
                    team1_name=team1,
                    team1_score=score1,
                    team2_name=team2,
                    team2_score=score2,
                    submitted_by='maxpreps_manual'
                )
                db.session.add(game)
                added += 1
                print(f"✓ {date_str}: {team1} {score1} - {team2} {score2}")
            else:
                skipped += 1

        db.session.commit()
        print()
        print(f"✓ Added {added} games, skipped {skipped} duplicates")

    # Update rankings
    print("\nUpdating rankings with game records...")
    from update_rankings_with_records import update_rankings_with_records
    update_rankings_with_records()
    print("✓ Rankings updated!")

    # Show final records
    print("\n" + "="*80)
    print("TAPPS 6A RECORDS UPDATED")
    print("="*80)
    import json
    data = json.load(open('data/rankings.json'))
    for team in data['private']['TAPPS_6A'][:8]:
        rank = team.get('rank', '?')
        name = team['team_name']
        wins = team.get('wins')
        losses = team.get('losses')
        record = f'{wins}-{losses}' if wins is not None else 'no record'
        print(f"Rank {rank}: {name:<45} {record}")

if __name__ == '__main__':
    add_games()
