"""
Fill missing data for all ranked teams:
1. Records (W-L) from TABC (priority) or box scores
2. Stats (PPG, Opp PPG) from box scores
3. Districts from UIL data or TABC
"""

import json
from pathlib import Path
from app import db, BoxScore
from sqlalchemy import func
import sys

# File paths
RANKINGS_FILE = Path('data/rankings.json')
WEEKLY_RANKINGS_FILE = Path('data/weekly_rankings_20251222.json')
MASTER_FILE = Path('rankings.json.master')

# Classification mapping
UIL_CLASS_MAP = {
    'AAAAAA': '6A',
    'AAAAA': '5A',
    'AAAA': '4A',
    'AAA': '3A',
    'AA': '2A',
    'A': '1A'
}

def normalize_team_name(name):
    """Normalize team name for matching"""
    return name.lower().strip().replace('.', '').replace("'", '')

def load_data():
    """Load all data files"""
    print("Loading data files...")
    rankings = json.load(open(RANKINGS_FILE))
    weekly = json.load(open(WEEKLY_RANKINGS_FILE))
    return rankings, weekly

def get_tabc_record(team_name, classification, category, weekly_data):
    """Get record from TABC data"""
    tabc_data = weekly_data['tabc']

    if category == 'uil':
        tabc_classification = UIL_CLASS_MAP.get(classification)
        teams = tabc_data['uil'].get(tabc_classification, [])
    else:  # private
        teams = tabc_data['private'].get(classification, [])

    # Find team by name match
    normalized_name = normalize_team_name(team_name)
    for team in teams:
        if normalize_team_name(team['team_name']) == normalized_name:
            return team.get('wins'), team.get('losses')

    return None, None

def get_box_score_stats(team_name, classification):
    """Calculate stats from box scores in database"""
    try:
        # Query box scores for this team
        games = BoxScore.query.filter(
            db.or_(
                BoxScore.team1_name == team_name,
                BoxScore.team2_name == team_name
            )
        ).all()

        if not games:
            return None, None, None, None

        wins = 0
        losses = 0
        total_points = 0
        total_opp_points = 0
        game_count = 0

        for game in games:
            if game.team1_name == team_name:
                team_score = game.team1_score
                opp_score = game.team2_score
            else:
                team_score = game.team2_score
                opp_score = game.team1_score

            if team_score is not None and opp_score is not None:
                total_points += team_score
                total_opp_points += opp_score
                game_count += 1

                if team_score > opp_score:
                    wins += 1
                else:
                    losses += 1

        if game_count > 0:
            ppg = round(total_points / game_count, 1)
            opp_ppg = round(total_opp_points / game_count, 1)
            return wins, losses, ppg, opp_ppg

    except Exception as e:
        print(f"  Error getting box score stats for {team_name}: {e}")

    return None, None, None, None

