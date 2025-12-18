"""
Daily MaxPreps Box Score Scraper
Scrapes box scores from MaxPreps for a given date and imports them into the database
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import sys

def scrape_maxpreps_scores(date_str):
    """
    Scrape MaxPreps scores for a specific date

    Args:
        date_str: Date in format MM/DD/YYYY (e.g., '12/15/2025')

    Returns:
        List of game dictionaries
    """
    # Format URL
    url = f"https://www.maxpreps.com/tx/basketball/scores/?date={date_str}"

    print(f"Scraping MaxPreps scores for {date_str}...")
    print(f"URL: {url}")

    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # TODO: Parse the HTML to extract box scores
        # This will need to be implemented based on MaxPreps HTML structure
        # For now, return empty list

        print(f"Successfully fetched page (size: {len(response.content)} bytes)")
        print("⚠️  HTML parsing not yet implemented - need to analyze MaxPreps page structure")

        return []

    except Exception as e:
        print(f"Error scraping MaxPreps: {e}")
        return []

def import_games_to_database(games):
    """Import scraped games into the database"""
    if not games:
        print("No games to import")
        return 0

    db_path = Path(__file__).parent / 'instance' / 'tbbas.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    imported = 0
    for game in games:
        try:
            cursor.execute('''
                INSERT INTO box_score (
                    game_date, classification,
                    team1_name, team1_score, team1_fg, team1_fga, team1_3pt, team1_3pta,
                    team1_ft, team1_fta, team1_reb, team1_ast, team1_stl, team1_blk, team1_to,
                    team2_name, team2_score, team2_fg, team2_fga, team2_3pt, team2_3pta,
                    team2_ft, team2_fta, team2_reb, team2_ast, team2_stl, team2_blk, team2_to,
                    submitted_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game['date'], game.get('classification', 'Unknown'),
                game['team1_name'], game['team1_score'],
                game.get('team1_fg'), game.get('team1_fga'),
                game.get('team1_3pt'), game.get('team1_3pta'),
                game.get('team1_ft'), game.get('team1_fta'),
                game.get('team1_reb'), game.get('team1_ast'),
                game.get('team1_stl'), game.get('team1_blk'), game.get('team1_to'),
                game['team2_name'], game['team2_score'],
                game.get('team2_fg'), game.get('team2_fga'),
                game.get('team2_3pt'), game.get('team2_3pta'),
                game.get('team2_ft'), game.get('team2_fta'),
                game.get('team2_reb'), game.get('team2_ast'),
                game.get('team2_stl'), game.get('team2_blk'), game.get('team2_to'),
                'MaxPreps Auto-Scraper'
            ))
            imported += 1
        except sqlite3.IntegrityError:
            # Game already exists
            pass
        except Exception as e:
            print(f"Error importing game: {e}")

    conn.commit()
    conn.close()

    return imported

def scrape_today():
    """Scrape scores for today's date"""
    today = datetime.now()
    date_str = today.strftime('%m/%d/%Y')

    games = scrape_maxpreps_scores(date_str)
    imported = import_games_to_database(games)

    print(f"\n✓ Scraped {len(games)} games, imported {imported} new games to database")
    return imported

def scrape_date_range(start_date, end_date):
    """Scrape scores for a date range"""
    current = start_date
    total_games = 0
    total_imported = 0

    while current <= end_date:
        date_str = current.strftime('%m/%d/%Y')
        games = scrape_maxpreps_scores(date_str)
        imported = import_games_to_database(games)

        total_games += len(games)
        total_imported += imported

        current += timedelta(days=1)

    print(f"\n✓ Total: {total_games} games scraped, {total_imported} imported")
    return total_imported

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Scrape specific date
        date_str = sys.argv[1]
        games = scrape_maxpreps_scores(date_str)
        imported = import_games_to_database(games)
        print(f"\n✓ {len(games)} games scraped, {imported} imported")
    else:
        # Scrape today by default
        scrape_today()
