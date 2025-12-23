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

def get_selenium_driver():
    """Initialize Selenium WebDriver (headless)"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    except Exception as e:
        print(f"Error initializing Selenium: {e}")
        print("Note: Selenium and ChromeDriver are required for MaxPreps scraping")
        print("Install with: pip install selenium webdriver-manager")
        return None

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

    games = []
    driver = None

    try:
        # MaxPreps loads games via JavaScript, so we need Selenium
        driver = get_selenium_driver()

        if driver is None:
            print("ERROR: Could not initialize Selenium driver - MaxPreps requires JavaScript")
            return games

        # Load the page and wait for JavaScript to render
        driver.get(url)

        # Wait for game elements to load (up to 10 seconds)
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        try:
            # Wait for contest boxes to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "contest-box-item"))
            )
        except:
            print(f"No games found or timeout waiting for games on {date_str}")
            return games

        # Parse the rendered page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all game containers using the actual MaxPreps structure
        game_containers = soup.find_all('div', class_='contest-box-item')

        print(f"Found {len(game_containers)} game containers")

        for container in game_containers:
            try:
                # Check if game has a score (completed games)
                state = container.get('data-contest-state', '')
                if state != 'boxscore':
                    continue  # Skip games that haven't been completed yet

                # Find team list items
                team_items = container.find('ul', class_='teams')
                if not team_items:
                    continue

                teams = team_items.find_all('li')
                if len(teams) < 2:
                    continue

                # Extract team names from <div class="name">
                team1_name_elem = teams[0].find('div', class_='name')
                team2_name_elem = teams[1].find('div', class_='name')

                if not team1_name_elem or not team2_name_elem:
                    continue

                team1_name = team1_name_elem.get_text(strip=True)
                team2_name = team2_name_elem.get_text(strip=True)

                # Find scores - they're in <div class="score">
                team1_score_elem = teams[0].find('div', class_='score')
                team2_score_elem = teams[1].find('div', class_='score')

                if not team1_score_elem or not team2_score_elem:
                    continue

                team1_score_text = team1_score_elem.get_text(strip=True)
                team2_score_text = team2_score_elem.get_text(strip=True)

                # Parse scores
                try:
                    team1_score = int(team1_score_text)
                    team2_score = int(team2_score_text)
                except ValueError:
                    print(f"  Could not parse scores: {team1_score_text}, {team2_score_text}")
                    continue

                game = {
                    'date': date_str,
                    'team1_name': team1_name,
                    'team1_score': team1_score,
                    'team2_name': team2_name,
                    'team2_score': team2_score,
                    'classification': 'Unknown'  # MaxPreps doesn't show classification on scores page
                }
                games.append(game)
                print(f"  {team1_name} {team1_score} vs {team2_name} {team2_score}")

            except Exception as e:
                print(f"  Error parsing game container: {e}")
                continue

        print(f"✓ Successfully scraped {len(games)} completed games from MaxPreps for {date_str}")

    except Exception as e:
        print(f"Error scraping MaxPreps: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()

    return games

def import_games_to_database(games):
    """Import scraped games into the database"""
    if not games:
        print("No games to import")
        return 0

    db_path = Path(__file__).parent / 'instance' / 'tbbas.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    imported = 0
    skipped = 0

    for game in games:
        try:
            # Convert date string to date object if needed
            game_date = game['date']
            if isinstance(game_date, str):
                # Parse MM/DD/YYYY format
                game_date = datetime.strptime(game_date, '%m/%d/%Y').date()

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
                game_date, game.get('classification', 'Unknown'),
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
            skipped += 1
        except Exception as e:
            print(f"Error importing game {game.get('team1_name')} vs {game.get('team2_name')}: {e}")

    conn.commit()
    conn.close()

    if skipped > 0:
        print(f"  Skipped {skipped} duplicate games")

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
