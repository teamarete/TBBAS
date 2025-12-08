"""
Add November 25-29, 2025 games manually collected from MaxPreps
"""

from app import app, db
from models import BoxScore
from datetime import datetime

# Games collected via WebFetch from MaxPreps
GAMES = [
    # Duncanville (6A) - confirmed from earlier WebFetch
    ('2025-11-25', 'AAAAAA', 'Duncanville', 65, 'Wagner', 54),
    ('2025-11-29', 'AAAAAA', 'Duncanville', 61, 'NSU University High School', 58),

    # San Antonio Brennan (6A)
    ('2025-11-28', 'AAAAAA', 'Booker T. Washington', 70, 'San Antonio Brennan', 62),

    # Katy Seven Lakes (6A)
    ('2025-11-25', 'AAAAAA', 'Katy Seven Lakes', 60, 'Red Mountain', 54),
    ('2025-11-26', 'AAAAAA', 'Katy Seven Lakes', 67, 'Chandler', 47),
    ('2025-11-28', 'AAAAAA', 'Katy Seven Lakes', 84, 'Highland', 80),
    ('2025-11-29', 'AAAAAA', 'Katy Seven Lakes', 94, 'Willow Canyon', 68),

    # Austin Westlake (6A)
    ('2025-11-25', 'AAAAAA', 'Alamo Heights', 59, 'Austin Westlake', 55),
    ('2025-11-28', 'AAAAAA', 'Austin Westlake', 61, 'Calvary Baptist Academy', 50),
    ('2025-11-29', 'AAAAAA', 'East St. Louis', 56, 'Austin Westlake', 53),

    # Plano (6A)
    ('2025-11-25', 'AAAAAA', 'Plano', 41, 'Rockwall', 30),
]

def add_games():
    """Add games to database"""
    print("="*80)
    print("ADDING NOVEMBER 25-29, 2025 GAMES")
    print("="*80)
    print()

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
                    submitted_by='manual_webfetch'
                )
                db.session.add(game)
                added += 1
                print(f"✓ {date_str}: {team1} {score1} - {team2} {score2}")
            else:
                skipped += 1
                print(f"○ Already exists: {date_str}: {team1} vs {team2}")

        db.session.commit()
        print()
        print(f"✓ Added {added} games")
        print(f"○ Skipped {skipped} duplicates")

        # Show total
        total = BoxScore.query.count()
        print(f"\nTotal games in database: {total}")

    # Update rankings
    print("\nUpdating rankings with new games...")
    from update_rankings_with_records import update_rankings_with_records
    update_rankings_with_records()
    print("✓ Rankings updated!")
    print()
    print("Next: Commit and push to deploy before 1 PM CST ranking update")

if __name__ == '__main__':
    add_games()
