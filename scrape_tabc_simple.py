"""
Simple TABC Rankings Scraper (No Selenium Required)
Scrapes TABC rankings using requests only
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

TABC_URLS = {
    'uil': 'https://tabchoops.org/uil-boys-rankings/',
    'private': 'https://tabchoops.org/private-school-boys-rankings/'
}

def scrape_tabc_uil():
    """Scrape TABC UIL rankings"""
    print("Scraping TABC UIL rankings...")

    url = TABC_URLS['uil']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"  Failed with status {response.status_code}")
            return {}

        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()

        # Parse rankings by classification
        rankings = {}
        class_map = {
            '6A': 'AAAAAA',
            '5A': 'AAAAA',
            '4A': 'AAAA',
            '3A': 'AAA',
            '2A': 'AA',
            '1A': 'A'
        }

        # Split by classification headers
        for class_name, internal_code in class_map.items():
            # Find section for this classification
            pattern = rf'{class_name}[\s\n]+((?:\d+\.\s+[^\n]+\n?)+)'
            match = re.search(pattern, text, re.MULTILINE)

            if match:
                teams_text = match.group(1)
                # Parse individual teams
                team_pattern = r'(\d+)\.\s+([A-Za-z\s\-\.\']+?)(?:\s+\(([\d]+)-([\d]+)\))?(?:\n|$)'
                teams = []

                for team_match in re.finditer(team_pattern, teams_text):
                    rank = int(team_match.group(1))
                    team_name = team_match.group(2).strip()
                    wins = int(team_match.group(3)) if team_match.group(3) else 0
                    losses = int(team_match.group(4)) if team_match.group(4) else 0

                    teams.append({
                        'rank': rank,
                        'team_name': team_name,
                        'wins': wins,
                        'losses': losses,
                        'classification': internal_code,
                        'source': 'TABC'
                    })

                rankings[internal_code] = teams[:25]  # Top 25
                print(f"  {class_name}: {len(teams)} teams")

        return rankings

    except Exception as e:
        print(f"  Error: {e}")
        return {}

def scrape_tabc_private():
    """Scrape TABC private school rankings"""
    print("Scraping TABC private school rankings...")

    url = TABC_URLS['private']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"  Failed with status {response.status_code}")
            return {}

        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()

        # Parse rankings by classification
        rankings = {
            'TAPPS_6A': [],
            'TAPPS_5A': [],
            'TAPPS_4A': [],
            'TAPPS_3A': [],
            'TAPPS_2A': [],
            'TAPPS_1A': []
        }

        # Classification header patterns (TABC uses various formats)
        class_patterns = [
            (r'(?:TAPPS\s*6A|SPC\s*4A|6A/SPC)', 'TAPPS_6A'),
            (r'(?:TAPPS\s*5A|SPC\s*3A|5A/SPC)', 'TAPPS_5A'),
            (r'TAPPS\s*4A', 'TAPPS_4A'),
            (r'TAPPS\s*3A', 'TAPPS_3A'),
            (r'TAPPS\s*2A', 'TAPPS_2A'),
            (r'TAPPS\s*1A', 'TAPPS_1A'),
        ]

        # Find all classification sections
        # Split text into sections by looking for classification headers
        lines = text.split('\n')
        current_class = None
        # Pattern handles both hyphens (-) and en-dashes (–) in records
        team_pattern = r'^\s*(\d+)\.\s+(.+?)\s+\((\d+)[-–](\d+)\)\s*$'

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line is a classification header
            for pattern, class_code in class_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    current_class = class_code
                    break

            # Try to parse as a team entry
            if current_class:
                team_match = re.match(team_pattern, line)
                if team_match:
                    rank = int(team_match.group(1))
                    team_name = team_match.group(2).strip()
                    wins = int(team_match.group(3))
                    losses = int(team_match.group(4))

                    rankings[current_class].append({
                        'rank': rank,
                        'team_name': team_name,
                        'wins': wins,
                        'losses': losses,
                        'classification': current_class,
                        'source': 'TABC'
                    })

        # Print summary
        for class_code, teams in rankings.items():
            if teams:
                print(f"  {class_code}: {len(teams)} teams")

        return rankings

    except Exception as e:
        print(f"  Error: {e}")
        return {}

def scrape_all_tabc():
    """Scrape all TABC rankings"""
    print("="*60)
    print("SCRAPING TABC RANKINGS")
    print("="*60)
    print()

    rankings = {
        'last_updated': datetime.now().isoformat(),
        'source': 'TABC',
        'uil': {},
        'private': {}
    }

    # Scrape UIL
    uil_rankings = scrape_tabc_uil()
    if uil_rankings:
        rankings['uil'] = uil_rankings

    # Scrape Private
    private_rankings = scrape_tabc_private()
    if private_rankings:
        rankings['private'] = private_rankings

    print()
    print("="*60)
    print("TABC SCRAPING COMPLETE")
    print("="*60)

    # Summary
    total_uil = sum(len(teams) for teams in rankings['uil'].values())
    total_private = sum(len(teams) for teams in rankings['private'].values())
    print(f"UIL: {total_uil} teams across {len(rankings['uil'])} classifications")
    print(f"Private: {total_private} teams across {len(rankings['private'])} classifications")

    return rankings

if __name__ == '__main__':
    rankings = scrape_all_tabc()

    # Save to file
    output_file = 'tabc_rankings_scraped.json'
    with open(output_file, 'w') as f:
        json.dump(rankings, f, indent=2)

    print(f"\n✓ Rankings saved to {output_file}")
