"""
Fill in missing records, PPG, Opp PPG, and districts for teams
- Records: Use TABC December 15 data (most up to date)
- PPG/Opp PPG: Calculate from database games
- Districts: Look up from UIL data
"""
import json
import sqlite3
from pathlib import Path
from school_abbreviations import get_search_variations

def get_team_stats_from_db(team_name):
    """Get PPG and Opp PPG from database for a team"""
    conn = sqlite3.connect('instance/tbbas.db')
    cursor = conn.cursor()

    variations = get_search_variations(team_name)

    for var in variations:
        cursor.execute('''
            SELECT COUNT(*) as game_count,
                   SUM(CASE WHEN team1_name = ? THEN team1_score ELSE team2_score END) as total_points,
                   SUM(CASE WHEN team1_name = ? THEN team2_score ELSE team1_score END) as total_opp_points
            FROM box_score
            WHERE team1_name = ? OR team2_name = ?
        ''', (var, var, var, var))

        result = cursor.fetchone()
        if result[0] > 0:
            games = result[0]
            ppg = round(result[1] / games, 1) if games > 0 else None
            opp_ppg = round(result[2] / games, 1) if games > 0 else None
            conn.close()
            return {
                'games': games,
                'ppg': ppg,
                'opp_ppg': opp_ppg,
                'db_name': var
            }

    conn.close()
    return None

def load_tabc_records():
    """Load TABC records from December 15 data"""
    tabc_file = Path(__file__).parent / 'data' / 'tabc_rankings_dec15_2025.json'
    with open(tabc_file, 'r') as f:
        data = json.load(f)

    # Create lookup by team name
    records = {}

    # UIL
    for cls_code, teams in data['uil'].items():
        for team in teams:
            name = team['team_name']
            record = team['record']
            if '-' in record:
                wins, losses = record.split('-')
                records[name] = {'wins': int(wins), 'losses': int(losses)}

    return records

def fill_missing_data():
    """Fill in all missing data for teams"""
    # Load current rankings
    rankings_file = Path(__file__).parent / 'data' / 'rankings.json'
    with open(rankings_file, 'r') as f:
        rankings = json.load(f)

    # Load TABC records
    tabc_records = load_tabc_records()

    print("=" * 80)
    print("FILLING MISSING DATA")
    print("=" * 80)

    updates_count = 0

    # Process UIL 6A
    classification = 'AAAAAA'
    teams = rankings['uil'].get(classification, [])

    print(f"\nProcessing UIL 6A ({len(teams)} teams)...")

    for team in teams:
        team_name = team['team_name']
        needs_update = False
        updates = []

        # Check if missing record
        if team.get('wins') is None or team.get('losses') is None:
            # Try TABC first
            if team_name in tabc_records:
                team['wins'] = tabc_records[team_name]['wins']
                team['losses'] = tabc_records[team_name]['losses']
                updates.append(f"record from TABC: {team['wins']}-{team['losses']}")
                needs_update = True

        # Check if missing PPG/Opp PPG
        if team.get('ppg') is None or team.get('ppg') == 0:
            db_stats = get_team_stats_from_db(team_name)
            if db_stats:
                team['ppg'] = db_stats['ppg']
                team['opp_ppg'] = db_stats['opp_ppg']
                updates.append(f"stats from DB ({db_stats['games']} games as '{db_stats['db_name']}'): PPG {db_stats['ppg']}, Opp {db_stats['opp_ppg']}")
                needs_update = True

        # For district, we'd need UIL data - skip for now since we don't have it loaded

        if needs_update:
            print(f"\n  {team_name}:")
            for update in updates:
                print(f"    + {update}")
            updates_count += 1

    # Save updated rankings
    with open(rankings_file, 'w') as f:
        json.dump(rankings, f, indent=2)

    # Also update master file
    master_file = Path(__file__).parent / 'rankings.json.master'
    with open(master_file, 'w') as f:
        json.dump(rankings, f, indent=2)

    print("\n" + "=" * 80)
    print(f"✓ Updated {updates_count} teams with missing data")
    print(f"✓ Saved to {rankings_file}")
    print(f"✓ Updated gold master: {master_file}")
    print("=" * 80)

if __name__ == '__main__':
    fill_missing_data()
