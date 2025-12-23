"""
Weekly Rankings Scraper
Scrapes TABC and MaxPreps rankings every Monday at 2 PM CST

Final rankings use 3-way weighted average:
- 33% Calculated (from box score efficiency ratings)
- 33% TABC
- 33% MaxPreps
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
from pathlib import Path

# MaxPreps ranking URLs
MAXPREPS_URLS = {
    # UIL
    '6A': 'https://www.maxpreps.com/tx/basketball/25-26/division/division-6a/rankings/1/?statedivisionid=f30bc9a3-067d-42e3-9954-2d6496693e1a',
    '5A': 'https://www.maxpreps.com/tx/basketball/25-26/division/division-5a/rankings/1/?statedivisionid=2a0df19a-ccb6-42ea-9f00-029bc1dfe1a6',
    '4A': 'https://www.maxpreps.com/tx/basketball/25-26/division/division-4a/rankings/1/?statedivisionid=eb02b34b-b4b1-4cb7-aef3-cb79b153adec',
    '3A': 'https://www.maxpreps.com/tx/basketball/25-26/division/division-3a/rankings/1/?statedivisionid=5d46b71b-854c-4f97-9b92-6e46b25e1961',
    '2A': 'https://www.maxpreps.com/tx/basketball/25-26/division/division-2a/rankings/1/?statedivisionid=00e4af8f-674c-482f-9f1e-a5ee9e879d16',
    '1A': 'https://www.maxpreps.com/tx/basketball/25-26/division/division-1a/rankings/1/?statedivisionid=ddc5fa20-ecdf-4e62-aa33-cfc02452bed9',
    # TAPPS
    'TAPPS_6A': 'https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-6a/rankings/1/?sectiondivisionid=1affa478-5b94-4e17-b8ca-dd572d9b1e02',
    'TAPPS_5A': 'https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-5a/rankings/1/?sectiondivisionid=c1741f02-d83d-4726-bc6c-00f7ebf3b5c9',
    'TAPPS_4A': 'https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-4a/rankings/1/?sectiondivisionid=22e9cece-a43d-46c8-8475-cf93ae55f46c',
    'TAPPS_3A': 'https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-3a/rankings/1/?sectiondivisionid=f966dbd3-90d6-42da-b7d1-1cc017e3b580',
    'TAPPS_2A': 'https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-2a/rankings/1/?sectiondivisionid=a8fd3dd2-936d-40b9-9ee8-8fbbcb096d11',
    'TAPPS_1A': 'https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-1a/rankings/1/?sectiondivisionid=48b38de3-57bc-4d34-b578-25adac65421f',
    'SPC': 'https://www.maxpreps.com/tx/basketball/25-26/division/division-southwest-prep/rankings/1/?statedivisionid=a4d800c8-6fa7-4b2f-b520-f4c19c7da173',
}

# TABC ranking URLs
TABC_URLS = {
    'uil': 'https://tabchoops.org/uil-boys-rankings/',
    'private': 'https://tabchoops.org/private-school-boys-rankings/'
}

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
        print(f"  Error initializing Selenium: {e}")
        print("  Note: Selenium and ChromeDriver are required for MaxPreps scraping")
        print("  Install with: pip install selenium webdriver-manager")
        return None

def scrape_maxpreps_rankings(division, url):
    """Scrape MaxPreps rankings for a division using Selenium"""
    print(f"Scraping MaxPreps {division}...")

    teams = []
    driver = None

    try:
        # MaxPreps loads rankings via JavaScript, so we need Selenium
        driver = get_selenium_driver()

        if driver is None:
            print("  ERROR: Could not initialize Selenium driver")
            return []

        # Load the page and wait for JavaScript to render
        driver.get(url)

        # Wait for ranking elements to load (up to 15 seconds)
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        try:
            # Wait for ranking table/list to appear
            # MaxPreps rankings typically use a table or list structure
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table, .ranking-list, .rankings-table, [class*='rank']"))
            )
        except:
            print(f"  No rankings found or timeout for {division}")
            return []

        # Parse the rendered page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Try multiple patterns to find rankings
        # Pattern 1: Look for table rows
        ranking_rows = soup.find_all('tr')
        if ranking_rows and len(ranking_rows) > 1:
            for row in ranking_rows:
                try:
                    # Skip header rows
                    if row.find('th'):
                        continue

                    cells = row.find_all('td')
                    if len(cells) < 2:
                        continue

                    # Try to extract rank (usually first cell)
                    rank_text = cells[0].get_text(strip=True)
                    # Remove any non-digit characters
                    rank_match = re.search(r'(\d+)', rank_text)
                    if not rank_match:
                        continue
                    rank = int(rank_match.group(1))

                    # Find team name (usually second or third cell)
                    team_name = None
                    record = None

                    for cell in cells[1:]:
                        text = cell.get_text(strip=True)

                        # Skip empty cells or cells with just numbers
                        if not text or text.isdigit():
                            continue

                        # Check if this looks like a record (e.g., "12-3" or "12-3-0")
                        if re.match(r'^\d+-\d+(-\d+)?$', text):
                            record = text
                            continue

                        # Check if this might be a team name
                        # Team names should be at least 2 chars and contain letters
                        if len(text) >= 2 and any(c.isalpha() for c in text):
                            # Skip common column headers
                            if text.lower() in ['team', 'school', 'record', 'wins', 'losses', 'rating', 'rank']:
                                continue
                            team_name = text
                            break

                    if team_name:
                        team_data = {
                            'rank': rank,
                            'team_name': team_name
                        }

                        # Parse record if found
                        if record and '-' in record:
                            parts = record.split('-')
                            if len(parts) >= 2:
                                team_data['wins'] = int(parts[0])
                                team_data['losses'] = int(parts[1])
                                team_data['record'] = record

                        teams.append(team_data)

                except Exception as e:
                    continue

        # Pattern 2: If no table found, try looking for list items or divs with ranking data
        if not teams:
            ranking_items = soup.find_all(['li', 'div'], class_=re.compile(r'rank|team', re.I))

            for item in ranking_items:
                try:
                    text = item.get_text()

                    # Try to parse "Rank. Team Name (Record)" pattern
                    match = re.match(r'(\d+)[\.\)]\s+(.+?)(?:\s+\((\d+-\d+)\))?$', text.strip())
                    if match:
                        rank = int(match.group(1))
                        team_name = match.group(2).strip()
                        record = match.group(3)

                        team_data = {
                            'rank': rank,
                            'team_name': team_name
                        }

                        if record and '-' in record:
                            parts = record.split('-')
                            team_data['wins'] = int(parts[0])
                            team_data['losses'] = int(parts[1])
                            team_data['record'] = record

                        teams.append(team_data)

                except Exception as e:
                    continue

        # Remove duplicates and sort by rank
        seen_ranks = set()
        unique_teams = []
        for team in teams:
            if team['rank'] not in seen_ranks:
                seen_ranks.add(team['rank'])
                unique_teams.append(team)

        teams = sorted(unique_teams, key=lambda x: x['rank'])

        # Limit to top 25 for UIL, top 10 for TAPPS
        if division.startswith('TAPPS_'):
            teams = teams[:10]
        else:
            teams = teams[:25]

        print(f"  Found {len(teams)} teams")

        if teams and len(teams) > 0:
            print(f"  Top team: #{teams[0]['rank']} {teams[0]['team_name']}")

    except Exception as e:
        print(f"  Error scraping MaxPreps {division}: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()

    return teams

def parse_tabc_team_list(text):
    """Parse team list from TABC text content"""
    teams = []
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line or len(line) < 3:
            continue

        # Match patterns like:
        # "1. Team Name (12-3)" or "1 Team Name 12-3" or "1) Team Name"
        # Try to capture rank, team name, and optional record
        match = re.match(r'^(\d+)[\.\)\s]+(.+?)(?:\s+\((\d+-\d+)\)|\s+(\d+-\d+))?$', line)
        if match:
            rank = int(match.group(1))
            team_name = match.group(2).strip()
            record = match.group(3) or match.group(4)  # Could be in parens or not

            # Clean up team name - remove trailing record if it wasn't captured
            team_name = re.sub(r'\s+\d+-\d+$', '', team_name)
            team_name = re.sub(r'\s+\(.*?\)$', '', team_name)
            team_name = re.sub(r'\s+', ' ', team_name)

            # Skip if team name is too short or just numbers
            if len(team_name) < 2 or team_name.isdigit():
                continue

            team_data = {
                'rank': rank,
                'team_name': team_name
            }

            # Parse record if found
            if record and '-' in record:
                wins, losses = record.split('-')
                team_data['wins'] = int(wins)
                team_data['losses'] = int(losses)
                team_data['record'] = record
            else:
                team_data['record'] = None

            teams.append(team_data)

    return teams

def scrape_tabc_uil_rankings(url):
    """Scrape TABC UIL rankings"""
    print(f"Scraping TABC UIL from {url}...")

    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text()

        rankings = {}

        # UIL classifications
        classifications = {
            '6A': ['Class 6A', '6A'],
            '5A': ['Class 5A', '5A'],
            '4A': ['Class 4A', '4A'],
            '3A': ['Class 3A', '3A'],
            '2A': ['Class 2A', '2A'],
            '1A': ['Class 1A', '1A']
        }

        for class_code, patterns in classifications.items():
            for pattern in patterns:
                # Find the classification section
                pattern_pos = text_content.find(pattern)
                if pattern_pos == -1:
                    continue

                # Extract text after the classification header
                section_start = pattern_pos + len(pattern)

                # Find the next classification or end
                section_end = len(text_content)
                for other_class, other_patterns in classifications.items():
                    if other_class == class_code:
                        continue
                    for other_pattern in other_patterns:
                        next_pos = text_content.find(other_pattern, section_start)
                        if next_pos != -1 and next_pos < section_end:
                            section_end = next_pos

                section_text = text_content[section_start:section_end]
                teams = parse_tabc_team_list(section_text)

                if teams:
                    rankings[class_code] = teams[:25]  # Top 25
                    print(f"  {class_code}: Found {len(teams[:25])} teams")
                    break  # Found data for this classification

        return rankings

    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return {}

def scrape_tabc_private_rankings(url):
    """Scrape TABC Private School rankings"""
    print(f"Scraping TABC Private from {url}...")

    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text()

        rankings = {}

        # Private school classifications
        classifications = {
            'TAPPS 6A/SPC 4A': 'TAPPS_6A',
            'TAPPS 5A/SPC 3A': 'TAPPS_5A',
            'TAPPS 4A': 'TAPPS_4A',
            'TAPPS 3A': 'TAPPS_3A',
            'TAPPS 2A': 'TAPPS_2A',
            'TAPPS 1A': 'TAPPS_1A'
        }

        for class_name, class_code in classifications.items():
            # Find the classification section
            pattern_pos = text_content.find(class_name)
            if pattern_pos == -1:
                continue

            # Extract text after the classification header
            section_start = pattern_pos + len(class_name)

            # Find the next classification or end
            section_end = len(text_content)
            for other_class in classifications.keys():
                if other_class == class_name:
                    continue
                next_pos = text_content.find(other_class, section_start)
                if next_pos != -1 and next_pos < section_end:
                    section_end = next_pos

            section_text = text_content[section_start:section_end]
            teams = parse_tabc_team_list(section_text)

            if teams:
                rankings[class_code] = teams[:10]  # Top 10 per classification
                print(f"  {class_code}: Found {len(teams[:10])} teams")

        return rankings

    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return {}

def scrape_all_rankings():
    """Scrape all rankings from TABC and MaxPreps"""
    print("=" * 80)
    print(f"WEEKLY RANKINGS SCRAPE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    rankings = {
        'date': datetime.now().isoformat(),
        'tabc': {
            'uil': {},
            'private': {}
        },
        'maxpreps': {
            'uil': {},
            'tapps': {},
            'spc': {}
        }
    }

    # Scrape TABC
    print("\n--- TABC RANKINGS ---")
    rankings['tabc']['uil'] = scrape_tabc_uil_rankings(TABC_URLS['uil'])
    rankings['tabc']['private'] = scrape_tabc_private_rankings(TABC_URLS['private'])

    # Scrape MaxPreps
    print("\n--- MAXPREPS RANKINGS ---")
    for division, url in MAXPREPS_URLS.items():
        division_rankings = scrape_maxpreps_rankings(division, url)

        if division.startswith('TAPPS_'):
            rankings['maxpreps']['tapps'][division] = division_rankings
        elif division == 'SPC':
            rankings['maxpreps']['spc'] = division_rankings
        else:
            rankings['maxpreps']['uil'][division] = division_rankings

    # Save raw scraped data
    output_file = Path(__file__).parent / 'data' / f'weekly_rankings_{datetime.now().strftime("%Y%m%d")}.json'
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(rankings, f, indent=2)

    print(f"\n✓ Rankings saved to {output_file}")
    print("=" * 80)

    return rankings

if __name__ == '__main__':
    scrape_all_rankings()
