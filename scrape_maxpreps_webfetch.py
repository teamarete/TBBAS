"""
MaxPreps Rankings Scraper using WebFetch API
Alternative to Selenium-based scraper that avoids ChromeDriver issues
"""
import anthropic
import json
import os
from datetime import datetime
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

def fetch_maxpreps_rankings(division, url):
    """Fetch MaxPreps rankings for a division using Claude API"""
    print(f"Fetching MaxPreps {division}...")

    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        # Use the prompt caching feature to efficiently fetch web content
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"""Fetch this MaxPreps ranking page and extract the basketball team rankings:

{url}

Extract and return ONLY a JSON array of teams with this exact format:
[
  {{"rank": 1, "team_name": "Team Name", "wins": 18, "losses": 2, "record": "18-2"}},
  {{"rank": 2, "team_name": "Another Team", "wins": 20, "losses": 1, "record": "20-1"}}
]

Rules:
- Return ONLY the JSON array, no other text
- Include all teams in the rankings (top 25 for UIL, top 10 for TAPPS)
- If record has 3 parts like "18-2-0", use first two numbers for wins/losses
- team_name should be clean without city prefix if possible (e.g., "Seven Lakes" not "Katy Seven Lakes")
"""
            }]
        )

        # Parse the JSON response
        text = response.content[0].text.strip()

        # Clean up any markdown code blocks
        if text.startswith('```'):
            text = text.split('\n', 1)[1]
            text = text.rsplit('\n```', 1)[0]
        if text.startswith('json'):
            text = text[4:].strip()

        teams = json.loads(text)

        print(f"  Found {len(teams)} teams")
        if teams:
            print(f"  Top team: #{teams[0]['rank']} {teams[0]['team_name']}")

        return teams

    except Exception as e:
        print(f"  Error fetching {division}: {e}")
        return []

def scrape_all_maxpreps():
    """Scrape all MaxPreps rankings"""
    print("=" * 80)
    print(f"MAXPREPS RANKINGS SCRAPE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    rankings = {
        'uil': {},
        'tapps': {},
        'spc': {}
    }

    for division, url in MAXPREPS_URLS.items():
        division_rankings = fetch_maxpreps_rankings(division, url)

        if division.startswith('TAPPS_'):
            rankings['tapps'][division] = division_rankings
        elif division == 'SPC':
            rankings['spc'] = division_rankings
        else:
            rankings['uil'][division] = division_rankings

    # Save rankings
    output_file = Path(__file__).parent / 'data' / f'maxpreps_rankings_{datetime.now().strftime("%Y%m%d")}.json'
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump({
            'date': datetime.now().isoformat(),
            'maxpreps': rankings
        }, f, indent=2)

    print(f"\n✓ MaxPreps rankings saved to {output_file}")
    print("=" * 80)

    return rankings

if __name__ == '__main__':
    scrape_all_maxpreps()
