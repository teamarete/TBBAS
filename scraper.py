"""
TBBAS Web Scraper
Scrapes Texas high school basketball rankings from TABC
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re


class TABCScraper:
    """Scraper for TABC Hoops rankings"""

    UIL_URL = "https://tabchoops.org/uil-boys-rankings/"
    PRIVATE_URL = "https://tabchoops.org/private-school-boys-rankings/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def scrape_uil_rankings(self):
        """Scrape UIL rankings from TABC"""
        try:
            response = self.session.get(self.UIL_URL, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            rankings = {
                'AAAAAA': [],  # 6A
                'AAAAA': [],   # 5A
                'AAAA': [],    # 4A
                'AAA': [],     # 3A
                'AA': [],      # 2A
                'A': []        # 1A
            }

            # Get all text content
            text_content = soup.get_text()

            # Split by classification headers
            classifications = {
                'AAAAAA': ['Class 6A', '6A'],
                'AAAAA': ['Class 5A', '5A'],
                'AAAA': ['Class 4A', '4A'],
                'AAA': ['Class 3A', '3A'],
                'AA': ['Class 2A', '2A'],
                'A': ['Class 1A', '1A']
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
                    teams = self._parse_team_list(section_text)

                    if teams:
                        rankings[class_code] = teams[:40]  # Top 40
                        break  # Found data for this classification

            return rankings

        except Exception as e:
            print(f"Error scraping UIL rankings: {e}")
            import traceback
            traceback.print_exc()
            return None

    def scrape_private_rankings(self):
        """Scrape Private School rankings from TABC"""
        try:
            response = self.session.get(self.PRIVATE_URL, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            teams = []
            headers = soup.find_all(['h4', 'h3', 'strong'])

            for header in headers:
                header_text = header.get_text().strip()

                # Look for TAPPS/SPC headers
                if 'TAPPS' in header_text or 'SPC' in header_text:
                    next_elem = header.find_next_sibling()
                    if next_elem:
                        text = next_elem.get_text()
                        parsed_teams = self._parse_team_list(text)
                        teams.extend(parsed_teams)

            # Remove duplicates while preserving order
            seen = set()
            unique_teams = []
            for team in teams:
                if team['team_name'] not in seen:
                    seen.add(team['team_name'])
                    unique_teams.append(team)

            return unique_teams[:40]  # Top 40

        except Exception as e:
            print(f"Error scraping private rankings: {e}")
            return None

    def _parse_team_list(self, text):
        """Parse team list from text"""
        teams = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # Match patterns like "1. Team Name" or "1 Team Name" or "1) Team Name"
            match = re.match(r'^(\d+)[\.\)\s]+(.+?)(?:\s+\(.*?\))?$', line)
            if match:
                rank = int(match.group(1))
                team_name = match.group(2).strip()

                # Clean up team name
                team_name = re.sub(r'\s+', ' ', team_name)

                # Skip if team name is too short or just numbers
                if len(team_name) < 2 or team_name.isdigit():
                    continue

                teams.append({
                    'rank': rank,
                    'team_name': team_name,
                    'wins': None,
                    'losses': None,
                    'district': None
                })

        return teams

    def scrape_all(self):
        """Scrape all rankings"""
        print("Scraping TABC rankings...")

        uil_rankings = self.scrape_uil_rankings()
        private_rankings = self.scrape_private_rankings()

        data = {
            'last_updated': datetime.now().isoformat(),
            'uil': uil_rankings,
            'private': private_rankings
        }

        return data

    def save_to_file(self, data, filename='data/rankings.json'):
        """Save rankings to JSON file"""
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Rankings saved to {filename}")


if __name__ == '__main__':
    scraper = TABCScraper()
    data = scraper.scrape_all()

    if data:
        scraper.save_to_file(data)

        # Print summary
        if data.get('uil'):
            for classification, teams in data['uil'].items():
                print(f"\n{classification}: {len(teams)} teams")
                if teams:
                    print(f"  #1: {teams[0]['team_name']}")

        if data.get('private'):
            print(f"\nPrivate: {len(data['private'])} teams")
            if data['private']:
                print(f"  #1: {data['private'][0]['team_name']}")
