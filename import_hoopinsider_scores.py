#!/usr/bin/env python3
"""
Import HoopInsider scores to TBBAS database

Usage:
1. Copy/paste game scores from HoopInsider into the GAMES list below
2. Run: python import_hoopinsider_scores.py
3. Games will be imported and rankings updated automatically
"""

from app import app, db
from models import BoxScore
from datetime import datetime, date
from update_rankings_with_records import update_rankings_with_records
import re

# =============================================================================
# PASTE HOOPINSIDER SCORES HERE
# =============================================================================
# Format: "Team1 Score - Team2 Score" or "Team1 Score, Team2 Score"
# One game per line, can include classification info
# Example: "Duncanville 75 - DeSoto 68 (6A)"
# Example: "Humble Atascocita 82, North Shore 76"

GAMES_TEXT = """
Duncanville 53, Red Oak 47 (6A)
North Crowley 96, Kingdom Collegiate 67 (6A)
Seven Lakes 73, College Park 57 (6A)
Atascocita 74, Shadow Creek 30 (6A)
Lancaster 74, Kimball 69 (6A)
Allen 84, Highland Park 65 (6A)
Jordan 73, Bush 60 (6A)
Steele 58, Brandeis 55 (6A)
Westlake 80, SA Johnson 45 (6A)
DeSoto 76, Little Elm 71 (6A)
Grand Oaks 90, Klein Collins 50 (6A)
Cy Falls 80, Hou Davis 21 (6A)
Friendswood 44, Pearland 41 (5A)
Lake Travis 53, Cedar Ridge 51 (6A)
Trinity Christian 66, Permian 48 (6A)
Horn 73, Seagoville 51 (6A)
Frisco Memorial 68, Plano 67 (5A)
Grand Prairie 52, Midlothian 51 (6A)
Arl Martin 59, Eastern Hills 45 (6A)
Lake Ridge 68, Keller Central 41 (6A)
Bmt United 77, La Porte 61 (5A)
Birdville 58, Byron Nelson 49 (5A)
CC Veterans Memorial 66, Nixon 65 (5A)
Timberview 55, Richardson 46 (5A)
FB Marshall 64, Hightower 51 (5A)
Summit 55, Lake Highlands 46 (5A)
Lufkin 60, Tyler Legacy 46 (5A)
Amarillo 63, Canyon 48 (5A)
Frisco Heritage 82, Melissa 47 (5A)
Alamo Heights 79, Holmes 46 (5A)
Iowa Colony 64, Deer Park 54 (5A)
Ryan 64, Lewisville 57 (5A)
Taft 73, Jay 57 (5A)
Vandegrift 58, Glenn 48 (5A)
Carter 69, South Oak Cliff 49 (4A)
Estacado 70, Brownfield 44 (4A)
LaMarque 70, Harmony Sugarland 27 (4A)
Kennedale 77, Crowley 76 (4A)
Panther Creek 77, Wakeland 56 (4A)
Krum 73, Celina 63 (4A)
Wimberley 74, St Andrews 28 (4A)
Paris 66, Mt Pleasant 58 (4A)
Monterey 82, Randall 42 (4A)
Southwest 54, Brock 47 (4A)
Austin LBJ 86, Cedar Creek 62 (4A)
Burkburnett 99, OKC Storm 83 (4A)
Chapel Hill 85, Jacksonville 74 (4A)
FB Crawford 62, Alief Hastings 43 (4A)
St Marks 61, Dallas Roosevelt 43 (4A)
West Plains 84, Lubbock Coronado 29 (4A)
Bridge City 58, Huffman 51 (4A)
Davenport 70, NBCA 48 (4A)
Paradise 44, Henrietta 39 (3A)
Cole 83, Crystal City 39 (3A)
Slaton 76, Plains 72 (3A)
Onalaska 80, Mexia 65 (3A)
Eagle Mountain 46, Ponder 37 (3A)
Gregory Portland 59, Aransas Pass 52 (3A)
Nederland 62, Orangefield 56 (3A)
Martins Mill 40, Gary 32 (2A)
Lipan 82, Peaster 42 (2A)
Rockdale 56, Hearne 50 (2A)
Graford 78, Slidell 59 (2A)
Port Aransas 46, Alice 38 (2A)
New Home 78, Idalou 38 (2A)
Mumford 75, Caldwell 35 (2A)
Olton 77, Frenship Memorial 58 (2A)
Troup 63, Frankston 30 (2A)
Hawkins 64, Alto 28 (2A)
Poolville 68, Chico 41 (2A)
Central Heights 63, Brookeland 56 (1A)
Huckabay 57, Jim Ned 39 (1A)
Perrin Whitt 57, Clyde 53 (1A)
Fayetteville 62, Wharton 57 (1A)
Central 65, Wells 53 (1A)
Grand Saline 51, Groveton Centerville 41 (1A)
Slocum 62, Latexo 53 (1A)
Abilene 83, Munday 49 (1A)
McLean 60, Silverton 25 (1A)
McLeod 58, Avery 56 (1A)
"""

# Game date from the article (change if different)
GAME_DATE = "2025-11-18"  # Ranked teams games from Nov 17-22 schedule

# =============================================================================
# PROCESSING CODE (Don't modify below this line)
# =============================================================================

