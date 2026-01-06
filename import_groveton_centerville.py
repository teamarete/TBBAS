"""
Import Groveton Centerville games from MaxPreps
18 games, 12-6 record for 2025-26 season
"""

from models import db, BoxScore
from app import app
from datetime import datetime

def import_groveton_centerville_games():
    """Import all Groveton Centerville games"""

    games = [
        # Date, Opponent, Centerville Score, Opponent Score, Result
        ('2024-11-14', 'Latexo', 65, 49, 'W'),
        ('2024-11-18', 'Grand Saline', 41, 51, 'L'),
        ('2024-11-20', 'Tarkington', 53, 61, 'L'),
        ('2024-11-20', 'Robinson', 60, 68, 'L'),
        ('2024-11-21', 'Normangee', 45, 35, 'W'),
        ('2024-11-22', 'Alto', 50, 31, 'W'),
        ('2024-11-24', 'Neches', 73, 49, 'W'),
        ('2024-12-02', 'Slocum', 66, 68, 'L'),
        ('2024-12-04', 'Hull-Daisetta', 74, 48, 'W'),
        ('2024-12-05', 'Groveton', 58, 32, 'W'),
        ('2024-12-05', 'Warren', 55, 52, 'W'),
        ('2024-12-06', 'Big Sandy', 39, 46, 'L'),
        ('2024-12-09', 'Big Sandy', 46, 39, 'W'),
        ('2024-12-12', 'Leggett', 78, 31, 'W'),
        ('2024-12-16', 'Richards', 76, 86, 'L'),
        ('2024-12-18', 'Leggett', 79, 32, 'W'),
        ('2024-12-30', 'Spurger', 79, 57, 'W'),
        ('2025-01-02', 'Laneville', 59, 33, 'W'),
    ]

    imported = 0
    updated = 0

    with app.app_context():
        for date_str, opponent, cent_score, opp_score, result in games:
            game_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Check if game already exists (check both as team1 and team2)
            existing = BoxScore.query.filter(
                db.or_(
                    db.and_(
                        BoxScore.team1_name == 'Groveton Centerville',
                        BoxScore.team2_name == opponent,
                        BoxScore.game_date == game_date
                    ),
                    db.and_(
                        BoxScore.team2_name == 'Groveton Centerville',
                        BoxScore.team1_name == opponent,
                        BoxScore.game_date == game_date
                    )
                )
            ).first()

            if existing:
                # Update existing game
                if existing.team1_name == 'Groveton Centerville':
                    existing.team1_score = cent_score
                    existing.team2_score = opp_score
                else:
                    existing.team2_score = cent_score
                    existing.team1_score = opp_score
                updated += 1
                print(f"  Updated: {date_str} vs {opponent} ({cent_score}-{opp_score})")
            else:
                # Create new game (Groveton Centerville as team1)
                box_score = BoxScore(
                    team1_name='Groveton Centerville',
                    team2_name=opponent,
                    game_date=game_date,
                    team1_score=cent_score,
                    team2_score=opp_score,
                    classification='A',  # UIL 1A
                    submitted_by='MaxPreps Import'
                )
                db.session.add(box_score)
                imported += 1
                print(f"  Imported: {date_str} vs {opponent} ({cent_score}-{opp_score})")

        db.session.commit()

    print(f"\n✓ Groveton Centerville: {imported} games imported, {updated} games updated")
    return imported, updated

if __name__ == '__main__':
    print("Importing Groveton Centerville Games")
    print("=" * 80)
    imported, updated = import_groveton_centerville_games()
    print(f"\nTotal: {imported + updated} games processed")
