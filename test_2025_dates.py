"""Test with 2025 dates (current season)"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Test 11/14/2025 (the actual date from user's URL!)
    url = "https://www.maxpreps.com/tx/basketball/scores/?date=11/14/2025"
    logger.info(f"Testing: {url}")

    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "contest-box-item"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    containers = soup.find_all('div', class_='contest-box-item')

    logger.info(f"Found {len(containers)} containers")

    # Count states
    states = {}
    completed_count = 0

    for c in containers:
        state = c.get('data-contest-state', 'unknown')
        states[state] = states.get(state, 0) + 1

        if state in ['boxscore', 'final']:
            completed_count += 1

    logger.info(f"States: {states}")
    logger.info(f"Completed games: {completed_count}")

    # Show first completed game
    for container in containers:
        state = container.get('data-contest-state')
        if state in ['boxscore', 'final']:
            logger.info(f"\n✓ Found completed game (state={state}):")
            teams_ul = container.find('ul', class_='teams')
            if teams_ul:
                team_lis = teams_ul.find_all('li')
                logger.info(f"  Teams found: {len(team_lis)}")
                for i, team_li in enumerate(team_lis):
                    name_div = team_li.find('div', class_='name')
                    score_span = team_li.find('span', class_='score')
                    if name_div:
                        team_name = name_div.get_text(strip=True)
                        score = score_span.get_text(strip=True) if score_span else "N/A"
                        logger.info(f"    Team {i+1}: {team_name} - {score}")
            break  # Just show first one

finally:
    driver.quit()
