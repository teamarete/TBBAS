"""
Add additional November 25-29, 2025 games from multiple classifications
"""

from app import app, db
from models import BoxScore
from datetime import datetime

# Additional games collected via WebFetch
GAMES = [
    # 5A teams
    ('2025-11-28', 'AAAAA', 'Dallas Kimball', 55, 'Cardinal Ritter College Prep', 48),
    ('2025-11-29', 'AAAAA', 'West Brook', 78, 'Dallas Kimball', 67),
    ('2025-11-25', 'AAAAA', 'Cedar Park', 53, 'Anderson', 46),
    ('2025-11-29', 'AAAAA', 'Cedar Ridge', 53, 'Cedar Park', 48),
    ('2025-11-25', 'AAAAA', 'Antonian Prep', 96, 'Liberty Hill', 61),

    # 4A teams
    ('2025-11-25', 'AAAA', 'Argyle', 56, 'Pinkston', 42),
    ('2025-11-29', 'AAAA', 'Douglass', 47, 'Argyle', 44),
    ('2025-11-25', 'AAAA', 'Lubbock Monterey', 77, 'Wylie', 72),
    ('2025-11-25', 'AAAA', 'Fort Worth Brewer', 52, 'Life Waxahachie', 40),
    ('2025-11-29', 'AAAA', 'Legacy', 50, 'Fort Worth Brewer', 47),

    # 3A teams
    ('2025-11-26', 'AAA', 'Yates', 97, 'St. John\'s', 54),
    ('2025-11-28', 'AAA', 'Yates', 127, 'Sam Houston', 45),
    ('2025-11-29', 'AAA', 'Yates', 80, 'Unknown Opponent', 57),
]

def add_games():
    """Add games to database"""
    print("="*80)
    print("ADDING MORE NOVEMBER 25-29, 2025 GAMES (Multiple Classifications)")
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
    print("Next: Commit and push before 1 PM CST")

if __name__ == '__main__':
    add_games()
