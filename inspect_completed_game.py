"""Inspect the HTML structure of completed games"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    url = "https://www.maxpreps.com/tx/basketball/scores/?date=11/14/2025"
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "contest-box-item"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    containers = soup.find_all('div', class_='contest-box-item')

    # Find first completed game and show full HTML
    for container in containers:
        state = container.get('data-contest-state')
        if state == 'boxscore':
            logger.info("="*70)
            logger.info("COMPLETED GAME HTML STRUCTURE:")
            logger.info("="*70)
            logger.info(container.prettify()[:2000])
            logger.info("\n[...HTML truncated...]\n")

            # Parse it
            logger.info("="*70)
            logger.info("PARSED ELEMENTS:")
            logger.info("="*70)

            teams_ul = container.find('ul', class_='teams')
            if teams_ul:
                team_lis = teams_ul.find_all('li')
                for i, team_li in enumerate(team_lis, 1):
                    logger.info(f"\nTeam {i}:")

                    # Try different ways to find team name
                    name_div = team_li.find('div', class_='name')
                    name_a = team_li.find('a')

                    logger.info(f"  <div class='name'>: {name_div.get_text(strip=True) if name_div else 'NOT FOUND'}")
                    logger.info(f"  <a>: {name_a.get_text(strip=True) if name_a else 'NOT FOUND'}")

                    # Try to find score in different ways
                    score_span = team_li.find('span', class_='score')
                    score_div = team_li.find('div', class_='score')
                    all_text = team_li.get_text(strip=True)

                    logger.info(f"  <span class='score'>: {score_span.get_text(strip=True) if score_span else 'NOT FOUND'}")
                    logger.info(f"  <div class='score'>: {score_div.get_text(strip=True) if score_div else 'NOT FOUND'}")
                    logger.info(f"  All text: {all_text}")

                    # Show the full HTML for this team
                    logger.info(f"\n  Full <li> HTML:")
                    logger.info(team_li.prettify()[:500])

            break

finally:
    driver.quit()