def fill_ranked_teams_data(rankings, weekly_data):
    """Fill missing data for all ranked teams"""
    print("\n" + "=" * 80)
    print("FILLING MISSING DATA FOR RANKED TEAMS")
    print("=" * 80)

    updates = {
        'records_from_tabc': 0,
        'records_from_boxscores': 0,
        'stats_from_boxscores': 0,
        'districts_filled': 0
    }

    # Process UIL
    print("\nProcessing UIL classifications...")
    for classification in ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']:
        print(f"\n{classification}:")
        teams = rankings['uil'][classification]
        ranked_teams = [t for t in teams if t.get('rank') and t['rank'] <= 25]

        for team in ranked_teams:
            team_name = team['team_name']
            rank = team['rank']

            # 1. Fill record (TABC priority)
            if team.get('wins') is None or team.get('losses') is None or (team.get('wins') == 0 and team.get('losses') == 0):
                # Try TABC first
                tabc_wins, tabc_losses = get_tabc_record(team_name, classification, 'uil', weekly_data)
                if tabc_wins is not None:
                    team['wins'] = tabc_wins
                    team['losses'] = tabc_losses
                    updates['records_from_tabc'] += 1
                    print(f"  #{rank:2d} {team_name:30s} - Record from TABC: {tabc_wins}-{tabc_losses}")
                else:
                    # Try box scores
                    bs_wins, bs_losses, _, _ = get_box_score_stats(team_name, classification)
                    if bs_wins is not None:
                        team['wins'] = bs_wins
                        team['losses'] = bs_losses
                        updates['records_from_boxscores'] += 1
                        print(f"  #{rank:2d} {team_name:30s} - Record from box scores: {bs_wins}-{bs_losses}")

            # 2. Fill stats (box scores only)
            if team.get('ppg') is None or team.get('opp_ppg') is None:
                _, _, ppg, opp_ppg = get_box_score_stats(team_name, classification)
                if ppg is not None:
                    team['ppg'] = ppg
                    team['opp_ppg'] = opp_ppg
                    updates['stats_from_boxscores'] += 1
                    print(f"  #{rank:2d} {team_name:30s} - Stats from box scores: {ppg} PPG, {opp_ppg} Opp PPG")

    # Process TAPPS
    print("\nProcessing TAPPS classifications...")
    for classification in ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']:
        print(f"\n{classification}:")
        teams = rankings['private'].get(classification, [])
        ranked_teams = [t for t in teams if t.get('rank') and t['rank'] <= 10]

        for team in ranked_teams:
            team_name = team['team_name']
            rank = team['rank']

            # 1. Fill record (TABC priority)
            if team.get('wins') is None or team.get('losses') is None or (team.get('wins') == 0 and team.get('losses') == 0):
                # Try TABC first
                tabc_wins, tabc_losses = get_tabc_record(team_name, classification, 'private', weekly_data)
                if tabc_wins is not None:
                    team['wins'] = tabc_wins
                    team['losses'] = tabc_losses
                    updates['records_from_tabc'] += 1
                    print(f"  #{rank:2d} {team_name:30s} - Record from TABC: {tabc_wins}-{tabc_losses}")
                else:
                    # Try box scores
                    bs_wins, bs_losses, _, _ = get_box_score_stats(team_name, classification)
                    if bs_wins is not None:
                        team['wins'] = bs_wins
                        team['losses'] = bs_losses
                        updates['records_from_boxscores'] += 1
                        print(f"  #{rank:2d} {team_name:30s} - Record from box scores: {bs_wins}-{bs_losses}")

            # 2. Fill stats (box scores only)
            if team.get('ppg') is None or team.get('opp_ppg') is None:
                _, _, ppg, opp_ppg = get_box_score_stats(team_name, classification)
                if ppg is not None:
                    team['ppg'] = ppg
                    team['opp_ppg'] = opp_ppg
                    updates['stats_from_boxscores'] += 1
                    print(f"  #{rank:2d} {team_name:30s} - Stats from box scores: {ppg} PPG, {opp_ppg} Opp PPG")

    return rankings, updates

def save_rankings(rankings):
    """Save updated rankings"""
    print("\nSaving updated rankings...")

    # Update timestamp
    from datetime import datetime
    rankings['last_updated'] = datetime.now().isoformat()

    # Save to both files
    with open(RANKINGS_FILE, 'w') as f:
        json.dump(rankings, f, indent=2)

    with open(MASTER_FILE, 'w') as f:
        json.dump(rankings, f, indent=2)

    print(f"✓ Saved to {RANKINGS_FILE}")
    print(f"✓ Saved to {MASTER_FILE}")

def main():
    """Main execution"""
    print("=" * 80)
    print("RANKED TEAMS DATA COMPLETION")
    print("=" * 80)

    # Load data
    rankings, weekly_data = load_data()

    # Initialize Flask app for database access
    from app import app
    with app.app_context():
        # Fill missing data
        rankings, updates = fill_ranked_teams_data(rankings, weekly_data)

        # Save
        save_rankings(rankings)

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Records filled from TABC: {updates['records_from_tabc']}")
        print(f"Records filled from box scores: {updates['records_from_boxscores']}")
        print(f"Stats filled from box scores: {updates['stats_from_boxscores']}")
        print("=" * 80)
        print("✓ Ranked teams data completion finished!")
        print("=" * 80)

if __name__ == '__main__':
    main()
