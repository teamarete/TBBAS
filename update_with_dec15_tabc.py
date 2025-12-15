"""
Update rankings with December 15, 2025 TABC data
Integrates TABC December 15 rankings with existing data and updates all records
"""
import json
from datetime import datetime
from pathlib import Path

def load_tabc_dec15_data():
    """Load TABC December 15, 2025 rankings from JSON files"""
    tabc_uil_file = Path(__file__).parent / 'data' / 'tabc_rankings_dec15_2025.json'
    tabc_private_file = Path(__file__).parent / 'data' / 'tabc_rankings_private_dec15_2025.json'

    # Load UIL rankings
    with open(tabc_uil_file, 'r') as f:
        uil_data = json.load(f)

    # Load Private rankings
    with open(tabc_private_file, 'r') as f:
        private_data = json.load(f)

    # Convert to format expected by merge_rankings
    tabc_data = {
        'last_updated': '2025-12-15T00:00:00',
        'uil': {},
        'private': {}
    }

    # Map UIL classifications
    classification_map = {
        '6A': 'AAAAAA',
        '5A': 'AAAAA',
        '4A': 'AAAA',
        '3A': 'AAA',
        '2A': 'AA',
        '1A': 'A'
    }

    for cls_short, cls_long in classification_map.items():
        teams = uil_data['uil'][cls_short]
        tabc_data['uil'][cls_long] = []
        for team in teams:
            # Parse record
            record = team['record']
            if '-' in record:
                wins, losses = record.split('-')
                wins = int(wins)
                losses = int(losses)
            else:
                wins = 0
                losses = 0

            tabc_data['uil'][cls_long].append({
                'rank': team['rank'],
                'team_name': team['team_name'],
                'wins': wins,
                'losses': losses,
                'record': record
            })

    # Map TAPPS classifications (already in correct format)
    for cls, teams in private_data['private'].items():
        tabc_data['private'][cls] = []
        for team in teams:
            # Parse record
            record = team['record']
            if '-' in record:
                wins, losses = record.split('-')
                wins = int(wins)
                losses = int(losses)
            else:
                wins = 0
                losses = 0

            tabc_data['private'][cls].append({
                'rank': team['rank'],
                'team_name': team['team_name'],
                'wins': wins,
                'losses': losses,
                'record': record
            })

    return tabc_data

def update_rankings_with_tabc():
    """Update rankings.json with December 15 TABC data"""
    # Load TABC December 15 data
    print("Loading TABC December 15, 2025 rankings...")
    tabc_data = load_tabc_dec15_data()

    # Load current rankings
    rankings_file = Path(__file__).parent / 'data' / 'rankings.json'
    with open(rankings_file, 'r') as f:
        current_data = json.load(f)

    print(f"Current data has {len(current_data.get('uil', {}).get('AAAAAA', []))} UIL 6A teams")

    # Update records from TABC
    updated_count = 0

    # Update UIL teams
    for classification in ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']:
        current_teams = current_data['uil'].get(classification, [])
        tabc_teams = tabc_data['uil'].get(classification, [])

        for current_team in current_teams:
            team_name = current_team['team_name']

            # Find matching TABC team
            tabc_team = next((t for t in tabc_teams if t['team_name'] == team_name), None)

            if tabc_team:
                # Update record from TABC
                if current_team.get('wins') != tabc_team['wins'] or current_team.get('losses') != tabc_team['losses']:
                    old_record = f"{current_team.get('wins', 0)}-{current_team.get('losses', 0)}"
                    new_record = f"{tabc_team['wins']}-{tabc_team['losses']}"
                    print(f"  {team_name}: {old_record} → {new_record}")
                    current_team['wins'] = tabc_team['wins']
                    current_team['losses'] = tabc_team['losses']
                    updated_count += 1

    # Update TAPPS teams
    for classification in ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']:
        current_teams = current_data['private'].get(classification, [])
        tabc_teams = tabc_data['private'].get(classification, [])

        for current_team in current_teams:
            team_name = current_team['team_name']

            # Find matching TABC team
            tabc_team = next((t for t in tabc_teams if t['team_name'] == team_name), None)

            if tabc_team:
                # Update record from TABC
                if current_team.get('wins') != tabc_team['wins'] or current_team.get('losses') != tabc_team['losses']:
                    old_record = f"{current_team.get('wins', 0)}-{current_team.get('losses', 0)}"
                    new_record = f"{tabc_team['wins']}-{tabc_team['losses']}"
                    print(f"  {team_name}: {old_record} → {new_record}")
                    current_team['wins'] = tabc_team['wins']
                    current_team['losses'] = tabc_team['losses']
                    updated_count += 1

    # Update timestamp
    current_data['last_updated'] = datetime.now().isoformat()

    # Save updated rankings
    with open(rankings_file, 'w') as f:
        json.dump(current_data, f, indent=2)

    print(f"\n✓ Updated {updated_count} team records with TABC December 15, 2025 data")
    print(f"✓ Rankings saved to {rankings_file}")

    return current_data

if __name__ == '__main__':
    print("="*80)
    print("UPDATING RANKINGS WITH TABC DECEMBER 15, 2025 DATA")
    print("="*80)
    print()

    update_rankings_with_tabc()

    print()
    print("="*80)
    print("UPDATE COMPLETE")
    print("="*80)