def parse_classification_from_text(text):
    """Extract classification from text like (6A) or [5A]"""
    patterns = [
        r'\(?6A\)?',
        r'\(?5A\)?',
        r'\(?4A\)?',
        r'\(?3A\)?',
        r'\(?2A\)?',
        r'\(?1A\)?',
        r'TAPPS\s*6A',
        r'TAPPS\s*5A',
        r'TAPPS\s*4A',
        r'TAPPS\s*3A',
        r'TAPPS\s*2A',
        r'TAPPS\s*1A',
    ]

    class_map = {
        '6A': 'AAAAAA',
        '5A': 'AAAAA',
        '4A': 'AAAA',
        '3A': 'AAA',
        '2A': 'AA',
        '1A': 'A',
        'TAPPS 6A': 'TAPPS_6A',
        'TAPPS 5A': 'TAPPS_5A',
        'TAPPS 4A': 'TAPPS_4A',
        'TAPPS 3A': 'TAPPS_3A',
        'TAPPS 2A': 'TAPPS_2A',
        'TAPPS 1A': 'TAPPS_1A',
    }

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            class_text = match.group(0).strip('()[]').strip()
            return class_map.get(class_text, '')

    return ''


def parse_game_line(line):
    """
    Parse a line like:
    "Duncanville 75 - DeSoto 68"
    "Humble Atascocita 82, North Shore 76 (6A)"
    "Fort Bend Marshall 65 vs Manvel 62"
    """
    line = line.strip()

    # Skip empty lines and comments
    if not line or line.startswith('#'):
        return None

    # Extract classification if present
    classification = parse_classification_from_text(line)

    # Remove classification from line for parsing
    line = re.sub(r'\([^)]*\)', '', line)
    line = re.sub(r'\[[^\]]*\]', '', line)

    # Try different separators: vs, -, ,
    separators = [' vs ', ' - ', ', ']

    for sep in separators:
        if sep in line:
            parts = line.split(sep)
            if len(parts) != 2:
                continue

            # Parse each side (Team Score)
            team1_match = re.match(r'(.+?)\s+(\d+)\s*$', parts[0].strip())
            team2_match = re.match(r'(.+?)\s+(\d+)\s*$', parts[1].strip())

            if team1_match and team2_match:
                return {
                    'team1_name': team1_match.group(1).strip(),
                    'team1_score': int(team1_match.group(2)),
                    'team2_name': team2_match.group(1).strip(),
                    'team2_score': int(team2_match.group(2)),
                    'classification': classification
                }

    return None


def import_games():
    """Import games from GAMES_TEXT"""

    print("=" * 80)
    print("HOOPINSIDER SCORE IMPORT")
    print("=" * 80)

    # Parse game date
    try:
        game_date = datetime.strptime(GAME_DATE, '%Y-%m-%d').date()
        print(f"\nGame Date: {game_date.strftime('%B %d, %Y')}")
    except Exception as e:
        print(f"Error: Invalid date format. Use YYYY-MM-DD")
        return

    # Parse games
    lines = GAMES_TEXT.strip().split('\n')
    parsed_games = []

    print(f"\nParsing {len(lines)} lines...")

    for i, line in enumerate(lines, 1):
        game = parse_game_line(line)
        if game:
            parsed_games.append(game)
            print(f"  ✓ Game {len(parsed_games)}: {game['team1_name']} {game['team1_score']} - {game['team2_name']} {game['team2_score']}")
        elif line.strip() and not line.strip().startswith('#'):
            print(f"  ⚠️  Line {i}: Could not parse: {line[:60]}")

    if not parsed_games:
        print("\n❌ No games parsed. Please check the format in GAMES_TEXT.")
        print("\nExpected format:")
        print("  Team1 Name Score - Team2 Name Score")
        print("  Example: Duncanville 75 - DeSoto 68")
        return

    print(f"\n✅ Parsed {len(parsed_games)} games")

    # Import to database
    with app.app_context():
        imported = 0
        skipped = 0

        print("\nImporting to database...")

        for game in parsed_games:
            # Check if game already exists
            existing = BoxScore.query.filter_by(
                game_date=game_date,
                team1_name=game['team1_name'],
                team2_name=game['team2_name']
            ).first()

            if existing:
                print(f"  ⏭️  Skipped (duplicate): {game['team1_name']} vs {game['team2_name']}")
                skipped += 1
                continue

            # Create new game
            box_score = BoxScore(
                game_date=game_date,
                classification=game['classification'],
                team1_name=game['team1_name'],
                team1_score=game['team1_score'],
                team2_name=game['team2_name'],
                team2_score=game['team2_score'],
                submitted_by='HoopInsider Import'
            )

            db.session.add(box_score)
            imported += 1

        # Commit all games
        db.session.commit()

        print(f"\n✅ Import complete:")
        print(f"   Imported: {imported}")
        print(f"   Skipped (duplicates): {skipped}")
        print(f"   Total games in database: {BoxScore.query.count()}")

        # Update rankings
        if imported > 0:
            print("\n🔄 Updating rankings with new games...")
            result = update_rankings_with_records()
            print(f"✅ Rankings updated!")
            print(f"   Teams with records: {result.get('games_analyzed', 0)}")
            print(f"   Last updated: {result.get('last_updated', 'unknown')}")

    print("\n" + "=" * 80)
    print("✅ IMPORT COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    import_games()
