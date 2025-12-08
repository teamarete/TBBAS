"""
Manually add game results for missing teams
Based on MaxPreps data collected via web fetch
"""

from app import app, db
from models import BoxScore
from datetime import datetime

# Game data collected from MaxPreps
GAMES_TO_ADD = [
    # Denton Ryan (5A)
    ('2025-11-14', 'AAAAA', 'Denton Ryan', 58, 'Guyer', 37),
    ('2025-11-15', 'AAAAA', 'Denton Ryan', 67, 'White', 60),
    ('2025-11-18', 'AAAAA', 'Denton Ryan', 64, 'Lewisville', 57),
    ('2025-11-22', 'AAAAA', 'Grace Prep', 74, 'Denton Ryan', 57),
]

def add_games():
    """Add games to database"""
    print("="*80)
    print("ADDING MISSING TEAM GAMES MANUALLY")
    print("="*80)

    with app.app_context():
        added = 0

        for game_data in GAMES_TO_ADD:
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
                    submitted_by='manual_entry'
                )
                db.session.add(game)
                added += 1
                print(f"✓ {date_str}: {team1} {score1} - {team2} {score2}")
            else:
                print(f"○ Already exists: {date_str}: {team1} vs {team2}")

        db.session.commit()
        print(f"\n✓ Added {added} games")

    # Update rankings
    print("\nUpdating rankings...")
    from update_rankings_with_records import update_rankings_with_records
    update_rankings_with_records()
    print("✓ Rankings updated!")

if __name__ == '__main__':
    add_games()
