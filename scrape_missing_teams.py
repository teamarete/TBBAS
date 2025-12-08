"""
Scrape missing teams' game results from MaxPreps
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
from app import app, db
from models import BoxScore

# Teams to scrape with their MaxPreps URLs and classifications
TEAMS_TO_SCRAPE = [
    # 5A
    ('Denton Ryan', 'AAAAA', 'https://www.maxpreps.com/tx/denton/ryan-raiders/basketball/'),

    # 3A
    ('Hitchcock', 'AAA', 'https://www.maxpreps.com/tx/hitchcock/hitchcock-bulldogs/basketball/'),
    ('Shallowater', 'AAA', 'https://www.maxpreps.com/tx/shallowater/shallowater-mustangs/basketball/'),
    ('Poth', 'AAA', 'https://www.maxpreps.com/tx/poth/poth-pirates/basketball/'),
    ('Wichita Falls City View', 'AAA', 'https://www.maxpreps.com/tx/wichita-falls/city-view-mustangs/basketball/'),
    ('Hooks', 'AAA', 'https://www.maxpreps.com/tx/hooks/hooks-hornets/basketball/'),

    # 2A
    ('Ropes', 'AA', 'https://www.maxpreps.com/tx/ropesville/ropes-eagles/basketball/'),
    ('Tom Bean', 'AA', 'https://www.maxpreps.com/tx/tom-bean/tom-bean-tomcats/basketball/'),
    ('Gruver', 'AA', 'https://www.maxpreps.com/tx/gruver/gruver-greyhounds/basketball/'),
    ('Goldthwaite', 'AA', 'https://www.maxpreps.com/tx/goldthwaite/goldthwaite-eagles/basketball/'),
    ('Lindsay', 'AA', 'https://www.maxpreps.com/tx/lindsay/lindsay-knights/basketball/'),
]

def setup_driver():
    """Setup Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def parse_date(date_str):
    """Parse MaxPreps date format to datetime"""
    try:
        # Format: "Nov 19" or "Nov 19, 2025"
        if ',' in date_str:
            return datetime.strptime(date_str, "%b %d, %Y").date()
        else:
            # Assume current season year
            return datetime.strptime(f"{date_str}, 2025", "%b %d, %Y").date()
    except:
        return None

def scrape_team_schedule(driver, team_name, classification, url):
    """Scrape a team's schedule from MaxPreps"""
    print(f"\nScraping {team_name} ({classification})...")

    try:
        driver.get(url)
        time.sleep(3)  # Wait for page load

        # Find schedule table
        games_added = 0

        # Look for completed games in the schedule
        game_rows = driver.find_elements(By.CSS_SELECTOR, 'tr.completed')

        for row in game_rows:
            try:
                # Get date
                date_elem = row.find_element(By.CSS_SELECTOR, 'td.date')
                date_str = date_elem.text.strip()
                game_date = parse_date(date_str)

                if not game_date:
                    continue

                # Get opponent
                opponent_elem = row.find_element(By.CSS_SELECTOR, 'td.opponent a')
                opponent_name = opponent_elem.text.strip()

                # Remove @ symbol if away game
                opponent_name = opponent_name.replace('@', '').strip()

                # Get result (W or L)
                result_elem = row.find_element(By.CSS_SELECTOR, 'td.result')
                result_text = result_elem.text.strip()

                if 'W' not in result_text and 'L' not in result_text:
                    continue

                is_win = 'W' in result_text

                # Get score
                score_elem = row.find_element(By.CSS_SELECTOR, 'td.result a')
                score_text = score_elem.text.strip()

                # Parse score (e.g., "70-65" or "W 70-65")
                score_parts = score_text.split()[-1].split('-')
                if len(score_parts) != 2:
                    continue

                team_score = int(score_parts[0])
                opp_score = int(score_parts[1])

                # Determine team1/team2 based on win/loss
                if is_win:
                    team1_name = team_name
                    team1_score = team_score
                    team2_name = opponent_name
                    team2_score = opp_score
                else:
                    team1_name = opponent_name
                    team1_score = opp_score
                    team2_name = team_name
                    team2_score = team_score

                # Check if game already exists
                existing = BoxScore.query.filter_by(
                    game_date=game_date,
                    team1_name=team1_name,
                    team2_name=team2_name
                ).first()

                if not existing:
                    # Add game
                    game = BoxScore(
                        game_date=game_date,
                        classification=classification,
                        team1_name=team1_name,
                        team1_score=team1_score,
                        team2_name=team2_name,
                        team2_score=team2_score,
                        submitted_by='maxpreps_scraper'
                    )
                    db.session.add(game)
                    games_added += 1
                    print(f"  ✓ {game_date}: {team1_name} {team1_score} - {team2_name} {team2_score}")

            except Exception as e:
                continue

        db.session.commit()
        print(f"  Added {games_added} games for {team_name}")
        return games_added

    except Exception as e:
        print(f"  ✗ Error scraping {team_name}: {e}")
        return 0

def main():
    """Scrape all missing teams"""
    print("="*80)
    print("SCRAPING MISSING TEAMS FROM MAXPREPS")
    print("="*80)

    driver = setup_driver()
    total_games = 0

    try:
        with app.app_context():
            for team_name, classification, url in TEAMS_TO_SCRAPE:
                games = scrape_team_schedule(driver, team_name, classification, url)
                total_games += games
                time.sleep(2)  # Be nice to MaxPreps

        print("\n" + "="*80)
        print(f"TOTAL NEW GAMES ADDED: {total_games}")
        print("="*80)

    finally:
        driver.quit()

    # Now update rankings
    print("\nUpdating rankings with new game data...")
    from update_rankings_with_records import update_rankings_with_records
    update_rankings_with_records()
    print("✓ Rankings updated!")

if __name__ == '__main__':
    main()
