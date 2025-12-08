"""
Final batch of November 25-29, 2025 games before 1 PM ranking update
"""

from app import app, db
from models import BoxScore
from datetime import datetime

# Final games collected via WebFetch
GAMES = [
    # 5A teams
    ('2025-11-29', 'AAAAA', 'Bishop O\'Connell', 77, 'Frisco Heritage', 70),
    ('2025-11-25', 'AAAAA', 'Beaumont West Brook', 67, 'Humble', 65),
    ('2025-11-29', 'AAAAA', 'Beaumont West Brook', 78, 'Dallas Kimball', 67),  # West Brook already in as opponent
    ('2025-11-25', 'AAAAA', 'Birdville', 59, 'Bell', 46),
    ('2025-11-28', 'AAAAA', 'The New School', 84, 'Birdville', 62),

    # 4A teams
    ('2025-11-25', 'AAAA', 'Dallas Carter', 69, 'South Oak Cliff', 49),
    ('2025-11-26', 'AAAA', 'Dallas Carter', 50, 'Mansfield Summit', 48),
    ('2025-11-29', 'AAAA', 'Waxahachie', 77, 'Dallas Carter', 76),
]

def add_games():
    """Add games to database"""
    print("="*80)
    print("FINAL BATCH: November 25-29, 2025 Games Before 1 PM Ranking Update")
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
    print("\nUpdating rankings with all games...")
    from update_rankings_with_records import update_rankings_with_records
    update_rankings_with_records()
    print("✓ Rankings updated!")
    print()
    print("=" * 80)
    print("READY FOR 1 PM CST RANKING UPDATE")
    print("=" * 80)

if __name__ == '__main__':
    add_games()
