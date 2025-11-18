"""
Debug script to save and inspect MaxPreps HTML
"""

import sys
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def inspect_html():
    """Inspect the actual HTML structure"""

    # Initialize Selenium
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://www.maxpreps.com/tx/basketball/scores/?date=11/14/2024"
        logger.info(f"Loading: {url}")

        driver.get(url)

        # Wait for containers
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "contest-box-item"))
        )

        # Get the HTML
        html = driver.page_source

        # Save to file
        with open('maxpreps_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info("HTML saved to maxpreps_debug.html")

        # Parse and show structure of first game
        soup = BeautifulSoup(html, 'html.parser')
        containers = soup.find_all('div', class_='contest-box-item')

        logger.info(f"\nFound {len(containers)} containers\n")

        # Show first 3 containers
        for i in range(min(3, len(containers))):
            container = containers[i]
            logger.info(f"="*60)
            logger.info(f"Container {i+1}:")
            logger.info(f"="*60)
            logger.info(f"State: {container.get('data-contest-state')}")
            logger.info(f"Live: {container.get('data-contest-live')}")

            # Show the HTML structure
            logger.info("\nHTML structure:")
            logger.info(container.prettify()[:1000])  # First 1000 chars

            # Try to find teams
            teams_ul = container.find('ul', class_='teams')
            if teams_ul:
                logger.info(f"\nFound teams <ul>")
                team_lis = teams_ul.find_all('li')
                logger.info(f"Number of <li> elements: {len(team_lis)}")

                for j, team_li in enumerate(team_lis):
                    logger.info(f"\nTeam {j+1} <li>:")
                    logger.info(team_li.prettify()[:500])

                    # Look for team name
                    team_link = team_li.find('a')
                    if team_link:
                        logger.info(f"  Team name: {team_link.get_text(strip=True)}")

                    # Look for score
                    score_span = team_li.find('span', class_='score')
                    if score_span:
                        logger.info(f"  Score: {score_span.get_text(strip=True)}")
            else:
                logger.info("\nNo <ul class='teams'> found!")

            logger.info("\n")

    finally:
        driver.quit()


if __name__ == "__main__":
    inspect_html()
