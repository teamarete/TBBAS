"""Test with a date that should have completed games"""

import logging
from datetime import datetime
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

# Initialize Selenium
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Try November 16, 2024 (yesterday from today's perspective)
    url = "https://www.maxpreps.com/tx/basketball/scores/?date=11/16/2024"
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
    for c in containers:
        state = c.get('data-contest-state', 'unknown')
        states[state] = states.get(state, 0) + 1

    logger.info(f"States: {states}")

    # Try to find completed games
    for container in containers[:5]:
        state = container.get('data-contest-state')
        if state in ['boxscore', 'final']:
            logger.info(f"\nFound completed game!")
            teams_ul = container.find('ul', class_='teams')
            if teams_ul:
                team_lis = teams_ul.find_all('li')
                for team_li in team_lis:
                    name_div = team_li.find('div', class_='name')
                    score_span = team_li.find('span', class_='score')
                    if name_div and score_span:
                        logger.info(f"  {name_div.get_text(strip=True)}: {score_span.get_text(strip=True)}")

finally:
    driver.quit()
