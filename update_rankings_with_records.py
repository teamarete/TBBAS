"""
Update rankings.json with win-loss records from game data
"""

import json
from app import app
from models import BoxScore
from collections import defaultdict
from datetime import datetime
from school_name_normalizer import SchoolNameNormalizer

def calculate_team_records():
    """Calculate win-loss records from game data"""
    print("Calculating team records from game data...")

    with app.app_context():
        games = BoxScore.query.all()

        team_records = defaultdict(lambda: {
            'wins': 0,
            'losses': 0,
            'games': 0,
            'points_for': 0,
            'points_against': 0
        })

        for game in games:
            # Team 1
            team_records[game.team1_name]['games'] += 1
            team_records[game.team1_name]['points_for'] += game.team1_score
            team_records[game.team1_name]['points_against'] += game.team2_score

            if game.team1_score > game.team2_score:
                team_records[game.team1_name]['wins'] += 1
            else:
                team_records[game.team1_name]['losses'] += 1

            # Team 2
            team_records[game.team2_name]['games'] += 1
            team_records[game.team2_name]['points_for'] += game.team2_score
            team_records[game.team2_name]['points_against'] += game.team1_score

            if game.team2_score > game.team1_score:
                team_records[game.team2_name]['wins'] += 1
            else:
                team_records[game.team2_name]['losses'] += 1

        print(f"Calculated records for {len(team_records)} teams from {len(games)} games")
        return team_records


def update_rankings_with_records():
    """Update rankings.json with actual records"""

    # Load existing rankings
    print("\nLoading rankings.json...")
    with open('data/rankings.json', 'r') as f:
        rankings = json.load(f)

    # Calculate records
    team_records = calculate_team_records()

    # Initialize normalizer for matching team names
    normalizer = SchoolNameNormalizer()

    # Update each ranking entry with records
    updated_count = 0

    for category in ['uil', 'private']:
        if category not in rankings:
            continue

        for classification, teams in rankings[category].items():
            for team in teams:
                team_name = team['team_name']

                # Try to find record (exact match first, then normalized)
                record = team_records.get(team_name)

                if not record:
                    # Try normalized matching
                    canonical_name = normalizer.find_canonical_name([team_name])
                    if canonical_name:
                        record = team_records.get(canonical_name)

                if record:
                    team['wins'] = record['wins']
                    team['losses'] = record['losses']
                    team['games'] = record['games']
                    team['ppg'] = round(record['points_for'] / record['games'], 1) if record['games'] > 0 else 0
                    team['opp_ppg'] = round(record['points_against'] / record['games'], 1) if record['games'] > 0 else 0
                    updated_count += 1

    # Update timestamp
    rankings['last_updated'] = datetime.now().isoformat()
    rankings['records_from_games'] = True
    rankings['games_analyzed'] = len(team_records)

    # Save updated rankings
    print(f"\nUpdated {updated_count} team records")

    with open('data/rankings.json', 'w') as f:
        json.dump(rankings, f, indent=2)

    print("✓ Rankings updated with game records!")
    print(f"  Teams with records: {updated_count}")
    print(f"  Total teams analyzed: {len(team_records)}")

    return rankings


if __name__ == "__main__":
    update_rankings_with_records()
