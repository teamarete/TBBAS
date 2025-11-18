"""
Standalone test script for MaxPreps scraper
Tests scraping without Flask dependencies
"""

import sys
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleMaxPrepsScraper:
    """Simple standalone MaxPreps scraper for testing"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def get_selenium_driver(self):
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
            logger.error(f"Error initializing Selenium: {e}")
            return None

    def scrape_daily_scores(self, target_date):
        """Scrape scores for a specific date"""
        date_str = target_date.strftime('%m/%d/%Y')
        url = f"https://www.maxpreps.com/tx/basketball/scores/?date={date_str}"

        logger.info(f"Scraping MaxPreps scores for {date_str}")
        logger.info(f"URL: {url}")
        games = []
        driver = None

        try:
            # Use Selenium to handle JavaScript
            driver = self.get_selenium_driver()

            if driver is None:
                logger.error("Could not initialize Selenium driver")
                return games

            # Load the page
            logger.info("Loading page with Selenium...")
            driver.get(url)

            # Wait for game elements
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            try:
                logger.info("Waiting for game containers to load...")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "contest-box-item"))
                )
                logger.info("Game containers found!")
            except Exception as wait_error:
                logger.warning(f"Timeout or no games found: {wait_error}")
                # Still try to parse what we have
                pass

            # Parse the page
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find game containers
            game_containers = soup.find_all('div', class_='contest-box-item')
            logger.info(f"Found {len(game_containers)} game containers")

            for idx, container in enumerate(game_containers):
                try:
                    # Check game state
                    state = container.get('data-contest-state', '')
                    logger.debug(f"Container {idx+1}: state={state}")

                    if state != 'boxscore' and state != 'final':
                        logger.debug(f"  Skipping (not completed)")
                        continue

                    # Find teams
                    team_items = container.find('ul', class_='teams')
                    if not team_items:
                        logger.debug(f"  No teams found")
                        continue

                    teams = team_items.find_all('li')
                    if len(teams) < 2:
                        logger.debug(f"  Less than 2 teams")
                        continue

                    # Extract team names from <div class="name">
                    team1_elem = teams[0].find('div', class_='name')
                    team2_elem = teams[1].find('div', class_='name')

                    if not team1_elem or not team2_elem:
                        logger.debug(f"  Team names not found")
                        continue

                    team1_name = team1_elem.get_text(strip=True)
                    team2_name = team2_elem.get_text(strip=True)

                    # Extract scores from <div class="score">
                    team1_score_elem = teams[0].find('div', class_='score')
                    team2_score_elem = teams[1].find('div', class_='score')

                    if not team1_score_elem or not team2_score_elem:
                        logger.debug(f"  Scores not found")
                        continue

                    team1_score_text = team1_score_elem.get_text(strip=True)
                    team2_score_text = team2_score_elem.get_text(strip=True)

                    try:
                        team1_score = int(team1_score_text)
                        team2_score = int(team2_score_text)
                    except ValueError:
                        logger.debug(f"  Invalid scores: {team1_score_text}, {team2_score_text}")
                        continue

                    game = {
                        'date': target_date.date(),
                        'team1_name': team1_name,
                        'team1_score': team1_score,
                        'team2_name': team2_name,
                        'team2_score': team2_score,
                    }
                    games.append(game)
                    logger.info(f"  ✓ {team1_name} {team1_score} vs {team2_name} {team2_score}")

                except Exception as e:
                    logger.debug(f"  Error parsing container {idx+1}: {e}")
                    continue

            logger.info(f"Successfully scraped {len(games)} games")

        except Exception as e:
            logger.error(f"Error scraping: {e}")
            import traceback
            logger.error(traceback.format_exc())

        finally:
            if driver:
                driver.quit()

        return games


def test_scraper():
    """Test the scraper"""
    logger.info("="*60)
    logger.info("MaxPreps Scraper Test")
    logger.info("="*60)

    scraper = SimpleMaxPrepsScraper()

    # Test dates (2025 season - user's requested dates)
    test_dates = [
        datetime(2025, 11, 14),
        datetime(2025, 11, 15),
    ]

    all_games = []

    for test_date in test_dates:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing: {test_date.strftime('%B %d, %Y')}")
        logger.info(f"{'='*60}\n")

        games = scraper.scrape_daily_scores(test_date)
        all_games.extend(games)

        logger.info(f"\nResults: {len(games)} games found\n")

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Dates tested: {len(test_dates)}")
    logger.info(f"Total games: {len(all_games)}")

    if all_games:
        logger.info("\n✓ SUCCESS - Scraper is working!")
        return 0
    else:
        logger.warning("\n⚠ WARNING - No games found")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(test_scraper())
    except KeyboardInterrupt:
        logger.info("\nInterrupted")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nFailed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
