"""
Bulk addition of November 25-29, 2025 games - comprehensive update
Collected via systematic WebFetch of all ranked teams
"""

from app import app, db
from models import BoxScore
from datetime import datetime

# All games collected from ranked teams
GAMES = [
    # 6A teams
    ('2025-11-26', 'AAAAAA', 'Desoto', 94, 'Unknown Opponent', 84),
    ('2025-11-29', 'AAAAAA', 'Putnam City', 74, 'Desoto', 70),
    ('2025-11-25', 'AAAAAA', 'San Antonio Harlan', 79, 'Corpus Christi Veterans Memorial', 60),
    ('2025-11-28', 'AAAAAA', 'Beaumont United', 65, 'San Antonio Harlan', 58),
    ('2025-11-29', 'AAAAAA', 'San Antonio Harlan', 56, 'Cypress Park', 47),
    ('2025-11-26', 'AAAAAA', 'Grand Prairie', 78, 'Wylie East', 44),
    ('2025-11-28', 'AAAAAA', 'Grand Prairie', 56, 'Madison Prep Academy', 42),

    # 5A teams
    ('2025-11-25', 'AAAAA', 'Duncanville', 65, 'SA Wagner', 54),  # Already have Duncanville side
    ('2025-11-26', 'AAAAA', 'Humble', 61, 'SA Wagner', 48),
    ('2025-11-29', 'AAAAA', 'Heights', 60, 'SA Wagner', 56),
    ('2025-11-25', 'AAAAA', 'Temple', 62, 'Ellison', 54),
    ('2025-11-28', 'AAAAA', 'Shadow Creek', 57, 'Ellison', 53),
    ('2025-11-29', 'AAAAA', 'Ellison', 66, 'Fort Bend Bush', 53),
    ('2025-11-25', 'AAAAA', 'Lufkin', 61, 'Keller', 34),
    ('2025-11-29', 'AAAAA', 'Owasso', 81, 'Lufkin', 63),
    ('2025-11-25', 'AAAAA', 'Palo Duro', 78, 'Seagoville', 66),
    ('2025-11-25', 'AAAAA', 'Amarillo', 58, 'Palo Duro', 50),
    ('2025-11-26', 'AAAAA', 'Trinity Christian', 73, 'Palo Duro', 62),

    # 4A teams
    ('2025-11-28', 'AAAA', 'Hou Wheatley', 61, 'Village', 45),
]

def add_games():
    """Add games to database"""
    print("="*80)
    print("BULK UPDATE: November 25-29, 2025 - All Ranked Teams")
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
                    submitted_by='manual_webfetch_bulk'
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
        print(f"Games added today (Nov 25-29): {32 + added}")

    # Update rankings
    print("\nUpdating all team records...")
    from update_rankings_with_records import update_rankings_with_records
    update_rankings_with_records()
    print("✓ All rankings updated!")
    print()
    print("=" * 80)
    print("DATABASE FULLY UPDATED - READY FOR 1 PM RANKING RECALCULATION")
    print("=" * 80)

if __name__ == '__main__':
    add_games()
